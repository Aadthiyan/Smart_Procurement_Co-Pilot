import streamlit as st
import yaml
import os
import sys
import time
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from backend.db_utils import db_manager
from backend.ai_service import ai_service
from backend.email_service import email_service
from backend.notification_service import notification_service
from backend.session_manager import get_session_manager
from backend.agent_communication import get_communication_bus
from backend.security.rbac import Permission, UserRole
from backend.security.audit_logger import get_audit_logger, AuditEventType
from backend.logger import get_logger

# Initialize logger
logger = get_logger(__name__)
audit_logger = get_audit_logger()

# Load settings
with open('src/config/settings.yaml', 'r') as f:
    config = yaml.safe_load(f)

st.set_page_config(page_title=config['app']['name'], layout="wide", page_icon="🤖")

# Custom CSS for "Premium" feel
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7f9;
    }
    .chat-message {
        padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
    }
    .chat-message.user {
        background-color: #2e7bcf; color: white;
    }
    .chat-message.bot {
        background-color: #ffffff; border: 1px solid #e0e0e0;
    }
    .chat-message .avatar {
      width: 20%;
    }
    .chat-message .message {
      width: 80%;
    }
    .permission-denied {
        background-color: #ffe6e6;
        border-left: 4px solid #ff6666;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title(f"🤖 {config['app']['name']}")

# Initialize session components
session_manager = get_session_manager()
comm_bus = get_communication_bus()

# Initialize session state
if "session_id" not in st.session_state:
    # Create new session
    session = session_manager.create_session(
        user_id=st.session_state.get("user_id", "demo_user"),
        metadata={
            "app": "Smart Procurement CoPilot",
            "version": config['app'].get('version', '1.0'),
            "start_time": datetime.now().isoformat()
        }
    )
    st.session_state.session_id = session.session_id
    logger.info(f"Created new session: {session.session_id}")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Smart Procurement Co-Pilot. I can help you with:\n- **Vendor Onboarding**\n- **Purchase Requisitions**\n- **Status Checks**\n\nHow can I assist you today?"}
    ]

if "user_role" not in st.session_state:
    st.session_state.user_role = "Viewer"

# Sidebar Navigation
st.sidebar.header("Navigation")
st.sidebar.write(f"📊 **Session ID:** `{st.session_state.session_id[:8]}...`")
st.sidebar.write(f"👤 **Role:** {st.session_state.user_role}")

mode = st.sidebar.radio("Choose Mode", ["Chat with Co-Pilot", "Dashboard", "Settings", "Admin"])

# Settings page
if mode == "Settings":
    st.header("Settings")
    st.sidebar.subheader("Preferences")
    
    # User role selection (for demo)
    available_roles = [role.value for role in UserRole]
    st.session_state.user_role = st.selectbox(
        "User Role (for demo)",
        available_roles,
        index=available_roles.index(st.session_state.user_role) if st.session_state.user_role in available_roles else 6
    )
    
    # Session info
    session = session_manager.get_session(st.session_state.session_id)
    if session:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Messages in Session", len(session.conversation_history))
            st.metric("Session Age (minutes)", int((datetime.now() - session.created_at).total_seconds() / 60))
        with col2:
            st.metric("Active Agent", session.current_agent or "None")
            st.metric("Context Keys", len(session.context))
    
    st.divider()
    
    # Audit log preview
    st.subheader("Recent Audit Events")
    try:
        audit_log_path = "logs/audit.log"
        if os.path.exists(audit_log_path):
            with open(audit_log_path, 'r') as f:
                lines = f.readlines()
                recent_events = lines[-5:] if len(lines) > 5 else lines
                for event in reversed(recent_events):
                    st.code(event.strip(), language="json")
        else:
            st.info("No audit log file yet. Events will appear here once generated.")
    except Exception as e:
        st.error(f"Could not read audit log: {str(e)}")

# Admin page
elif mode == "Admin":
    st.header("⚙️ Administration Panel")
    
    # Check permission
    admin_roles = [UserRole.ADMIN.value]
    if st.session_state.user_role not in admin_roles:
        st.markdown("""
        <div class="permission-denied">
            <strong>⛔ Access Denied</strong><br>
            You don't have permission to access this section. Required role: Admin
        </div>
        """, unsafe_allow_html=True)
        
        # Log the failed access attempt
        try:
            audit_logger.log_event(
                event_type=AuditEventType.UNAUTHORIZED_ACCESS_ATTEMPT,
                user_id=st.session_state.user_role,
                resource_type="admin_panel",
                resource_id="admin",
                action="access_attempt",
                details={"user_role": st.session_state.user_role}
            )
        except Exception as e:
            logger.warning(f"Failed to log unauthorized access: {str(e)}")
    else:
        # Admin access granted
        st.success("✅ Admin access granted")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sessions", len(session_manager.sessions))
        with col2:
            st.metric("Active Sessions", sum(1 for s in session_manager.sessions.values() if s))
        with col3:
            st.metric("Pending Messages", len(comm_bus.message_queue) if hasattr(comm_bus, 'message_queue') else 0)
        
        st.divider()
        
        if st.button("🧹 Cleanup Expired Sessions"):
            removed_count = session_manager.cleanup_expired_sessions()
            st.success(f"Cleaned up {removed_count} expired sessions")
            
            # Log cleanup action
            try:
                audit_logger.log_event(
                    event_type=AuditEventType.SESSION_CLEANUP,
                    user_id="admin",
                    resource_type="session",
                    resource_id="all_sessions",
                    action="cleanup",
                    details={"sessions_removed": removed_count}
                )
            except Exception as e:
                logger.warning(f"Failed to log cleanup: {str(e)}")

# Dashboard Mode
elif mode == "Dashboard":
    st.header("Procurement Dashboard")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Sessions", 5, "+2 today")
    with col2:
        st.metric("Pending Approvals", 12, "-3 today")
    with col3:
        st.metric("Vendors Onboarded", 28, "+5 this week")
    
    st.divider()
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Create PO"):
            if st.session_state.user_role in [UserRole.PROCUREMENT_MANAGER.value, UserRole.ADMIN.value]:
                st.success("Redirecting to PO creation...")
                # Log the action
                try:
                    audit_logger.log_event(
                        event_type=AuditEventType.PO_CREATED,
                        user_id=st.session_state.user_role,
                        resource_type="po",
                        resource_id="new_po",
                        action="create",
                        details={"user_role": st.session_state.user_role}
                    )
                except Exception as e:
                    logger.warning(f"Failed to log PO creation: {str(e)}")
            else:
                st.error("❌ You don't have permission to create purchase orders")
                try:
                    audit_logger.log_event(
                        event_type=AuditEventType.UNAUTHORIZED_ACCESS_ATTEMPT,
                        user_id=st.session_state.user_role,
                        resource_type="po",
                        resource_id="new_po",
                        action="create_attempt",
                        details={"user_role": st.session_state.user_role}
                    )
                except Exception as e:
                    logger.warning(f"Failed to log denied access: {str(e)}")
    
    with col2:
        if st.button("👥 Onboard Vendor"):
            if st.session_state.user_role in [UserRole.VENDOR_MANAGER.value, UserRole.ADMIN.value]:
                st.success("Redirecting to vendor onboarding...")
                try:
                    audit_logger.log_event(
                        event_type=AuditEventType.VENDOR_CREATED,
                        user_id=st.session_state.user_role,
                        resource_type="vendor",
                        resource_id="new_vendor",
                        action="create",
                        details={"user_role": st.session_state.user_role}
                    )
                except Exception as e:
                    logger.warning(f"Failed to log vendor creation: {str(e)}")
            else:
                st.error("❌ You don't have permission to onboard vendors")
    
    with col3:
        if st.button("📊 View Analytics"):
            st.info("Analytics would be displayed here")

# Chat Mode
else:  # mode == "Chat with Co-Pilot"
    
    from backend.orchestrator import orchestrator
    
    def process_input(user_input):
        """
        Delegates processing to the Orchestrator with enhanced logging.
        """
        try:
            # Log the incoming message
            try:
                audit_logger.log_event(
                    event_type=AuditEventType.USER_INPUT_RECEIVED,
                    user_id=st.session_state.user_role,
                    resource_type="chat",
                    resource_id=st.session_state.session_id,
                    action="message_received",
                    details={"message_preview": user_input[:50]}
                )
            except Exception as e:
                logger.warning(f"Failed to log user input: {str(e)}")
            
            # Get session and add message
            session = session_manager.get_session(st.session_state.session_id)
            if session:
                session.add_message("user", "user", user_input)
            
            # Process through orchestrator
            result = orchestrator.route_message(user_input)
            response_text = result["response"]
            
            # Add assistant response to session
            if session:
                session.add_message("assistant", "assistant", response_text)
            
            # Log the response
            try:
                audit_logger.log_event(
                    event_type=AuditEventType.ASSISTANT_RESPONSE_SENT,
                    user_id=st.session_state.user_role,
                    resource_type="chat",
                    resource_id=st.session_state.session_id,
                    action="message_sent",
                    details={"message_preview": response_text[:50]}
                )
            except Exception as e:
                logger.warning(f"Failed to log response: {str(e)}")
            
            return response_text
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}", exc_info=True)
            return f"Sorry, I encountered an error processing your request. Please try again."
    
    # Chat Interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Type your request here..."):
        # User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Bot Response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Simulate processing delay
            with st.spinner("Thinking..."):
                time.sleep(0.5)
                response_text = process_input(prompt)
            
            # Typewriter effect
            for chunk in response_text.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"Session: {st.session_state.session_id[:12]}...")
with col2:
    st.caption(f"Mode: {mode}")
with col3:
    st.caption(f"Role: {st.session_state.user_role}")

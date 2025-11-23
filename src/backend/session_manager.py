"""
Agent Session Management
Handles conversation state, timeouts, and persistence
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


class SessionState:
    """Represents a single user conversation session"""
    
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.timeout_minutes = 30
        self.messages = []  # Conversation history
        self.context = {}  # Shared context across agents
        self.current_agent = None  # Which agent is currently handling
        self.is_active = True
        self.metadata = {}  # Additional session data
    
    def is_expired(self) -> bool:
        """Check if session has timed out"""
        elapsed = datetime.utcnow() - self.last_activity
        return elapsed > timedelta(minutes=self.timeout_minutes)
    
    def get_time_until_expiry(self) -> int:
        """Get seconds until session expires"""
        elapsed = (datetime.utcnow() - self.last_activity).total_seconds()
        return max(0, int(self.timeout_minutes * 60 - elapsed))
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def add_message(
        self, 
        agent: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add message to conversation history
        
        Args:
            agent: Agent that generated message
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional additional data
        """
        self.messages.append({
            "agent": agent,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        })
        self.update_activity()
    
    def set_context(self, key: str, value: Any):
        """Store data in session context"""
        self.context[key] = value
        self.update_activity()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Retrieve data from session context"""
        return self.context.get(key, default)
    
    def get_full_context(self) -> Dict[str, Any]:
        """Get entire session context"""
        return self.context.copy()
    
    def set_current_agent(self, agent_name: str):
        """Set which agent is currently handling the session"""
        self.current_agent = agent_name
        self.update_activity()
    
    def get_conversation_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history
        
        Args:
            limit: Number of recent messages to return
        
        Returns:
            List of message dicts
        """
        if limit:
            return self.messages[-limit:]
        return self.messages.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize session to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "timeout_minutes": self.timeout_minutes,
            "is_active": self.is_active,
            "current_agent": self.current_agent,
            "message_count": len(self.messages),
            "context": self.context,
            "metadata": self.metadata
        }


class SessionManager:
    """Centralized session management"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}
        self.archived_sessions = {}  # For audit/compliance
    
    def create_session(self, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> SessionState:
        """
        Create new conversation session
        
        Args:
            user_id: User starting the session
            metadata: Optional session metadata (workflow type, etc.)
        
        Returns:
            Created SessionState
        """
        session_id = str(uuid.uuid4())
        session = SessionState(session_id, user_id)
        
        if metadata:
            session.metadata = metadata
        
        self.sessions[session_id] = session
        logger.info(f"Created session {session_id} for user {user_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """
        Get session by ID
        
        Args:
            session_id: Session identifier
        
        Returns:
            SessionState if valid, None if expired or not found
        """
        session = self.sessions.get(session_id)
        
        if session and session.is_expired():
            logger.warning(f"Session {session_id} expired, archiving")
            self.archive_session(session_id)
            return None
        
        if session:
            session.update_activity()
        
        return session
    
    def end_session(self, session_id: str):
        """
        End and archive session
        
        Args:
            session_id: Session to end
        """
        if session_id in self.sessions:
            session = self.sessions.pop(session_id)
            session.is_active = False
            self.archive_session(session_id)
            logger.info(f"Session {session_id} ended and archived")
    
    def archive_session(self, session_id: str):
        """
        Archive session for audit purposes
        
        Args:
            session_id: Session to archive
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
        elif session_id in self.archived_sessions:
            return  # Already archived
        else:
            return
        
        duration = (datetime.utcnow() - session.created_at).total_seconds() / 60
        
        self.archived_sessions[session_id] = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "ended_at": datetime.utcnow().isoformat(),
            "duration_minutes": duration,
            "message_count": len(session.messages),
            "final_context": session.context.copy(),
            "messages": session.messages
        }
        
        logger.info(f"Session {session_id} archived (duration: {duration:.1f} min)")
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions
        
        Returns:
            Number of sessions cleaned up
        """
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for session_id in expired:
            self.archive_session(session_id)
            del self.sessions[session_id]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
        
        return len(expired)
    
    def get_session_history(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get archived session history for audit
        
        Args:
            session_id: Session ID
        
        Returns:
            Archived session data or None
        """
        return self.archived_sessions.get(session_id)
    
    def get_user_sessions(self, user_id: str) -> List[SessionState]:
        """
        Get all active sessions for a user
        
        Args:
            user_id: User identifier
        
        Returns:
            List of active sessions
        """
        return [
            session for session in self.sessions.values()
            if session.user_id == user_id and session.is_active
        ]
    
    def get_session_count(self) -> Dict[str, int]:
        """Get session statistics"""
        return {
            "active_sessions": len(self.sessions),
            "archived_sessions": len(self.archived_sessions),
            "total_sessions": len(self.sessions) + len(self.archived_sessions)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed session statistics"""
        active_sessions = list(self.sessions.values())
        archived_sessions = list(self.archived_sessions.values())
        
        avg_message_count = 0
        if active_sessions:
            avg_message_count = sum(
                len(s.messages) for s in active_sessions
            ) / len(active_sessions)
        
        return {
            "active_sessions": len(active_sessions),
            "archived_sessions": len(archived_sessions),
            "average_messages_per_session": avg_message_count,
            "oldest_active_session": min(
                (s.created_at.isoformat() for s in active_sessions),
                default=None
            ) if active_sessions else None
        }


# Global session manager instance
_session_manager = None


def get_session_manager() -> SessionManager:
    """Get global session manager instance (singleton)"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

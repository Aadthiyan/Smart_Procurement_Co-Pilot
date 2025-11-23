# Optional REST API server
from flask import Flask, jsonify, request
import sys
import os
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import all components
from backend.security import CredentialProvider, AccessControl, get_audit_logger
from backend.security.rbac import require_permission, Permission
from backend.security.audit_logger import audit_log, AuditEventType
from backend.session_manager import get_session_manager
from backend.agent_communication import get_communication_bus
from backend.watsonx_orchestrate_client import get_watsonx_client
from backend.skill_base import get_skill_registry
from backend.logger import get_logger

app = Flask(__name__)
logger = get_logger(__name__)

# Initialize all components on startup
def initialize_components():
    """Initialize all gap-filling components."""
    try:
        # Initialize security components
        cred_provider = CredentialProvider()
        audit_logger = get_audit_logger()
        
        # Initialize session and communication
        session_mgr = get_session_manager()
        comm_bus = get_communication_bus()
        
        # Initialize orchestration
        watsonx_client = get_watsonx_client()
        skill_registry = get_skill_registry()
        
        logger.info("✅ All components initialized successfully")
        logger.info("  - Secrets Manager: Ready")
        logger.info("  - Audit Logger: Ready")
        logger.info("  - RBAC: Ready")
        logger.info("  - Session Manager: Ready")
        logger.info("  - Agent Communication Bus: Ready")
        logger.info("  - watsonx Client: Ready")
        logger.info("  - Skill Registry: Ready")
        
        return True
    except Exception as e:
        logger.error(f"❌ Component initialization failed: {str(e)}", exc_info=True)
        return False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": "2025-11-23"}), 200

@app.route('/api/init-status', methods=['GET'])
def init_status():
    """Check initialization status of all components."""
    try:
        cred = CredentialProvider()
        audit = get_audit_logger()
        session = get_session_manager()
        comm = get_communication_bus()
        watsonx = get_watsonx_client()
        skills = get_skill_registry()
        
        return jsonify({
            "status": "initialized",
            "components": {
                "security": "ready",
                "audit_logging": "ready",
                "session_management": "ready",
                "agent_communication": "ready",
                "watsonx_orchestration": "ready",
                "skill_framework": "ready"
            }
        }), 200
    except Exception as e:
        logger.error(f"Component check failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Initialize components
    if initialize_components():
        logger.info("Starting Smart Procurement Co-Pilot server...")
        app.run(debug=True, port=5000)
    else:
        logger.error("Failed to initialize components. Exiting.")
        sys.exit(1)

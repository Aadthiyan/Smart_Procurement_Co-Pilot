"""
Agent Communication Protocol
Standardized message format and inter-agent communication
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import uuid
import logging
import time
from threading import Lock

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """Types of inter-agent messages"""
    REQUEST = "request"  # One agent asking another
    RESPONSE = "response"  # Reply from agent
    HANDOFF = "handoff"  # Task handoff
    CALLBACK = "callback"  # Async callback
    ESCALATION = "escalation"  # Escalating to human/manager
    ERROR = "error"  # Error notification


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class AgentMessage(BaseModel):
    """
    Formal message contract between agents
    Ensures all agent communication follows the same format
    """
    
    # Message Identification
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType
    priority: MessagePriority = MessagePriority.NORMAL
    
    # Agent Routing
    from_agent: str
    to_agent: str
    
    # Request/Response Linkage
    request_id: str  # Tracks original request across agents
    in_reply_to: Optional[str] = None  # Response links to request
    
    # Content
    subject: str
    payload: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None  # Shared context data
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # When message/task expires
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentResponse(BaseModel):
    """Response from an agent"""
    
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    in_reply_to: str  # ID of the request message
    from_agent: str
    to_agent: str
    status: str  # "success", "failure", "partial", "timeout"
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentCommunicationBus:
    """
    Central communication bus for inter-agent communication
    Manages message routing, queuing, and callbacks
    """
    
    def __init__(self):
        self.message_queue = {}  # message_id -> AgentMessage
        self.pending_responses = {}  # request_id -> response
        self.callback_registry = {}  # request_id -> callback_function
        self.lock = Lock()  # Thread safety
    
    def send_message(self, message: AgentMessage) -> str:
        """
        Send message from one agent to another
        
        Args:
            message: AgentMessage to send
        
        Returns:
            message_id for tracking
        """
        with self.lock:
            self.message_queue[message.message_id] = message
        
        logger.info(
            f"Message sent from {message.from_agent} to {message.to_agent}: "
            f"{message.subject} (priority: {message.priority})"
        )
        return message.message_id
    
    def send_sync_request(
        self,
        from_agent: str,
        to_agent: str,
        subject: str,
        payload: Dict[str, Any],
        timeout_seconds: int = 30,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> AgentResponse:
        """
        Send synchronous request and wait for response
        
        Args:
            from_agent: Requesting agent
            to_agent: Target agent
            subject: Request subject
            payload: Request data
            timeout_seconds: Max wait time
            priority: Message priority
        
        Returns:
            AgentResponse with result or error
        """
        request_id = str(uuid.uuid4())
        
        # Create and send message
        message = AgentMessage(
            message_type=MessageType.REQUEST,
            from_agent=from_agent,
            to_agent=to_agent,
            request_id=request_id,
            subject=subject,
            payload=payload,
            priority=priority
        )
        
        self.send_message(message)
        
        # Wait for response
        start = time.time()
        while time.time() - start < timeout_seconds:
            with self.lock:
                if request_id in self.pending_responses:
                    return self.pending_responses.pop(request_id)
            time.sleep(0.1)
        
        # Timeout
        logger.warning(
            f"Request {request_id} from {from_agent} to {to_agent} timed out"
        )
        return AgentResponse(
            in_reply_to=message.message_id,
            from_agent=to_agent,
            to_agent=from_agent,
            status="timeout",
            error_code="TIMEOUT",
            error_message=f"No response within {timeout_seconds} seconds"
        )
    
    def send_async_request(
        self,
        from_agent: str,
        to_agent: str,
        subject: str,
        payload: Dict[str, Any],
        callback_function: Optional[Callable] = None,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> str:
        """
        Send asynchronous request with callback
        
        Args:
            from_agent: Requesting agent
            to_agent: Target agent
            subject: Request subject
            payload: Request data
            callback_function: Function to call when response arrives
            priority: Message priority
        
        Returns:
            request_id
        """
        request_id = str(uuid.uuid4())
        
        message = AgentMessage(
            message_type=MessageType.REQUEST,
            from_agent=from_agent,
            to_agent=to_agent,
            request_id=request_id,
            subject=subject,
            payload=payload,
            priority=priority
        )
        
        if callback_function:
            with self.lock:
                self.callback_registry[request_id] = callback_function
        
        self.send_message(message)
        
        logger.info(
            f"Async request {request_id} sent from {from_agent} to {to_agent}"
        )
        return request_id
    
    def handle_response(self, response: AgentResponse):
        """
        Handle response from agent
        
        Args:
            response: AgentResponse from agent
        """
        request_id = response.in_reply_to
        
        callback = None
        with self.lock:
            # Store response for sync waiters
            self.pending_responses[request_id] = response
            
            # Trigger callback if registered (async mode)
            if request_id in self.callback_registry:
                callback = self.callback_registry.pop(request_id)
        
        # Execute callback outside lock
        if callback:
            try:
                callback(response)
                logger.debug(f"Callback executed for request {request_id}")
            except Exception as e:
                logger.error(f"Callback execution failed: {str(e)}")
    
    def handoff_to_agent(
        self,
        current_agent: str,
        target_agent: str,
        context: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> bool:
        """
        Hand off current task to another agent
        
        Args:
            current_agent: Current agent
            target_agent: Target agent for handoff
            context: Task context
            request_id: Optional request ID to link
        
        Returns:
            True if handoff successful
        """
        message = AgentMessage(
            message_type=MessageType.HANDOFF,
            from_agent=current_agent,
            to_agent=target_agent,
            request_id=request_id or str(uuid.uuid4()),
            subject=f"Task handoff from {current_agent}",
            payload=context,
            priority=MessagePriority.HIGH
        )
        
        self.send_message(message)
        logger.info(f"Task handed off from {current_agent} to {target_agent}")
        return True
    
    def escalate_to_human(
        self,
        from_agent: str,
        escalation_type: str,
        context: Dict[str, Any],
        reason: str
    ) -> str:
        """
        Escalate issue to human reviewer
        
        Args:
            from_agent: Agent performing escalation
            escalation_type: Type of escalation (approval_request, manual_review, etc.)
            context: Issue context
            reason: Reason for escalation
        
        Returns:
            escalation_id for tracking
        """
        escalation_id = str(uuid.uuid4())
        
        message = AgentMessage(
            message_type=MessageType.ESCALATION,
            from_agent=from_agent,
            to_agent="human_reviewer",
            request_id=escalation_id,
            subject=f"Escalation: {escalation_type}",
            payload={
                "escalation_type": escalation_type,
                "reason": reason,
                "context": context
            },
            priority=MessagePriority.HIGH
        )
        
        self.send_message(message)
        logger.warning(
            f"Issue escalated from {from_agent}: {escalation_type} - {reason}"
        )
        return escalation_id
    
    def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a message"""
        with self.lock:
            message = self.message_queue.get(message_id)
        
        if message:
            return {
                "message_id": message_id,
                "status": "pending",
                "created_at": message.created_at.isoformat()
            }
        return None
    
    def clear_expired_messages(self, max_age_seconds: int = 3600):
        """Clean up old messages to prevent memory leak"""
        cutoff = datetime.utcnow().timestamp() - max_age_seconds
        
        with self.lock:
            expired_ids = [
                mid for mid, msg in self.message_queue.items()
                if msg.created_at.timestamp() < cutoff
            ]
            for mid in expired_ids:
                del self.message_queue[mid]
        
        if expired_ids:
            logger.debug(f"Cleaned up {len(expired_ids)} expired messages")


# Global communication bus instance
_communication_bus = None


def get_communication_bus() -> AgentCommunicationBus:
    """Get global communication bus instance (singleton)"""
    global _communication_bus
    if _communication_bus is None:
        _communication_bus = AgentCommunicationBus()
    return _communication_bus

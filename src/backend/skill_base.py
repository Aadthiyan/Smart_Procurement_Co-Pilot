"""
Base Skill Class with Formal Input/Output Contracts
All digital skills must inherit from this class and implement formal contracts
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime
import logging
import time
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class SkillStatus(str, Enum):
    """Skill execution status codes"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    ERROR = "error"
    TIMEOUT = "timeout"


class SkillInput(BaseModel):
    """Base class for all skill inputs"""
    skill_name: str
    request_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    execution_context: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 30
    
    class Config:
        use_enum_values = True


class SkillOutput(BaseModel):
    """Formal output contract for all skills"""
    skill_name: str
    status: SkillStatus
    request_id: str
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    execution_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseSkill(ABC):
    """
    Base class for all digital skills with formal contracts
    
    All skills must:
    1. Inherit from this class
    2. Implement validate_input() to validate inputs
    3. Implement _execute_logic() for the actual skill logic
    4. Define input_schema and output_schema
    
    Features:
    - Automatic input/output validation
    - Error handling with fallback strategies
    - Execution timing
    - Request tracking
    - Audit logging
    """
    
    def __init__(self, skill_name: str):
        """
        Initialize the skill
        
        Args:
            skill_name: Name of the skill (e.g., 'validate_vendor')
        """
        self.skill_name = skill_name
        self.logger = logging.getLogger(f"skill.{skill_name}")
        self.timeout_ms = None
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input against skill's input schema
        
        Must be implemented by subclasses to define what inputs are valid
        
        Args:
            input_data: Input data to validate
        
        Returns:
            True if valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement validate_input()")
    
    @abstractmethod
    def _execute_logic(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement actual skill logic
        
        Must be implemented by subclasses
        
        Args:
            input_data: Validated input data
        
        Returns:
            Result dictionary
        """
        raise NotImplementedError("Subclasses must implement _execute_logic()")
    
    def execute(self, input_data: Dict[str, Any]) -> SkillOutput:
        """
        Execute the skill with formal error handling
        
        This method orchestrates:
        1. Input validation
        2. Skill execution
        3. Output validation
        4. Error handling
        5. Timing and logging
        
        Args:
            input_data: Raw input data
        
        Returns:
            SkillOutput with status and result
        """
        import uuid
        start_time = time.time()
        request_id = input_data.get("request_id", str(uuid.uuid4()))
        
        try:
            # Validate input
            if not self.validate_input(input_data):
                self.logger.warning(f"Input validation failed for request {request_id}")
                return SkillOutput(
                    skill_name=self.skill_name,
                    status=SkillStatus.FAILURE,
                    request_id=request_id,
                    error_message="Input validation failed",
                    error_code="INVALID_INPUT",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    metadata={"validation_failed": True}
                )
            
            # Execute skill logic
            result = self._execute_logic(input_data)
            
            execution_time = (time.time() - start_time) * 1000
            
            self.logger.info(
                f"Skill executed successfully: {self.skill_name} "
                f"(request: {request_id}, time: {execution_time:.1f}ms)"
            )
            
            return SkillOutput(
                skill_name=self.skill_name,
                status=SkillStatus.SUCCESS,
                request_id=request_id,
                result=result,
                execution_time_ms=execution_time
            )
            
        except TimeoutError:
            execution_time = (time.time() - start_time) * 1000
            self.logger.error(
                f"Skill execution timeout: {self.skill_name} "
                f"(request: {request_id})"
            )
            return SkillOutput(
                skill_name=self.skill_name,
                status=SkillStatus.TIMEOUT,
                request_id=request_id,
                error_message="Skill execution timeout",
                error_code="TIMEOUT",
                execution_time_ms=execution_time
            )
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self.logger.error(
                f"Skill execution error: {self.skill_name}: {str(e)}",
                exc_info=True
            )
            return SkillOutput(
                skill_name=self.skill_name,
                status=SkillStatus.ERROR,
                request_id=request_id,
                error_message=str(e),
                error_code="EXECUTION_ERROR",
                execution_time_ms=execution_time,
                metadata={"exception_type": type(e).__name__}
            )
    
    def handle_error(
        self, 
        error_code: str, 
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Handle skill-specific errors with fallback strategies
        
        Override in subclasses to implement skill-specific fallback logic
        
        Args:
            error_code: Error code from exception
            context: Error context
        
        Returns:
            Fallback result or None
        """
        return None


class SkillRegistry:
    """Registry for all available skills"""
    
    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {}
    
    def register(self, skill: BaseSkill):
        """Register a skill"""
        self.skills[skill.skill_name] = skill
        logger.info(f"Registered skill: {skill.skill_name}")
    
    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """Get a skill by name"""
        return self.skills.get(skill_name)
    
    def execute_skill(
        self,
        skill_name: str,
        input_data: Dict[str, Any]
    ) -> SkillOutput:
        """
        Execute a registered skill
        
        Args:
            skill_name: Name of the skill to execute
            input_data: Input data for the skill
        
        Returns:
            SkillOutput with result
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return SkillOutput(
                skill_name=skill_name,
                status=SkillStatus.ERROR,
                request_id=input_data.get("request_id", "unknown"),
                error_message=f"Skill not found: {skill_name}",
                error_code="SKILL_NOT_FOUND",
                execution_time_ms=0
            )
        
        return skill.execute(input_data)
    
    def list_skills(self) -> Dict[str, str]:
        """List all registered skills"""
        return {name: skill.skill_name for name, skill in self.skills.items()}


# Global skill registry
_skill_registry = None


def get_skill_registry() -> SkillRegistry:
    """Get global skill registry (singleton)"""
    global _skill_registry
    if _skill_registry is None:
        _skill_registry = SkillRegistry()
    return _skill_registry

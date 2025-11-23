"""
IBM watsonx Orchestrate Integration
Client for orchestrating agents and workflows
"""

import os
import logging
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ExecutionMode(str, Enum):
    """Workflow execution mode"""
    SYNC = "sync"  # Wait for response
    ASYNC = "async"  # Background execution


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class WatsonxOrchestrationClient:
    """
    Client for IBM watsonx Orchestrate Agent Management
    Bridges the agent layer with watsonx.orchestrate platform
    
    Features:
    - Agent orchestration and lifecycle management
    - Workflow execution with conditional routing
    - Digital skill invocation
    - Multi-agent collaboration/handoff
    - Status tracking and monitoring
    """
    
    def __init__(self):
        """Initialize watsonx Orchestrate client"""
        self.api_key = os.getenv("WATSONX_API_KEY", "")
        self.account_id = os.getenv("WATSONX_ACCOUNT_ID", "")
        self.base_url = os.getenv(
            "WATSONX_BASE_URL",
            "https://api.watsonxdata.cloud.ibm.com/v2"
        )
        self.timeout = 30
        
        # Mock mode for testing
        self.use_mock = os.getenv("USE_MOCK_WATSONX", "false").lower() == "true"
        
        if not self.use_mock:
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        else:
            logger.warning("Using mock watsonx - NOT FOR PRODUCTION")
    
    def execute_agent_workflow(
        self,
        agent_id: str,
        workflow_id: str,
        input_data: Dict[str, Any],
        execution_mode: ExecutionMode = ExecutionMode.SYNC
    ) -> Dict[str, Any]:
        """
        Execute a specific workflow in watsonx Orchestrate
        
        Args:
            agent_id: ID of the procurement agent
            workflow_id: ID of the workflow to execute
            input_data: Input parameters for the workflow
            execution_mode: Sync or async execution
        
        Returns:
            Workflow execution result with status and output
        """
        
        if self.use_mock:
            return self._mock_execute_workflow(
                agent_id, workflow_id, input_data
            )
        
        endpoint = f"{self.base_url}/agents/{agent_id}/workflows/{workflow_id}/execute"
        
        payload = {
            "accountId": self.account_id,
            "input": input_data,
            "executionMode": execution_mode.value,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(
                f"Workflow executed: {agent_id}/{workflow_id} "
                f"(executionId: {result.get('executionId')})"
            )
            
            return {
                "status": "success",
                "execution_id": result.get("executionId"),
                "output": result.get("output"),
                "timestamp": result.get("timestamp")
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Workflow timeout: {agent_id}/{workflow_id}")
            return {
                "status": "timeout",
                "error_message": "Workflow execution timed out",
                "timestamp": datetime.utcnow().isoformat()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_workflow_status(
        self,
        agent_id: str,
        execution_id: str
    ) -> Dict[str, Any]:
        """
        Get status of a workflow execution
        
        Args:
            agent_id: ID of the agent
            execution_id: ID of the execution
        
        Returns:
            Current status and progress
        """
        
        if self.use_mock:
            return {
                "status": "success",
                "execution_id": execution_id,
                "progress": 100,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        endpoint = f"{self.base_url}/agents/{agent_id}/executions/{execution_id}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def invoke_skill(
        self,
        skill_name: str,
        skill_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke a digital skill within watsonx Orchestrate
        
        Args:
            skill_name: Name of the skill (e.g., 'validate_vendor')
            skill_input: Input data for the skill
        
        Returns:
            Skill execution result
        """
        
        if self.use_mock:
            return self._mock_invoke_skill(skill_name, skill_input)
        
        endpoint = f"{self.base_url}/skills/{skill_name}/invoke"
        
        payload = {
            "accountId": self.account_id,
            "input": skill_input,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            logger.info(f"Skill invoked: {skill_name}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Skill invocation failed: {skill_name}: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e),
                "skill_name": skill_name
            }
    
    def route_to_agent(
        self,
        target_agent: str,
        context: Dict[str, Any],
        current_agent: str = "primary"
    ) -> Dict[str, Any]:
        """
        Route a request to another agent (multi-agent collaboration)
        
        Args:
            target_agent: Name of the target agent
            context: Context data to pass to the agent
            current_agent: Current agent initiating the handoff
        
        Returns:
            Routing result with agent response
        """
        
        if self.use_mock:
            return {
                "status": "success",
                "target_agent": target_agent,
                "handoff_id": "hoff-123456",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        endpoint = f"{self.base_url}/agents/{target_agent}/route"
        
        payload = {
            "accountId": self.account_id,
            "fromAgent": current_agent,
            "context": context,
            "handoffMode": "seamless",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            logger.info(
                f"Handoff from {current_agent} to {target_agent} successful"
            )
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Agent handoff failed: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e),
                "target_agent": target_agent
            }
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents
        
        Returns:
            List of agent details
        """
        
        if self.use_mock:
            return [
                {
                    "agent_id": "vendor_agent",
                    "name": "Vendor Onboarding Agent",
                    "status": "active"
                },
                {
                    "agent_id": "requisition_agent",
                    "name": "Requisition Agent",
                    "status": "active"
                },
                {
                    "agent_id": "compliance_agent",
                    "name": "Compliance Agent",
                    "status": "active"
                },
                {
                    "agent_id": "approval_agent",
                    "name": "Approval Agent",
                    "status": "active"
                },
                {
                    "agent_id": "communication_agent",
                    "name": "Communication Agent",
                    "status": "active"
                }
            ]
        
        endpoint = f"{self.base_url}/agents"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("agents", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list agents: {str(e)}")
            return []
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        
        if self.use_mock:
            return {
                "agent_id": agent_id,
                "status": "active",
                "last_activity": datetime.utcnow().isoformat(),
                "execution_count": 42
            }
        
        endpoint = f"{self.base_url}/agents/{agent_id}/status"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get agent status: {str(e)}")
            return {"status": "error", "agent_id": agent_id}
    
    # Mock methods for development/testing
    
    def _mock_execute_workflow(
        self,
        agent_id: str,
        workflow_id: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock workflow execution for testing"""
        logger.debug(f"Mock: Executing workflow {workflow_id} in {agent_id}")
        return {
            "status": "success",
            "execution_id": f"exec-{agent_id}-{workflow_id}",
            "output": {
                "result": "Mock execution successful",
                "input_received": input_data
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _mock_invoke_skill(
        self,
        skill_name: str,
        skill_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock skill invocation for testing"""
        logger.debug(f"Mock: Invoking skill {skill_name}")
        return {
            "status": "success",
            "skill_name": skill_name,
            "result": {
                "mock": True,
                "input_received": skill_input
            },
            "timestamp": datetime.utcnow().isoformat()
        }


# Global client instance
_watsonx_client = None


def get_watsonx_client() -> WatsonxOrchestrationClient:
    """Get global watsonx client instance (singleton)"""
    global _watsonx_client
    if _watsonx_client is None:
        _watsonx_client = WatsonxOrchestrationClient()
    return _watsonx_client

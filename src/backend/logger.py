import logging
import os
import json
from datetime import datetime

class Logger:
    def __init__(self):
        self.log_dir = "logs"
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # Configure logging
        logging.basicConfig(
            filename=os.path.join(self.log_dir, 'workflow_execution.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("ProcurementCoPilot")

    def log_step(self, workflow_id, step_name, status, details=None):
        """
        Logs a specific step in a workflow.
        """
        log_entry = {
            "workflow_id": workflow_id,
            "step": step_name,
            "status": status,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(json.dumps(log_entry))
        print(f"[LOG] {step_name}: {status}")

    def log_error(self, workflow_id, error_msg):
        self.logger.error(f"Workflow {workflow_id} Failed: {error_msg}")

workflow_logger = Logger()

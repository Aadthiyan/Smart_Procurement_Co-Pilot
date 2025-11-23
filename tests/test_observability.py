import sys
import os
import time
sys.path.append(os.path.join(os.getcwd(), 'src'))

from backend.logger import workflow_logger
from backend.monitor import metrics_collector

def test_observability():
    print("\n=== Testing Logging ===")
    workflow_id = "WF-TEST-001"
    workflow_logger.log_step(workflow_id, "Start", "Running")
    workflow_logger.log_step(workflow_id, "VendorCheck", "Success", {"vendor": "Acme"})
    workflow_logger.log_step(workflow_id, "End", "Completed")
    
    print("\n=== Testing Monitoring ===")
    start_time = time.time()
    time.sleep(0.1) # Simulate work
    duration = (time.time() - start_time) * 1000
    
    metrics_collector.record_workflow_completion(success=True, duration_ms=duration)
    
    metrics = metrics_collector.get_metrics()
    print(f"Current Metrics: {metrics}")
    
    assert metrics["total_requests"] > 0
    print("Observability tests passed.")

if __name__ == "__main__":
    test_observability()

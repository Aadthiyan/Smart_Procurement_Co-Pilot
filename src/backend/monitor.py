import time
import json
import os

class MetricsCollector:
    def __init__(self):
        self.metrics_file = "logs/metrics.json"
        self._init_metrics()

    def _init_metrics(self):
        if not os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'w') as f:
                json.dump({
                    "total_requests": 0,
                    "successful_workflows": 0,
                    "failed_workflows": 0,
                    "avg_response_time": 0,
                    "response_times": []
                }, f)

    def _read_metrics(self):
        with open(self.metrics_file, 'r') as f:
            return json.load(f)

    def _write_metrics(self, data):
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)

    def record_workflow_completion(self, success, duration_ms):
        data = self._read_metrics()
        data["total_requests"] += 1
        if success:
            data["successful_workflows"] += 1
        else:
            data["failed_workflows"] += 1
            
        data["response_times"].append(duration_ms)
        data["avg_response_time"] = sum(data["response_times"]) / len(data["response_times"])
        
        self._write_metrics(data)

    def get_metrics(self):
        return self._read_metrics()

metrics_collector = MetricsCollector()

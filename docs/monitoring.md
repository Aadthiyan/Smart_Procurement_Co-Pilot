# Monitoring & Observability

## Overview
The system uses a file-based logging and metrics approach suitable for the hackathon prototype.

## Logging
*   **File**: `logs/workflow_execution.log`
*   **Format**: JSON-structured log lines.
*   **Content**: Captures every step of the workflow (Start, Agent Action, End) with timestamps and status.

## Monitoring
*   **Metrics**: Stored in `logs/metrics.json`.
*   **Key Indicators**:
    *   Total Requests Processed
    *   Success/Failure Rate
    *   Average Response Time

## Dashboard
The metrics are visualized in the **Dashboard** tab of the Streamlit application (`src/frontend/app.py`).

## Access
*   Logs can be viewed directly in the `logs/` directory.
*   Metrics are exposed via the `metrics_collector.get_metrics()` API.

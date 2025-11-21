# Smart Procurement Co-Pilot

## Project Overview
A conversational AI interface for procurement, integrating with IBM Cloud and orchestrating various agents for vendor onboarding, requisition, compliance, and approval.

## Architecture
The system is built on a multi-agent architecture where specialized agents handle different aspects of the procurement lifecycle.

### Agents
1.  **Vendor Onboarding Agent**: Manages new vendor registration and validation.
2.  **Requisition Agent**: Helps users create purchase requests.
3.  **Compliance Agent**: Checks requests against company policies.
4.  **Approval Agent**: Routes requests for necessary approvals.
5.  **Communication Agent**: Handles notifications and updates.

### Diagrams
Please refer to the [Architecture Document](docs/architecture.md) for detailed Mermaid.js diagrams of the system architecture and data flow.
Please refer to the [Workflow Document](docs/workflow.md) for detailed process flowcharts.

## Progress Update - Day 1
We have successfully established the foundation of the Smart Procurement Co-Pilot.

### Accomplishments
- [x] **Project Structure**: Set up the complete file system, including `orchestrate`, `src`, and `docs` directories.
- [x] **Agent Architecture**: Defined roles, responsibilities, and prompts for 5 core agents.
- [x] **Digital Skills**: Implemented Python scripts for 6 key skills (contract extraction, validation, budget check, etc.).
- [x] **Workflow Design**: Designed and simulated 2 end-to-end workflows (Supplier Onboarding & Purchase Request) with conditional routing.
- [x] **Documentation**: Created comprehensive architecture, workflow, and skills documentation.
- [x] **Testing**: Verified agent logic and workflow orchestration via simulation scripts.

## Setup
1.  Clone the repository.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Configure environment variables in `src/config/cloud.env`.
4.  Run the simulation tests:
    - Agents: `python tests/simulate_agents.py`
    - Workflows: `python tests/simulate_workflows.py`
5.  Run the application (Frontend pending): `streamlit run src/frontend/app.py`

## Usage
Start the application and select the desired agent or mode from the sidebar. Use the chat interface to initiate requests like "I want to onboard a new vendor" or "I need to buy office supplies".

## Credits
[Team Members]

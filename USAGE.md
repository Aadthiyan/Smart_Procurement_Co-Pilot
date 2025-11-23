# User Guide

Welcome to the **Smart Procurement Co-Pilot**! This guide will help you navigate the system, interact with agents, and perform common procurement tasks.

---

## 🚀 Getting Started

### 1. Launch the Application
Follow the installation instructions in the [README](README.md). Once running, open your browser to:
`http://localhost:8501`

### 2. Navigation
The sidebar provides access to different modes:
*   **Chat with Co-Pilot**: The main interface for talking to agents.
*   **Dashboard**: A visual overview of requests, vendors, and budget.
*   **Settings**: Configure your user role (for demo purposes) and view session info.
*   **Admin**: (Admin only) System management and logs.

---

## 🤖 Interacting with Agents

The Co-Pilot uses natural language. You don't need to memorize commands—just talk to it!

### Scenario 1: Onboarding a New Vendor
**Goal**: Register a new supplier in the system.

1.  **Select Role**: Go to **Settings** and select **Vendor Manager**.
2.  **Go to Chat**: Switch back to "Chat with Co-Pilot".
3.  **Type**: "I want to onboard a new vendor."
4.  **Follow Prompts**:
    *   Agent: "Please provide the Vendor Name."
    *   You: "Quantum Systems Inc."
    *   Agent: "What is their Tax ID?"
    *   You: "99-8877665"
    *   Agent: "Industry?"
    *   You: "Technology Hardware"
5.  **Result**: The **Vendor Agent** will validate the Tax ID and Industry. If compliant, it will auto-approve and give you a Vendor ID.

### Scenario 2: Creating a Purchase Request
**Goal**: Buy office equipment.

1.  **Select Role**: Select **Employee** or **Procurement Manager**.
2.  **Type**: "I need to buy 5 ergonomic chairs."
3.  **Agent Response**: The **Requisition Agent** will check your department's budget.
4.  **Interaction**:
    *   Agent: "I found 'Herman Miller Aeron' for $1,200 each. Total: $6,000. Shall I proceed?"
    *   You: "Yes, please."
5.  **Result**:
    *   If under $5,000: Auto-approved.
    *   If over $5,000: Routed for approval. You'll get a Request ID (e.g., `REQ-101`).

### Scenario 3: Checking Status
**Goal**: See where your request is.

1.  **Type**: "Check status of REQ-101."
2.  **Result**: The **Approval Agent** will tell you: "Pending approval from Finance Director."

---

## 📊 Using the Dashboard

Switch to the **Dashboard** tab to see real-time metrics:
*   **Active Sessions**: Number of users currently using the system.
*   **Pending Approvals**: Requests waiting for sign-off.
*   **Vendors Onboarded**: Total count of approved vendors.
*   **Quick Actions**: Buttons to jump-start common tasks (Create PO, Onboard Vendor).

---

## ⚙️ Settings & Roles

For the hackathon demo, you can switch roles instantly to test different permissions:

| Role | Permissions |
|------|-------------|
| **Viewer** | Read-only access. |
| **Employee** | Can create requests, check status. |
| **Vendor Manager** | Can onboard vendors. |
| **Procurement Manager** | Can approve requests < $50k. |
| **CFO** | Can approve requests > $50k. |
| **Admin** | Full system access. |

---

## ❓ Troubleshooting

**"I don't get a response."**
*   Check the terminal where you ran `python src/backend/server.py`. Is it running?
*   Ensure `streamlit` is running in a separate terminal.

**"Permission Denied"**
*   Check your Role in **Settings**. You might be a "Viewer". Switch to "Admin" or "Manager".

**"Database Error"**
*   The system uses a local fallback (`local_db.json`) if IBM Cloudant is not configured. Ensure this file exists or the backend has write permissions to create it.

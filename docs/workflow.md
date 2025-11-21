# Procurement Workflows

## Overall Workflow

The procurement process is divided into distinct stages managed by specific agents.

```mermaid
flowchart LR
    Start((Start)) --> Intent{Identify Intent}
    Intent -- "New Vendor" --> Onboarding
    Intent -- "Buy Item" --> Requisition
    
    subgraph Onboarding [Vendor Onboarding]
        V1[Collect Info] --> V2[Validate Docs]
        V2 --> V3[Sanctions Check]
        V3 --> V4[Create Vendor]
    end

    subgraph Requisition [Requisition Process]
        R1[Gather Requirements] --> R2[Check Budget]
        R2 --> R3[Create PR]
    end

    Onboarding --> End((End))
    Requisition --> Compliance

    subgraph Compliance [Compliance Check]
        C1[Policy Review] --> C2{Compliant?}
        C2 -- No --> Reject[Reject/Revise]
        C2 -- Yes --> Approval
    end

    subgraph Approval [Approval Process]
        A1[Route to Manager] --> A2{Approved?}
        A2 -- No --> Reject
        A2 -- Yes --> Finalize[Finalize PO]
    end

    Finalize --> Notify[Communication Agent]
    Reject --> Notify
    Notify --> End
```

## Agent Interaction Patterns

*   **Handoffs**: Agents return control to the Orchestrator after completing their sub-task. The Orchestrator then invokes the next agent.
*   **Shared State**: All agents read from and write to a shared database/context to maintain continuity.
*   **Asynchronous Notifications**: The Communication Agent operates asynchronously to avoid blocking the main workflow.

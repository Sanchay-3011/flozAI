# FlozAI Architectural Design Document

This document explains the internal mechanisms, data flows, and design choices of the FlozAI system.

---

## 1. Multi-Step Intent Parsing Pipeline

To handle natural language request translation efficiently under Groq's 6,000 TPM limits, FlozAI implements a **Two-Call Token-Saving Strategy** inside [intent_parser.py](file:///c:/Users/roysa/OneDrive/Desktop/flozAI%20db/flozAI/src/flozai/core/intent_parser.py):

```
                       ┌──────────────────────┐
                       │  User Input Prompt   │
                       └──────────┬───────────┘
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │     Call 1: Intent Classifier (~300 tokens)   │
           │  Determine if request is CLEAR, INCOMPLETE,  │
           │  or OUT OF SCOPE.                            │
           └──────────────────────┬───────────────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
       [ NEEDS CLARIFICATION ]                 [ CLEAR ]
                  │                               │
                  ▼                               ▼
       Short-circuit parser              ┌──────────────────┐
       and prompt for details            │  Call 2: Parser  │
                                         │  (Full schema)   │
                                         └────────┬─────────┘
                                                  │
                                                  ▼
                                         Structured JSON Intent
```

* **Call 1 (Classifier):** Skips loading the 1,500-character capabilities registry and output specifications. It simply asks the LLM to classify the status. If the request is out of scope or incomplete, it short-circuits immediately.
* **Call 2 (Full Parser):** Runs only when the classification is `CLEAR`. It loads the capability configuration, maps it, and outputs the exact JSON payload defining the triggers and actions.

---

## 2. Multi-Tenant Database & Security Model

FlozAI leverages **PostgreSQL Row-Level Security (RLS)** in Supabase to guarantee that users can only view or modify their own data.

```sql
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own workflows"
  ON workflows FOR SELECT
  USING (auth.uid() = user_id);
```

### Table Relations
* **`users`:** Synced directly from Supabase Auth (`auth.users`).
* **`workflows`:** Belongs to `user_id`. Includes JSONB columns for `nodes`, `edges`, and `steps` to preserve the visual state of the React Flow canvas.
* **`tasks`:** Individual steps mapping to a parent `workflow_id`.
* **`logs`:** Execution history entries mapping to `workflow_id`.
* **`integrations`:** API credentials (API keys, OAuth tokens) stored securely for a user.

---

## 3. Visual Node Auto-Layout (Dagre)

When a workflow is generated from text, the frontend receives a flat list of `steps`. In [WorkflowCanvas.jsx](file:///c:/Users/roysa/OneDrive/Desktop/flozAI%20db/flozAI/frontend/src/components/app/WorkflowCanvas.jsx), FlozAI uses **Dagre** (`dagre`) to construct a layout graph:

1. Creates nodes for triggers, merges, and actions.
2. Configures default width (`260px`) and height (`160px`) for cards.
3. Automatically computes coordinate paths using Left-to-Right (`LR`) rank ordering.
4. Feeds coordinates into `@xyflow/react` to construct the visually positioned canvas.

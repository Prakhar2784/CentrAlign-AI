# CentrAlign AI — Autonomous Task Worker: Technical Interview Demo Script

**Target Duration**: 3 to 5 minutes  
**Goal**: Clearly demonstrate real autonomous tool selection, failure recovery, database persistence, and independent verification.

---

## 1. Introduction & Context (30 seconds)

> *"Hi! Today I'm demonstrating an Autonomous AI Task Worker built for automated invoice processing and enterprise finance synchronization.*  
> *Rather than building a simple chatbot or a hardcoded script, this system uses a true ReAct agent loop. It receives high-level natural language instructions, reasons over available tools, extracts structured data from multi-document candidate sets, persists changes to an internal database, and strictly verifies state before reporting success."*

---

## 2. Architecture Quick Tour (45 seconds)

> *"The system is structured into four main layers:*  
> 1. **React / Vite Frontend**: Displays real-time SSE execution logs, plan progression, verification badges, and live database tables.  
> 2. **FastAPI Backend**: Hosts the Agent Orchestrator, REST endpoints, and SSE event streaming.  
> 3. **Agent Core & Tool Registry**: Includes a pluggable LLM provider (Gemini 2.5 Flash with fallback ReAct Reasoner), an explicit short-term memory scratchpad, a Safety Guard for write authorization, and individual atomic tools (`search_invoices`, `get_invoice`, `extract_invoice_data`, `search_finance_records`, `update_invoice_record`, `verify_invoice_record`).  
> 4. **Simulated Company Environment**: Independent SQLite databases for the simulated Document Portal and the Internal Finance Ledger."*

---

## 3. Live Walkthrough — 4 Evaluation Scenarios (2.5 minutes)

### Scenario 1: Standard Autonomous Execution (Acme Corp)
1. In the UI, click **"1. Standard Execution"** or type:  
   `"Find the latest invoice from Acme Corp, extract the amount and due date, update the invoice record in the finance system, and tell me when it is done."`
2. Click **"Run Task Autonomously"**.
3. **Point out in the UI**:
   - **Plan Progression**: The 6-step plan updates dynamically from *Pending* to *In Progress* to *Completed*.
   - **Chronological Reasoning**: Acme Corp has 3 invoices (`INV-1001`, `INV-1002`, `INV-1003`). The agent autonomously sorts by issue date and identifies `INV-1003` ($48,000.00, due 2026-10-15) as the latest.
   - **Database Persistence**: Look at the *Internal Finance System* table below; record `INV-1003` updates from `$0.00 (Unset)` to `$48,000.00` with status `SYNCED`.
   - **Verification Gate**: The green badge confirms that the agent read back the database record before declaring success.

---

### Scenario 2: Self-Healing Failure Recovery (Simulated DB Lock)
1. In the UI, click **"2. Transient Lock & Retry"** (this enables `Simulate DB Lock on 1st Update`).
2. Click **"Run Task Autonomously"**.
3. **Point out in the UI**:
   - Step 5 (`update_invoice_record`) fails on attempt #1 with error:  
     `FINANCE_DB_LOCK_TIMEOUT: Ledger lock collision on financial periods table.`
   - **Agent Adaptation**: Look at the Agent Thought in the logs: the agent observes that the error is retryable, increments the retry counter, re-attempts the update on Step 6, and succeeds.
   - The task completes with verified database state.

---

### Scenario 3: Verification Discrepancy & Safety Rejection
1. In the UI, click **"3. Verification Failure"** (this enables `Simulate Verification Mismatch`).
2. Click **"Run Task Autonomously"**.
3. **Point out in the UI**:
   - The agent executes the update, but when calling `verify_invoice_record`, a checksum discrepancy is detected.
   - **Crucial Behavior**: The agent does **NOT** falsely report success. It halts execution, sets status to `FAILED`, and displays the exact discrepancy details to the operator.

---

### Scenario 4: Multi-Vendor Generalization (Globex)
1. In the UI, click **"4. Multi-Vendor Generalization"** (`Globex`).
2. Click **"Run Task Autonomously"**.
3. **Point out in the UI**:
   - The agent searches for Globex, discovers `INV-2001` and `INV-2002`, selects the latest (`INV-2002`, $64,000.00, due 2026-09-15), updates the finance ledger, and verifies it.
   - Proves zero hardcoding for Acme Corp.

---

## 4. Summary & Limitations (30 seconds)

> *"In summary, the system satisfies all interview requirements:*  
> - *Every tool is atomic and selected dynamically by the reasoner.*  
> - *Short-term memory and safety checks prevent unauthorized modifications.*  
> - *The verifier guarantees database integrity.*  
> *Known limitations: The system currently operates over structured/text invoice data rather than raw OCR/PDF scans, and operates within a local simulated company environment.*  
> *I'm happy to dive into any specific module or live test in pytest!"*

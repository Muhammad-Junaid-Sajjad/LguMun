# WORKFLOWS

## WORKFLOW-001: Registration Flow
**Created**: 2026-04-19T09:52:22Z  
**Status**: Not Configured  
**Purpose**: Handle delegate registration end-to-end

### Steps
1. User visits homepage
2. User clicks "Register" button
3. User fills registration form
4. Client-side validation runs
5. Server-side validation runs
6. Duplicate check (email, student ID)
7. Committee capacity check
8. Transaction with SELECT FOR UPDATE
9. Roll number generation
10. Success screen displayed

### Agents Involved
- Validator Agent: Test registration flow

---

## WORKFLOW-002: Approval Workflow
**Created**: 2026-04-19T09:52:22Z  
**Status**: Not Configured  
**Purpose**: Handle approval requests

### Steps
1. User submits approval request
2. Request added to `approvals/pending/`
3. User reviews request
4. User approves or rejects
5. If approved: Move to `approvals/approved/`
6. If rejected: Move to `approvals/rejected/`
7. When executed: Move to `approvals/executed/`
8. When archived: Move to `approvals/history/`

### Agents Involved
- None (human-driven)

---

## WORKFLOW-003: Continuous Improvement Loop
**Created**: 2026-04-19T09:52:22Z  
**Status**: Not Configured  
**Purpose**: Enable Claude to learn from actions

### Steps
1. Execute action
2. Log result
3. Analyze outcome
4. Extract lesson (if any)
5. Update `learning/` files
6. Apply learning to next action

### Agents Involved
- All agents contribute to learning

---

## WORKFLOW-004: Error Recovery Workflow
**Created**: 2026-04-19T09:52:22Z  
**Status**: Not Configured  
**Purpose**: Handle errors systematically

### Steps
1. Stop immediately
2. Log error in `errors.md`
3. Analyze root cause
4. Propose fix
5. Wait for approval if critical
6. Apply fix
7. Re-verify system integrity

### Agents Involved
- Reviewer Agent: Review fix
- Validator Agent: Verify fix

---

## WORKFLOW-005: Agent Activation Workflow
**Created**: 2026-04-19T09:52:22Z  
**Status**: Not Configured  
**Purpose**: Activate agents for specific tasks

### Steps
1. Determine required agent(s)
2. Check agent configuration
3. Configure subagents if needed
4. Execute agent task
5. Log results
6. Extract lessons

### Agents Involved
- Architect, Reviewer, Validator

---

## WORKFLOW-006: Phase Transition Workflow
**Created**: 2026-04-19T09:52:22Z  
**Status**: Not Configured  
**Purpose**: Move between project phases

### Steps
1. Complete all tasks in current phase
2. Update `core/phases.md`
3. Update `core/state.md`
4. Update `reports/progress.md`
5. Update `reports/health.md`
6. Update `CHANGELOG.md`
7. Move to next phase

### Agents Involved
- Architect: Plan next phase
- Reviewer: Validate phase completion
- Validator: Test phase deliverables

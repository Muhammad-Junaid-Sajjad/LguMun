# LESSONS LEARNED

## LESSON-001: Tool Requirements Must Be Respected
**Date**: 2026-04-19T09:45:00Z  
**Source**: MISTAKE-001

### Context
When working with existing files, the Write tool requires a prior Read tool call.

### Key Insight
Each tool has specific requirements that must be met before use. Ignoring these constraints causes errors and delays.

### Best Practice
- Always Read before Write for existing files
- Check tool requirements before execution
- Build validation into workflow

### Application
Apply this to all file operations:
1. Read file to verify existence and content
2. Write file with required changes
3. Verify write succeeded

---

## LESSON-002: Structured State Management Prevents Confusion
**Date**: 2026-04-19T09:44:48Z  
**Source**: Project initialization

### Context
Without structured state management, project information becomes scattered and hard to track.

### Key Insight
Centralized state tracking provides:
- Single source of truth
- Complete audit trail
- Clear visibility into project status
- Easy onboarding for new contributors

### Best Practice
- Use `/project-state-management/` as central hub
- Document everything in structured files
- Update state after every meaningful action
- Use YAML frontmatter for metadata

### Application
Apply to all future projects:
1. Initialize state management first
2. Document all decisions
3. Track all tasks
4. Log all actions

---

## LESSON-003: State Transitions Require Clear Workflow
**Date**: 2026-04-19T09:40:00Z  
**Source**: Approval workflow design

### Context
Approvals need to move through clear states: pending → approved → executed → history

### Key Insight
- File movement + YAML metadata = automatic audit trail
- Git tracks everything automatically
- Easy to query by status

### Best Practice
- Use subfolders for each state
- Include status in YAML frontmatter
- Move files between folders on state change
- Archive completed items

### Application
Apply to all approval workflows:
1. Create pending folder for new items
2. Move to approved when approved
3. Move to executed when implemented
4. Archive to history for long-term storage

---

## LESSON-004: Agent Specialization Improves Quality
**Date**: 2026-04-19T09:40:00Z  
**Source**: Agent architecture design

### Context
Specialized agents (Architect, Reviewer, Validator) with subagents produce better results than general-purpose agents.

### Key Insight
- Division of labor enables focused expertise
- Multi-perspective review catches more issues
- Continuous improvement loop works better with specialization

### Best Practice
- Create agents for specific responsibilities
- Use subagents for specialized tasks
- Max 2-level depth (agent → subagent)
- Log all agent actions

### Application
Apply to all agent workflows:
1. Define agent responsibilities clearly
2. Create specialized subagents
3. Log all agent decisions
4. Extract lessons from agent actions

---

## LESSON-005: Continuous Self-Improvement Is Possible
**Date**: 2026-04-19T09:40:00Z  
**Source**: Self-improvement loop design

### Context
Claude can learn from its own responses and improve over time.

### Key Insight
- Every action → Log → Analyze → Extract lesson → Apply
- Mistakes database enables pattern recognition
- Anti-patterns prevent regression

### Best Practice
- Log all errors and near-misses
- Extract lessons from patterns
- Update anti-patterns regularly
- Apply learning to future actions

### Application
Apply to all future interactions:
1. Log any error or issue
2. Analyze root cause
3. Update learning files
4. Apply to next action

---

## LESSON-006: Verify Systems Actually Work, Don't Just Claim They Do
**Date**: 2026-04-21T07:48:44Z  
**Source**: MISTAKE-002

### Context
Auto-mode system was "activated" but never actually tracked or updated files.

### Key Insight
Creating configuration files and documentation doesn't make a system functional. A system is only "active" if it's actually executing and producing results. Claiming something works without verification leads to broken systems and lost visibility.

### Best Practice
- After "activating" a system, verify it's actually working
- Check that files are being updated as claimed
- Don't confuse declarative (config) with functional (running code)
- Be honest: if it doesn't work, call it "planned" not "active"

### Application
Apply to all system activations:
1. Activate the system
2. Verify it's actually working (check outputs)
3. If not working, fix it or document as "planned"
4. Never claim a system is "active" without proof

# ARCHITECTURAL DECISIONS

## DECISION-001: Single-Service Architecture
**Date**: 2026-04-19  
**Status**: Approved  
**Executed**: Yes  
**Context**: Backend and frontend served by one FastAPI service  
**Rationale**: Minimizes deployment complexity on free-tier hosting (Render.com)  
**Alternatives Considered**: Microservices, separate frontend server  
**Trade-offs**: Simplicity vs. scalability (acceptable for Phase 0)  
**Impact**: Zero inter-service communication failures, single GitHub push deployment  

---

## DECISION-002: Flat File Structure
**Date**: 2026-04-19  
**Status**: Approved  
**Executed**: Yes  
**Context**: All backend code in `app/*.py` with no subdirectories  
**Rationale**: Simplicity over abstraction - 7 backend files, instant navigation  
**Alternatives Considered**: Nested modules, organized by feature  
**Trade-offs**: Minimal overhead vs. potential reorganization needs later  
**Impact**: No mental overhead for file location, rapid development  

---

## DECISION-003: Zero Build Frontend
**Date**: 2026-04-19  
**Status**: Approved  
**Executed**: Yes  
**Context**: Vanilla HTML/CSS/JS only, no npm/webpack  
**Rationale**: Eliminates build tools complexity and failure points  
**Alternatives Considered**: React/Vue with build pipeline  
**Trade-offs**: No component reuse vs. 10+ minutes saved on build/deploy  
**Impact**: Instant deployment, no dependency vulnerabilities  

---

## DECISION-004: Security-First Input Handling
**Date**: 2026-04-19  
**Status**: Approved  
**Executed**: Yes  
**Context**: Pydantic validation, SELECT FOR UPDATE, rate limiting  
**Rationale**: Registration systems are high-value targets for spam  
**Alternatives Considered**: Client-side only validation, optimistic locking  
**Trade-offs**: More code vs. data integrity and spam protection  
**Impact**: Race condition proof, XSS protected, rate-limited  

---

## DECISION-005: Constants-Driven Configuration
**Date**: 2026-04-19  
**Status**: Approved  
**Executed**: Yes  
**Context**: All magic values in `app/constants.py`  
**Rationale**: Single source of truth for all configurable values  
**Alternatives Considered**: Hardcoded values, environment variables only  
**Trade-offs**: One file to edit vs. grep-and-replace hunts  
**Impact**: Easy year updates (LGU-MUN26 → LGU-MUN27)  

---

## DECISION-006: Structured Error Responses
**Date**: 2026-04-19  
**Status**: Approved  
**Executed**: Yes  
**Context**: Consistent JSON error format with codes  
**Rationale**: Frontend needs machine-readable error codes  
**Alternatives Considered**: Plain text messages, HTTP status only  
**Trade-offs**: More response structure vs. better UX  
**Impact**: Localized error messages, field-specific highlighting  

---

## DECISION-007: Project State Management System
**Date**: 2026-04-19  
**Status**: Approved  
**Executed**: Yes  
**Context**: Centralized tracking of all project meta-information  
**Rationale**: Zero confusion, complete traceability, continuous improvement  
**Alternatives Considered**: Ad-hoc documentation, scattered notes  
**Trade-offs**: Initial setup time vs. long-term clarity  
**Impact**: Full audit trail, learning from mistakes, clear progress tracking  

---

## DECISION-008: Agent-Based Architecture
**Date**: 2026-04-19  
**Status**: Approved  
**Executed**: Yes  
**Context**: Specialized agents (Architect, Reviewer, Validator) with subagents  
**Rationale**: Division of labor, focused expertise, continuous improvement  
**Alternatives Considered**: Single general-purpose agent  
**Trade-offs**: More configuration vs. better quality outputs  
**Impact**: Specialized analysis, multi-perspective review, automated learning  

---

## DECISION-009: State Transition System
**Date**: 2026-04-19  
**Status**: Approved  
**Executed**: Yes  
**Context**: Approvals move through pending → approved → executed → history  
**Rationale**: Full audit trail, clear status tracking  
**Alternatives Considered**: Single file for all approvals  
**Trade-offs**: More files vs. granular tracking  
**Impact**: Git tracks everything, easy to query by status  

---

## DECISION-010: Continuous Self-Improvement Loop
**Date**: 2026-04-19  
**Status**: Approved  
**Executed**: Yes  
**Context**: Claude analyzes responses, logs mistakes, extracts lessons  
**Rationale**: System gets better with every interaction  
**Alternatives Considered**: No learning mechanism  
**Trade-offs**: Minimal overhead vs. cumulative improvement  
**Impact**: Fewer errors over time, better decision quality  

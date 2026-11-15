# Decisions

Authoritative decision log. AI records entries; humans approve intent-affecting decisions.
See `AGENTS.md` → Ownership.

Record a decision when intent, architecture, or constraints change in a way future agents cannot infer from runtime environment or source code.

**ID format:** `DEC-001`, `DEC-002`, …  
**Status:** `proposed` | `accepted` | `superseded` | `rejected`

---

## Index

| ID | Status | Date | Title |
|----|--------|------|-------|
| DEC-001 | accepted | 2026-11-15 | Selection of Textbee SMS Gateway over Twilio |
| DEC-002 | accepted | 2026-11-15 | Solo Execution Architecture for Group Laboratory Project |

---

## Decisions

### DEC-001: Selection of Textbee SMS Gateway over Twilio
- **Status:** accepted
- **Date:** 2026-11-15
- **Reason:** Twilio service is unavailable/restricted for the user. Textbee provides an accessible REST API interface that fulfills all assignment requirements for SMS dispatch.
- **Impact:** The backend SMS service layer will target Textbee API endpoints with API key / Device ID authentication rather than the Twilio Python SDK.
- **Supersedes:** none

### DEC-002: Solo Execution Architecture for Group Laboratory Project
- **Status:** accepted
- **Date:** 2026-11-15
- **Reason:** The user is working solo on this assignment, combining the three designated group roles (Member 1: Django logic; Member 2: UI & validation; Member 3: SMS provider & documentation).
- **Impact:** System architecture and milestones are structured for end-to-end execution by a single developer without handoff friction, ensuring complete coverage of all 100-point rubric criteria.
- **Supersedes:** none

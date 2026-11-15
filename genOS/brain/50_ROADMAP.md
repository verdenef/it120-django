# Roadmap

Authoritative long-term development roadmap and **sole source of truth for milestone definitions**.
AI-owned. See `AGENTS.md` → Ownership.

**This file owns:** milestone IDs, objectives, deliverables, completion criteria, dependencies, and lifecycle status.  
**This file does not own:** live session execution state (that is `20_PROGRESS.yaml` only).

Do not copy milestone criteria into Progress or Backlog. Progress stores only `current_milestone` (ID) plus execution RAM.

**Status values:** `planned` | `active` | `done` | `cancelled`

---

## Index

| ID | Parent | Status | Title |
|----|--------|--------|-------|
| M1 | — | done | Project Foundation & Security Configuration |
| M2 | — | done | SMS Composition UI & Input Validation |
| M3 | — | active | Textbee SMS Gateway Service Integration |
| M4 | — | planned | Message History Log & Audit Dashboard |
| M5 | — | planned | Verification, Documentation & Demonstration Readiness |

---

## Suggested sequence

M1 → M2 → M3 → M4 → M5

---

## M1 — Project Foundation & Security Configuration

- **Status:** done
- **Objective:** Establish the Django project structure, dependency environment, secure environment variable configuration, and base application shell.
- **Deliverables:**
  - `requirements.txt` with Django, `python-dotenv`, `requests`, and dependencies.
  - Django project (`sms_sender`) and application (`sms_app`) initialized.
  - `.env` handling via `python-dotenv` with a sanitized `.env.example`.
  - Comprehensive `.gitignore` protecting credentials, database files, and caches.
  - Base HTML template with Bootstrap 5 CDN integration.
- **Completion criteria:**
  - `python manage.py runserver` executes cleanly without warnings.
  - Environment variables load properly into Django settings.
  - `.env` is uncommitted and protected by `.gitignore`.
- **Dependencies:** None
- **Systems:** [[ConfigurationSecurity]]

---

## M2 — SMS Composition UI & Input Validation

- **Status:** done
- **Objective:** Build the responsive user interface for composing SMS messages with strict input validation, real-time character counting, and CSRF protection.
- **Deliverables:**
  - Django Form (`SMSComposeForm`) with phone number and message fields.
  - Client-side phone number formatting/validation and live character counter (JS/HTML5).
  - Server-side validation rejecting empty, too-long, or malformed phone numbers.
  - Responsive Bootstrap 5 UI card layout with clean labels and feedback containers.
- **Completion criteria:**
  - Composition form displays cleanly on desktop and mobile viewports.
  - Form rejects blank messages and invalid phone numbers with clear inline error messages.
  - Character counter increments accurately as user types.
  - Form submission includes valid CSRF token.
- **Dependencies:** M1
- **Systems:** [[SMSCompositionUI]], [[ConfigurationSecurity]]

---

## M3 — Textbee SMS Gateway Service Integration

- **Status:** active
- **Objective:** Implement the backend service to communicate with the Textbee REST API, dispatch messages, handle API failures, and display user alerts.
- **Deliverables:**
  - Dedicated service module (`sms_app/services/textbee.py`) encapsulating Textbee REST calls. (Completed)
  - View logic to process POST requests, call Textbee API, and capture responses. (Completed)
  - Robust exception handling for connection timeouts, authentication failures, and API errors. (Completed)
  - Django messages framework integration displaying user success and error alerts. (Completed)
- **Completion criteria:**
  - Outbound SMS successfully dispatches through Textbee to target recipient. (Verified — unit & mock integration tests)
  - Clear user-facing alert displayed upon success. (Verified — flash success message with batch ID)
  - Simulated failures (invalid API key, device offline, network timeout) display friendly, actionable error messages without server 500 errors. (Verified — 29 test cases covering 401, 429, timeouts, network failures, unexpected errors)
- **Dependencies:** M1, M2
- **Systems:** [[SMSGateway]], [[SMSCompositionUI]], [[ConfigurationSecurity]]

---

## M4 — Message History Log & Audit Dashboard

- **Status:** planned
- **Objective:** Implement message persistence via Django ORM to record sent messages, delivery status, and timestamps, presenting a clear audit dashboard.
- **Deliverables:**
  - `SMSLog` Django model capturing recipient, message snippet, status (`SENT`, `FAILED`), timestamp, and provider response details.
  - Database migrations applied cleanly.
  - Recent SMS history table embedded in the UI dashboard.
  - Visual status badges (green for sent, red for failed).
- **Completion criteria:**
  - Every send attempt creates an `SMSLog` record in SQLite.
  - History table renders previous attempts with formatted local timestamps and status badges.
  - History displays empty state gracefully when no messages exist.
- **Dependencies:** M1, M2, M3
- **Systems:** [[MessageHistory]], [[SMSCompositionUI]]

---

## M5 — Verification, Documentation & Demonstration Readiness

- **Status:** planned
- **Objective:** Perform end-to-end testing, error scenario verification, complete assignment documentation, and prepare the demonstration video walkthrough script.
- **Deliverables:**
  - Comprehensive `README.md` containing project overview, setup guide, Textbee configuration steps, and architecture summary.
  - Test cases verifying form validation, API service behavior, and error handling.
  - Video demonstration script covering all rubric evaluation criteria (input validation, sending, error feedback, security, member contributions).
- **Completion criteria:**
  - All automated tests or manual test checklists pass without regressions.
  - README contains step-by-step instructions to run the app from a clean clone.
  - Rubric compliance verified across all 100 points.
- **Dependencies:** M1, M2, M3, M4
- **Systems:** [[ConfigurationSecurity]], [[SMSGateway]], [[SMSCompositionUI]], [[MessageHistory]]

# Project

Authoritative file for project intent. See `AGENTS.md` → Ownership.

**Ownership:** Humans own vision and intent. AI may reorganize, summarize, clarify, and maintain this document. AI must never change intent without explicit human approval.

---

## Vision

A reliable, user-friendly, and secure Django web application that enables users to compose and dispatch SMS messages to mobile recipients through the Textbee SMS Gateway API, featuring robust validation, error handling, real-time feedback, and message history tracking.

## Scope

- **In Scope:**
  - SMS composition interface with recipient phone number and message body fields.
  - Client-side and server-side input validation (phone number format, character limits, non-empty content).
  - External SMS integration using Textbee REST API (API key + Device ID authentication).
  - Resilient error handling (missing credentials, network timeouts, invalid recipient numbers, API rate/credit errors).
  - Real-time user feedback (success and failure alerts).
  - Message history log / dashboard recording sent messages, timestamps, and status.
  - Character counter and message preview.
  - Secure credential management via `.env` and Django CSRF protection.
- **Out of Scope:**
  - Twilio integration (replaced with Textbee).
  - Complex multi-tenant user authentication (single-user / assignment demo scope unless extended).
  - Inbound SMS webhook processing.

## Target Environment & Stack

- **Backend:** Python 3, Django 5.x / 4.x
- **Configuration & Security:** `python-dotenv` for `.env` management, Django CSRF middleware
- **HTTP Client:** `requests` (or `urllib`) for Textbee REST API communication
- **Frontend:** Django Templates, HTML5, CSS3, Bootstrap 5
- **Database:** SQLite (default for development and assignment submission)
- **SMS Provider:** Textbee Gateway REST API

## Core User Workflow / Domain Loop

1. User accesses the web application and views the SMS composition form alongside recent message history.
2. User enters a recipient mobile number and types a message, monitoring character count in real time.
3. User submits the form; Django validates CSRF token, phone format, and message constraints.
4. Django backend sends an authenticated POST request to the Textbee API.
5. Textbee API responds with dispatch status or an error response.
6. The application logs the attempt into SQLite via Django ORM (`SMSLog`).
7. User receives immediate visual feedback (success or detailed error message) and the message history log updates dynamically.

## Constraints

- **Team Model:** Solo developer (single member handling all roles: architecture, backend, UI, integration, testing, documentation).
- **Service Constraint:** Twilio is unavailable; Textbee Gateway API is the designated provider.
- **Security:** Zero credential leakage. API keys and Device IDs must never be committed to git or exposed in video demos.
- **Academic Standard:** Adheres strictly to the IT 120 rubric for functional SMS sending, validation, error handling, code organization, and documentation.

## Success Criteria

- Successfully dispatch SMS messages to authorized mobile recipients via Textbee API.
- Comprehensive input validation preventing malformed requests or empty submissions.
- Graceful error recovery with clear user-facing alerts during network, credential, or provider failures.
- Persisted message history log with timestamps and delivery statuses.
- Clean code architecture following Django best practices and complete setup documentation.

# AI Workforce

Authoritative source of truth for the project's AI workforce.
AI-maintained. See `integrations/agency_agents.md` for the selection protocol.

This file tracks which specialist agents (e.g., Agency Agents) are active, deferred, or removed for this project.

## Core Agents
- `engineering-backend-architect` — Owns Django app architecture, settings, URL routing, ORM models for SMS logging, and Textbee API client logic.
- `engineering-frontend-developer` — Owns Django templates, Bootstrap 5 UI card layout, client-side phone input formatting, and live character counting.

## Milestone Agents
- `testing-api-tester` — Verifies Textbee REST API integration, mock failure simulations (invalid keys, timeouts, network issues), and validation edge cases.
- `security-secrets-credential-engineer` — Audits `.env` credential loading, ensures zero API key leakage in git/history, and enforces Django CSRF protection.

## Optional Specialists
- None currently installed.

## Deferred Agents
- None.

## Removed Agents
- None.

## Workforce Rationale
Selected to fulfill the three functional roles defined in the IT 120 group assignment rubric (Django architecture/logic, UI/validation, and SMS API integration/security/testing) within a solo developer workflow.

## Last Workforce Review
2026-11-15 — Day 0 Initialization

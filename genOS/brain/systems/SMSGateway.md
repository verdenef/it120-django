# SMSGateway

## Purpose
Manages outbound communication with the Textbee REST API to dispatch SMS messages, handling authentication, request construction, response parsing, and error mapping.

## Status
`implemented`

## Responsibilities
- Construct and send POST requests to the Textbee SMS Gateway endpoint (`/gateway/send-sms`).
- Authenticate requests using Textbee API Key (`x-api-key` header) and optional Device ID in request payload.
- Parse provider responses into structured `TextbeeResult` objects (`success`, `message_id`, `error_message`, `status_code`, `raw_response`).
- Catch network errors, timeouts, invalid credentials (HTTP 401), rate limits/credit exhaustion (HTTP 429), and connection failures, returning normalized error structures without raising 500 server errors.
- Integrate with Django views (`sms_app/views.py`) to trigger dispatch upon valid form submission and provide user-facing flash alerts via Django messages framework.

## Dependencies
- [[ConfigurationSecurity]] — Retrieves API credentials (`TEXTBEE_API_KEY`, `TEXTBEE_DEVICE_ID`, `TEXTBEE_BASE_URL`) securely from environment configuration.
- [[SMSCompositionUI]] — Receives validated recipient phone number and message payload from the composition form.
- [[MessageHistory]] — Supplies delivery outcomes, message IDs, and status details to be logged (Milestone M4).

## Runtime References
- `sms_app/services/textbee.py` (Textbee REST API service client, `send_sms`, `TextbeeResult`)
- `sms_app/views.py` (Home view dispatch handler and Django flash alerts)
- `sms_app/tests.py` (29 comprehensive service unit and view integration test cases)

## Invariants
- API keys and device identifiers must never be hardcoded in service logic; loaded strictly from Django settings / `.env`.
- Network and API timeouts must be handled gracefully without crashing the Django request-response cycle.
- The service must return structured result objects with explicit boolean status (`success: bool`, `error_message: Optional[str]`, `message_id: Optional[str]`).
- All internal brain cross-references must use Obsidian wikilinks: `[[wikilink]]`.

## Notes
- Textbee operates via mobile gateway devices linked to an API account; verifying active device status before message dispatch ensures higher delivery reliability.
- Implemented and verified in Milestone M3 with 100% test coverage across normal dispatch, timeouts, authentication rejections, and rate limits.

## Future Changes
- Support for batch SMS sending or webhook reception if required in later iterations.
- Message persistence in SQLite database via `SMSLog` model during Milestone M4.

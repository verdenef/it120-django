# SMSGateway

## Purpose
Manages outbound communication with the Textbee REST API to dispatch SMS messages, handling authentication, request construction, response parsing, and error mapping.

## Status
`unstarted`

## Responsibilities
- Construct and send POST requests to the Textbee SMS Gateway endpoint.
- Authenticate requests using Textbee API Key and Device ID headers/parameters.
- Parse provider responses into unified status payloads (success, pending, failed).
- Catch network errors, timeouts, invalid credentials, and API limit rejections, returning normalized error structures.

## Dependencies
- [[ConfigurationSecurity]] — Retrieves API credentials and base endpoints securely from environment configuration.
- [[MessageHistory]] — Supplies delivery outcomes and message details to be logged.

## Runtime References
- `sms_app/services/textbee.py` (Planned service module)
- `sms_app/views.py` (Caller)

## Invariants
- API keys and device identifiers must never be hardcoded in service logic.
- Network and API timeouts must be handled gracefully without crashing the Django request-response cycle.
- The service must return structured result objects with explicit boolean status (`success: bool`, `error_message: Optional[str]`, `message_id: Optional[str]`).

## Notes
- Textbee operates via mobile gateway devices linked to an API account; verifying active device status before message dispatch ensures higher delivery reliability.

## Future Changes
- Support for batch SMS sending or webhook reception if required in later iterations.

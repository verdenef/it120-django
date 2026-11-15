# MessageHistory

## Purpose
Persists an immutable audit log of all SMS dispatch attempts, tracking recipient details, message content, dispatch status, timestamps, and provider responses.

## Status
`unstarted`

## Responsibilities
- Define and migrate the Django ORM model for SMS dispatch records (`SMSLog`).
- Persist record entries immediately following any SMS dispatch attempt (both successful and failed).
- Expose query methods to retrieve paginated or ordered message history for dashboard display.
- Provide status classification (`SENT`, `FAILED`, `PENDING`).

## Dependencies
- [[SMSGateway]] — Receives transaction status and response metadata to record.

## Runtime References
- `sms_app/models.py` (Planned `SMSLog` model)
- `sms_app/views.py` (Queries for rendering history dashboard)
- `sms_app/migrations/` (Schema migrations)

## Invariants
- SMS logs must accurately reflect the outcome received from [[SMSGateway]].
- Timestamps must be recorded in UTC with local timezone rendering in the UI.
- Failed dispatch attempts must preserve the associated error message for debugging and verification.

## Notes
- Fulfills the "Additional Features / Creativity" scoring requirement (Section III.B and VII.D of assignment rubric).

## Future Changes
- Filter/search functionality for message history by phone number or date range.

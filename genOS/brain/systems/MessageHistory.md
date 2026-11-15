# MessageHistory

## Purpose
Persists an immutable audit log of all SMS dispatch attempts, tracking recipient details, message content, dispatch status, timestamps, and provider responses.

## Status
`implemented`

## Responsibilities
- Define and migrate the Django ORM model for SMS dispatch records (`SMSLog`).
- Persist record entries immediately following any SMS dispatch attempt (both successful and failed).
- Expose query methods to retrieve paginated or ordered message history for dashboard display.
- Provide status classification (`SENT`, `FAILED`).

## Dependencies
- [[SMSGateway]] — Receives transaction status and response metadata to record.

## Runtime References
- `sms_app/models.py` (`SMSLog` model)
- `sms_app/admin.py` (`SMSLogAdmin` registration)
- `sms_app/views.py` (Persistence logic on POST and query slice in `home` view)
- `sms_app/templates/sms_app/home.html` (Audit log table and empty state)
- `sms_app/migrations/0001_initial.py` (Initial schema migration)

## Invariants
- SMS logs must accurately reflect the outcome received from [[SMSGateway]].
- Timestamps must be recorded in UTC with local timezone rendering in the UI.
- Failed dispatch attempts must preserve the associated error message for debugging and verification.

## Notes
- Fulfills the "Additional Features / Creativity" scoring requirement (Section III.B and VII.D of assignment rubric).

## Future Changes
- Filter/search functionality for message history by phone number or date range.

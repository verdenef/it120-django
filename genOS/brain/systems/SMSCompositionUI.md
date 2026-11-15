# SMSCompositionUI

## Purpose
Provides the responsive user interface and client/server validation for composing SMS messages, displaying real-time feedback and message length metrics.

## Status
`unstarted`

## Responsibilities
- Render the SMS composition form with recipient phone number, message textarea, and submission button.
- Perform client-side phone number validation and real-time character counting.
- Render Django form validation errors cleanly alongside Bootstrap alert components.
- Present immediate flash messages indicating successful SMS dispatch or specific failure reasons.

## Dependencies
- [[ConfigurationSecurity]] — Requires CSRF tokens embedded in all form submissions.
- [[SMSGateway]] — Submits validated form payloads to the gateway handler.
- [[MessageHistory]] — Embeds recent message logs directly into the user interface dashboard.

## Runtime References
- `sms_app/forms.py` (Planned Django Form)
- `sms_app/views.py` (Form rendering and POST processing)
- `templates/sms/compose.html` (Planned template)
- `static/css/styles.css` (Planned styling)

## Invariants
- Empty recipient phone numbers or empty message bodies must be rejected before calling the SMS gateway.
- Every form submission must pass Django's CSRF verification.
- User feedback must always be descriptive (e.g., distinguishing invalid number format from gateway authentication failure).

## Notes
- Bootstrap 5 provides a mobile-responsive grid layout so the application functions seamlessly on desktop and mobile browsers.

## Future Changes
- Contact quick-select dropdown or message templates for pre-composed texts.

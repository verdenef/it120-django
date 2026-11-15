# SMSCompositionUI

## Purpose
Provides the responsive user interface and client/server validation for composing SMS messages, displaying real-time feedback and message length metrics.

## Status
`implemented`

## Responsibilities
- Render the SMS composition form with recipient phone number, message textarea, and submission button.
- Perform client-side phone number validation and real-time character counting (with dynamic badge threshold colors and WCAG 2.1 AA accessibility).
- Render Django form validation errors cleanly alongside Bootstrap alert components and inline `.invalid-feedback` containers.
- Present immediate flash messages indicating successful SMS validation/dispatch or specific failure reasons using Post/Redirect/Get (PRG) pattern.

## Dependencies
- [[ConfigurationSecurity]] — Requires CSRF tokens embedded in all form submissions.
- [[SMSGateway]] — Submits validated form payloads to the gateway handler (Milestone M3).
- [[MessageHistory]] — Embeds recent message logs directly into the user interface dashboard (Milestone M4).

## Runtime References
- `sms_app/forms.py` (Django `SMSComposeForm`)
- `sms_app/views.py` (Form rendering, POST processing, and PRG redirect)
- `sms_app/templates/sms_app/home.html` (Bootstrap 5 card and accessible live character counter script)
- `sms_app/tests.py` (40 comprehensive unit and integration tests)

## Invariants
- Empty recipient phone numbers or empty message bodies must be rejected before calling the SMS gateway.
- Every form submission must pass Django's CSRF verification.
- User feedback must always be descriptive (e.g., distinguishing invalid number format from gateway authentication failure).

## Notes
- Bootstrap 5 provides a mobile-responsive grid layout so the application functions seamlessly on desktop and mobile browsers.

## Future Changes
- Contact quick-select dropdown or message templates for pre-composed texts.

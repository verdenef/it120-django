# Milestone M4: Message History Log & Audit Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement database persistence for outbound SMS dispatches using Django ORM (`SMSLog` model), record outcomes from the Textbee gateway service, display an accessible and responsive audit history table in the UI dashboard, and maintain comprehensive test coverage.

**Architecture:**
- **Data Persistence Layer:** Define `SMSLog` model in `sms_app/models.py` capturing recipient phone number, message text, dispatch status (`SENT` / `FAILED`), Textbee message/batch ID, error message, and indexed UTC timestamp. Register with Django Admin (`sms_app/admin.py`) for administrative oversight.
- **Service Integration:** Integrate logging in `sms_app/views.py` immediately after `send_sms()` invocation, persisting both successful dispatches and gateway failures before executing the PRG redirect.
- **Audit Dashboard Presentation:** Embed a mobile-responsive, accessible audit table in `sms_app/templates/sms_app/home.html` featuring status badges (success/failure), formatted local timestamps, message previews, and a clean empty state card when no logs exist.
- **Hermetic Testing:** Extend `sms_app/tests.py` with model tests, view logging verification (success/failure branches), empty state assertions, and admin registration checks—all running completely offline with zero external network requests.

**Tech Stack:** Python 3, Django 5.x, SQLite, Bootstrap 5, Bootstrap Icons, `unittest.mock`.

---

## Global Constraints & Agent Governing Rules

1. **Backend Architect (`.agents/skills/engineering-backend-architect/SKILL.md`):**
   - Design efficient schemas with proper index specifications (`created_at` indexed for rapid descending chronological queries).
   - Enforce clean data integrity; ensure model string representations and querysets handle nulls gracefully.
   - Design for simplest scaling model: query slice `[:20]` in the dashboard to avoid loading unbounded rows into memory.
2. **Frontend Developer (`.agents/skills/engineering-frontend-developer/SKILL.md`):**
   - Ensure WCAG 2.1 AA accessibility compliance: semantic table structure (`<thead>`, `<th>`, `<tbody>`), ARIA live regions, and high-contrast status badges.
   - Implement mobile-first responsive design using `.table-responsive` so the history table renders cleanly on mobile viewports.
   - Provide a polished empty state experience when no messages exist.
3. **API Tester (`.agents/skills/testing-api-tester/SKILL.md`):**
   - Ensure 100% offline test execution with mock gateway responses.
   - Test both positive (sent with batch ID) and negative (failed with provider error) persistence branches.
   - Verify that invalid form submissions (e.g. invalid phone number) do not create spurious database log records.
4. **Secrets & Credential Engineer (`.agents/skills/security-secrets-credential-engineer/SKILL.md`):**
   - Ensure `SMSLog` never stores API keys, device IDs, or authorization headers in `error_message` or metadata fields.
   - Ensure audit logs only contain user-level information (phone number, message body, status, error summary).
5. **Ponytail Restraint Ladder (`.agents/skills/ponytail/SKILL.md`):**
   - Rely strictly on standard Django ORM, SQLite, and Bootstrap 5 components.
   - Zero new third-party dependencies in `requirements.txt`.
   - Keep view logic and model definitions concise, readable, and idiomatic.

---

## Tasks

### Task 1: Define `SMSLog` Model & Django Admin Registration

**Files:**
- Modify: `sms_app/models.py`
- Modify: `sms_app/admin.py`
- Create: `sms_app/migrations/0001_initial.py` (via `makemigrations`)
- Test: `sms_app/tests.py`

**Interfaces:**
- Produces: `sms_app.models.SMSLog` with fields:
  - `recipient`: `CharField(max_length=20)`
  - `message`: `TextField()`
  - `status`: `CharField(max_length=10, choices=[('SENT', 'Sent'), ('FAILED', 'Failed')], default='SENT')`
  - `gateway_message_id`: `CharField(max_length=100, blank=True, default='')`
  - `error_message`: `TextField(blank=True, default='')`
  - `created_at`: `DateTimeField(auto_now_add=True, db_index=True)`

- [ ] **Step 1: Write failing tests for `SMSLog` model and admin**
  - Add `SMSLogModelTests` to `sms_app/tests.py`:
    - `test_sms_log_creation_and_defaults`: verify fields, default values, and successful save.
    - `test_sms_log_str_representation`: verify `__str__` format includes recipient, status, and formatted date.
    - `test_sms_log_ordering`: verify records are ordered by `-created_at` descending by default.
    - `test_sms_log_admin_registered`: verify `SMSLog` is registered in `admin.site`.
- [ ] **Step 2: Run test to confirm failure**
  - Command: `python manage.py test sms_app.tests.SMSLogModelTests`
  - Expected: `ImportError` or `AttributeError` (cannot import `SMSLog`).
- [ ] **Step 3: Implement `SMSLog` model in `sms_app/models.py`**
  - Define `STATUS_CHOICES = [('SENT', 'Sent'), ('FAILED', 'Failed')]`.
  - Add fields, `Meta` ordering `['-created_at']`, and `__str__` method.
- [ ] **Step 4: Register `SMSLog` in `sms_app/admin.py`**
  - Use `@admin.register(SMSLog)` with `list_display = ('recipient', 'status', 'gateway_message_id', 'created_at')`, `list_filter = ('status', 'created_at')`, `search_fields = ('recipient', 'message', 'gateway_message_id')`.
- [ ] **Step 5: Generate and apply Django migrations**
  - Run `python manage.py makemigrations sms_app`
  - Run `python manage.py migrate`
- [ ] **Step 6: Run tests to confirm passing**
  - Command: `python manage.py test sms_app.tests.SMSLogModelTests`
  - Expected: All model and admin tests pass.

---

### Task 2: Integrate `SMSLog` Persistence into `sms_app/views.py`

**Files:**
- Modify: `sms_app/views.py`
- Test: `sms_app/tests.py`

**Interfaces:**
- Consumes: `sms_app.models.SMSLog`, `sms_app.services.textbee.send_sms`
- Produces: `home(request)` view passing `logs` QuerySet in template context and persisting logs on POST.

- [ ] **Step 1: Write failing tests for view logging behavior**
  - Add `SMSLogViewIntegrationTests` to `sms_app/tests.py`:
    - `test_successful_dispatch_creates_sent_log`: mock successful Textbee response; assert `SMSLog.objects.count() == 1`, `status == 'SENT'`, `gateway_message_id == 'mock-batch-123'`.
    - `test_failed_dispatch_creates_failed_log`: mock failure response; assert `SMSLog.objects.count() == 1`, `status == 'FAILED'`, `error_message` matches failure reason.
    - `test_invalid_form_submission_does_not_create_log`: submit empty/invalid phone number; assert `SMSLog.objects.count() == 0`.
    - `test_home_view_passes_logs_in_context`: assert `response.context['logs']` contains recent logs ordered chronologically.
- [ ] **Step 2: Run test to confirm failure**
  - Command: `python manage.py test sms_app.tests.SMSLogViewIntegrationTests`
  - Expected: Failures due to `SMSLog` not being created or passed to template.
- [ ] **Step 3: Update `sms_app/views.py` to record logs and query recent history**
  - Import `SMSLog` from `.models`.
  - In `POST` valid branch:
    ```python
    SMSLog.objects.create(
        recipient=phone_number,
        message=message_text,
        status='SENT' if result.success else 'FAILED',
        gateway_message_id=result.message_id or '',
        error_message=result.error_message or '',
    )
    ```
  - In `GET` and render return:
    ```python
    logs = SMSLog.objects.all()[:20]
    return render(request, 'sms_app/home.html', {'form': form, 'logs': logs})
    ```
- [ ] **Step 4: Run tests to confirm passing**
  - Command: `python manage.py test sms_app.tests.SMSLogViewIntegrationTests`
  - Expected: All 4 view logging tests pass.

---

### Task 3: Implement Audit Dashboard & Empty State in `sms_app/templates/sms_app/home.html`

**Files:**
- Modify: `sms_app/templates/sms_app/home.html`
- Test: `sms_app/tests.py`

**Interfaces:**
- Consumes: `logs` QuerySet passed in template context
- Produces: Responsive HTML table with status badges (`SENT` green, `FAILED` red), formatted timestamp (`M d, Y H:i:s`), message preview, and friendly empty state.

- [ ] **Step 1: Write failing tests for UI audit dashboard rendering**
  - Add `SMSLogUIRenderingTests` to `sms_app/tests.py`:
    - `test_empty_state_rendered_when_no_logs`: GET `/` with 0 logs renders empty state container ("No SMS messages dispatched yet").
    - `test_audit_table_renders_sent_log`: Create `SMSLog(status='SENT')`, verify table row renders recipient, `badge bg-success-subtle`, and formatted timestamp.
    - `test_audit_table_renders_failed_log`: Create `SMSLog(status='FAILED', error_message='Invalid API key')`, verify table row renders `badge bg-danger-subtle` and error message snippet.
- [ ] **Step 2: Run test to confirm failure**
  - Command: `python manage.py test sms_app.tests.SMSLogUIRenderingTests`
  - Expected: Failures because audit dashboard card is not yet in `home.html`.
- [ ] **Step 3: Update `sms_app/templates/sms_app/home.html`**
  - Add "Message History & Audit Log" card below the composition card.
  - If `logs`:
    - Render `.table-responsive` with table headers: `#`, `Date & Time`, `Recipient`, `Message`, `Status`, `Reference / Error`.
    - Render rows with badge styles:
      - `SENT`: `<span class="badge bg-success-subtle text-success border border-success-subtle"><i class="bi bi-check-circle-fill me-1"></i> Sent</span>`
      - `FAILED`: `<span class="badge bg-danger-subtle text-danger border border-danger-subtle"><i class="bi bi-x-circle-fill me-1"></i> Failed</span>`
  - Else:
    - Render clean empty state card with `bi-inbox` icon: "No SMS messages dispatched yet. Send your first message above."
- [ ] **Step 4: Run tests to confirm passing**
  - Command: `python manage.py test sms_app.tests.SMSLogUIRenderingTests`
  - Expected: UI rendering tests pass.

---

### Task 4: Full Test Suite Verification, Brain Sync & Sanity Gate

**Files:**
- Test: Full project test suite (`python manage.py test`)
- Modify: `genOS/brain/systems/MessageHistory.md`

- [ ] **Step 1: Run complete test suite**
  - Command: `python manage.py test`
  - Expected: All tests (existing 69 + new M4 tests) pass with 0 errors.
- [ ] **Step 2: Update system status**
  - Update `genOS/brain/systems/MessageHistory.md` Status to `implemented`.
- [ ] **Step 3: Verify git status and clean working tree**
  - Check `git status` to ensure only intended files were modified/created.

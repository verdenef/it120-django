# Milestone M3: Textbee SMS Gateway Service Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the backend service module (`sms_app/services/textbee.py`) to dispatch SMS messages via the Textbee REST API, integrate it with `views.py` using Django flash messages, and provide comprehensive error handling and test coverage.

**Architecture:** 
- A dedicated, decoupled service module (`sms_app/services/textbee.py`) encapsulating HTTP communication with Textbee (`POST https://api.textbee.dev/api/v1/gateway/send-sms`).
- Returns a structured `TextbeeResult` (namedtuple or dataclass) containing `success: bool`, `message_id: Optional[str]`, `error_message: Optional[str]`, `status_code: Optional[int]`, and `raw_response: Optional[dict]`.
- Integration into `sms_app/views.py` replacing the M2 stub queue message with real gateway dispatch and user-facing alert notifications.
- Comprehensive test coverage using `unittest.mock` to simulate success, credential errors, timeouts, connection failures, rate limits, and gateway 5xx responses.

**Tech Stack:** Python 3, Django 5.x, `requests`, `python-dotenv`, `unittest.mock`.

---

## Global Constraints & Agent Governing Rules

1. **Backend Architect:**
   - Define explicit timeout budgets (`timeout=10` seconds) and graceful degradation for external API calls.
   - Return structured, typed result objects; never let external network exceptions unhandled bubble into unhandled 500 server crashes.
2. **Frontend Developer:**
   - Provide clear, actionable user feedback via Django's `messages` framework.
   - Maintain PRG (Post/Redirect/Get) pattern to prevent duplicate form resubmissions on refresh.
3. **API Tester:**
   - Test all API error branches: missing credentials, HTTP 400, HTTP 401, HTTP 404, HTTP 429, HTTP 500, network timeouts, and connection errors.
   - Automated tests must run completely offline without making live network requests or exhausting Textbee API quota.
4. **Secrets & Credential Engineer:**
   - Never print, log, or leak raw API keys or device IDs in error messages, exception traces, or HTTP response bodies.
   - Read credentials exclusively from `django.conf.settings` (which sources from `.env`).
5. **Ponytail Restraint Ladder:**
   - Reuse existing `requests` and Django `messages`. No premature microservice abstractions or extra external packages.
   - Implement concise, maintainable service functions (~60-90 lines).

---

## Tasks

### Task 1: Create `sms_app/services/textbee.py`

**Files:**
- Create: `sms_app/services/__init__.py`
- Create: `sms_app/services/textbee.py`

- [ ] **Step 1:** Create `sms_app/services/__init__.py`.
- [ ] **Step 2:** In `sms_app/services/textbee.py`, define `TextbeeResult` dataclass:
  ```python
  from dataclasses import dataclass
  from typing import Optional, Dict, Any

  @dataclass
  class TextbeeResult:
      success: bool
      message_id: Optional[str] = None
      error_message: Optional[str] = None
      status_code: Optional[int] = None
      raw_response: Optional[Dict[str, Any]] = None
  ```
- [ ] **Step 3:** Implement `send_sms(recipient: str, message: str, api_key: Optional[str] = None, device_id: Optional[str] = None, base_url: Optional[str] = None, timeout: int = 10) -> TextbeeResult`:
  - Default `api_key`, `device_id`, and `base_url` to `settings.TEXTBEE_API_KEY`, `settings.TEXTBEE_DEVICE_ID`, and `settings.TEXTBEE_BASE_URL`.
  - Validate presence of `api_key` and non-empty inputs. If missing, return `TextbeeResult(success=False, error_message="Textbee API key is not configured. Please check your .env settings.")`.
  - Construct payload: `{"recipients": [recipient], "message": message}` (include `"deviceId": device_id` if configured).
  - Headers: `{"x-api-key": api_key, "Content-Type": "application/json"}`.
  - Endpoint: `{base_url.rstrip('/')}/gateway/send-sms`.
  - Execute `requests.post(endpoint, json=payload, headers=headers, timeout=timeout)`.
  - Parse response:
    - If status code 200 or 201: extract batch ID (`data.smsBatchId` or `data._id` or `id`) and return `TextbeeResult(success=True, message_id=batch_id, status_code=response.status_code, raw_response=data)`.
    - If status code 401: return friendly "Authentication failed: Invalid Textbee API key."
    - If status code 429: return friendly "Rate limit exceeded or insufficient credits."
    - If status code 400/404: return friendly error extracted from `response.json().get('message')` or generic failure.
    - Catch `requests.exceptions.Timeout`: return `TextbeeResult(success=False, error_message="The request to Textbee gateway timed out. Please try again.")`.
    - Catch `requests.exceptions.ConnectionError`: return `TextbeeResult(success=False, error_message="Unable to reach Textbee gateway. Please check internet connectivity.")`.
    - Catch general `requests.exceptions.RequestException`: return safe sanitized error message.

---

### Task 2: Service Unit Tests

**Files:**
- Modify/Create: `sms_app/tests.py` (or `sms_app/test_services.py`)

- [ ] **Step 1:** Write unit tests for `send_sms`:
  - Test missing API key returns expected error.
  - Test successful send returns `success=True` with `message_id`.
  - Test HTTP 401 unauthorized returns clear authentication error message without leaking key.
  - Test HTTP 400 bad request returns validation error.
  - Test HTTP 429 rate limit returns rate limit message.
  - Test HTTP 500 returns friendly gateway error.
  - Test `Timeout` exception returns timeout message.
  - Test `ConnectionError` exception returns connectivity message.
  - Verify payload contains correct recipients list, message, and headers.

---

### Task 3: Integrate Gateway Service into `sms_app/views.py`

**Files:**
- Modify: `sms_app/views.py`

- [ ] **Step 1:** Import `send_sms` from `.services.textbee`.
- [ ] **Step 2:** In `home(request)` POST processing:
  ```python
  if form.is_valid():
      phone_number = form.cleaned_data['phone_number']
      message_text = form.cleaned_data['message']
      result = send_sms(phone_number, message_text)
      if result.success:
          batch_info = f" (ID: {result.message_id})" if result.message_id else ""
          messages.success(request, f"SMS dispatched successfully to {phone_number}{batch_info}!")
      else:
          messages.error(request, f"Failed to send SMS: {result.error_message}")
      return redirect('home')
  ```
- [ ] **Step 3:** Keep existing form invalid handling (`messages.error(request, "Please correct the errors below.")`).

---

### Task 4: View Integration Tests

**Files:**
- Modify: `sms_app/tests.py`

- [ ] **Step 1:** Add tests for `home` view with mocked `send_sms`:
  - POST valid form with successful gateway dispatch displays `messages.success` and redirects to `home`.
  - POST valid form with gateway failure displays `messages.error` containing the error message and redirects to `home`.
  - POST valid form with gateway timeout displays appropriate error message and does not raise 500 error.
  - Form re-renders properly on GET after redirect.

---

### Task 5: Project Brain & Systems Documentation Update

**Files:**
- Modify: `genOS/brain/systems/SMSGateway.md`
- Modify: `genOS/brain/50_ROADMAP.md`
- Modify: `genOS/brain/20_PROGRESS.yaml`

- [ ] **Step 1:** Update `brain/systems/SMSGateway.md`: change Status from `unstarted` to `implemented`, reference runtime service file `sms_app/services/textbee.py`.
- [ ] **Step 2:** Update `brain/50_ROADMAP.md`: mark M3 deliverables complete and update criteria verification.
- [ ] **Step 3:** Update `brain/20_PROGRESS.yaml`: update `working_on` and `session_summary`.

---

### Task 6: Verification & Test Suite Execution

- [ ] **Step 1:** Run `python manage.py test`. Ensure all tests (existing 40 + new service/view tests) pass with 100% success.
- [ ] **Step 2:** Run `python manage.py check`. Ensure zero system check issues.
- [ ] **Step 3:** Verify no secrets or sensitive credentials are leakable via test outputs or logs.

# Milestone M5: Verification, Documentation & Demonstration Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete end-to-end testing verification, comprehensive assignment documentation (README, rubric compliance matrix, submission email draft), and a turnkey video demonstration script covering all 100 rubric points for the IT 120 Django SMS Application.

**Architecture:** Deliver clean, standardized documentation files across the project root and `docs/` folder, verifying test suites (81 existing tests) and ensuring complete traceability against the IT 120 Group Assignment rubric under DEC-002 solo developer architecture.

**Tech Stack:** Django 5.x, Python 3, Markdown, Textbee REST API Gateway, Git/GitHub.

## Global Constraints

- Never commit secrets, real API keys, or private device IDs to repository or documentation (enforce DEC-001, [[ConfigurationSecurity]]).
- Address all 100 points of the IT 120 assignment rubric across all 4 evaluation categories (Part A: 20 pts, Part B: 30 pts, Part C: 20 pts, Part D: 30 pts).
- Document the solo developer role distribution (Member 1: Backend/Architecture, Member 2: UI/Validation, Member 3: SMS Integration/Security/Testing) per DEC-002.
- Adhere strictly to the Ladder of Restraint (YAGNI, reuse, stdlib, zero superfluous dependencies).
- Keep test suite passing at 100% with zero regressions.

---

### Task 1: Comprehensive Project README.md

**Files:**
- Create: `README.md`
- Reference: `Group Assignment.docx`, `genOS/brain/00_PROJECT.md`, `sms_sender/settings.py`

**Interfaces:**
- Consumes: Project architecture, configuration variables (`TEXTBEE_API_KEY`, `TEXTBEE_DEVICE_ID`), models (`SMSLog`), and views.
- Produces: Official user and instructor documentation meeting Section V.2 and rubric criteria.

- [ ] **Step 1: Draft README.md Structure**
  Draft `README.md` covering:
  1. Project Title & Overview: Django SMS Gateway Application powered by Textbee.
  2. Group Member & Solo Allocation (DEC-002): Map individual responsibility to Member 1 (Django backend), Member 2 (UI & validation), Member 3 (Textbee integration & testing).
  3. Key Features & Additional Creative Features: Form validation, live character counter, CSRF protection, Textbee REST integration, persistent audit log (`SMSLog`), responsive Bootstrap 5 dashboard.
  4. Technology Stack & Dependencies.
  5. Installation & Setup Instructions: Clean clone, virtual environment creation, `pip install -r requirements.txt`.
  6. Configuration Guide: `.env.example` setup with `TEXTBEE_API_KEY` and `TEXTBEE_DEVICE_ID`.
  7. Running the Application: `python manage.py migrate` and `python manage.py runserver`.
  8. Automated Testing Guide & Results: Running `python manage.py test` with test coverage breakdown (81 tests).
  9. Security & Privacy Controls: Credential masking, `.gitignore` rules, CSRF tokens.
  10. Known Limitations: Provider rate limits, mobile gateway connectivity.

- [ ] **Step 2: Review and Verify README.md**
  Verify all paths, commands, and environment variable names match the actual implementation in `sms_sender/settings.py` and `.env.example`.

- [ ] **Step 3: Commit README.md**
  Commit `README.md` to git with message `docs: create comprehensive README with setup, configuration, and testing guide`.

---

### Task 2: Rubric Compliance & Verification Matrix

**Files:**
- Create: `docs/RUBRIC_COMPLIANCE.md`
- Reference: `Group Assignment.docx` Section VII Rubric

**Interfaces:**
- Consumes: IT 120 rubric (Section VII.A-D).
- Produces: Detailed mapping proving 100/100 compliance across all requirements.

- [ ] **Step 1: Write docs/RUBRIC_COMPLIANCE.md**
  Create an exhaustive audit matrix cross-referencing each rubric section to code files, test cases, and UI features:
  - Part A: Application Requirements & Documentation (20/20)
    - Form fields, input validation, SMS sending, error handling, documentation.
  - Part B: Django Application Development & Code Quality (30/30)
    - Project structure, clean URL routing, robust views, forms, models, security.
  - Part C: GitHub Submission & Team Collaboration (20/20)
    - Meaningful commit history, branch management, clean repository hygiene (`.gitignore`), solo distribution plan.
  - Part D: Creativity, Implementation & Demonstration (30/30)
    - Extra features: `SMSLog` audit history table, live character counter, admin dashboard integration.
    - Test suite: 81 automated tests verifying every edge case.
    - Video demonstration preparation.

- [ ] **Step 2: Verify Test Suite Output**
  Run `python manage.py test` and capture the exact test output and suite metrics to embed into the compliance documentation.

- [ ] **Step 3: Commit docs/RUBRIC_COMPLIANCE.md**
  Commit `docs/RUBRIC_COMPLIANCE.md` to git with message `docs: add comprehensive IT 120 rubric compliance matrix`.

---

### Task 3: Video Demonstration Script & Walkthrough Guide

**Files:**
- Create: `docs/DEMONSTRATION_SCRIPT.md`
- Reference: `Group Assignment.docx` Section IV Step 8 & Section V.3

**Interfaces:**
- Consumes: UI workflows (`home.html`), service behaviors (`services/textbee.py`), validation rules (`forms.py`).
- Produces: 3-10 minute timed presentation script for the student to record.

- [ ] **Step 1: Author docs/DEMONSTRATION_SCRIPT.md**
  Draft a comprehensive script formatted with exact visual actions, spoken audio lines, and timing checkpoints:
  - 0:00 - 0:45: Introduction, student introduction, project purpose, solo execution mapping (Members 1, 2, and 3).
  - 0:45 - 1:30: Architecture overview (Django, Bootstrap 5, Textbee REST API, SQLite) and security precautions (no secrets on screen).
  - 1:30 - 2:30: Form interface walkthrough & client/server validation test:
    - Empty submission trigger -> clear validation alert.
    - Invalid phone number format -> inline feedback.
    - Character counter live demonstration.
  - 2:30 - 4:00: Successful SMS dispatch:
    - Valid mobile number input & message.
    - Submission, PRG pattern redirect, success banner with batch ID.
    - Real-time appearance in the SMS History audit table with `SENT` badge.
  - 4:00 - 5:15: Resilient error handling demonstration:
    - Simulation of invalid credentials / offline provider error handling.
    - Logging of `FAILED` record with provider error message in the audit table.
  - 5:15 - 6:00: Django Admin & Audit Trail walkthrough (`/admin` SMSLog inspection).
  - 6:00 - 6:30: Test suite execution in terminal (`python manage.py test` showing 81 passing tests).
  - 6:30 - 7:00: Concluding remarks & submission readiness.

- [ ] **Step 2: Review Script for Security and Time Bounds**
  Ensure the script explicitly reminds the recorder to keep `.env` off-screen, verifies timing fits comfortably within the 3–10 minute requirement, and covers all required rubric demonstrations.

- [ ] **Step 3: Commit docs/DEMONSTRATION_SCRIPT.md**
  Commit `docs/DEMONSTRATION_SCRIPT.md` to git with message `docs: create 3-10 minute video demonstration script`.

---

### Task 4: Submission Email & Final Verification Checklist

**Files:**
- Create: `docs/SUBMISSION_EMAIL.md`
- Reference: `Group Assignment.docx` Section V.4 & Section VI

**Interfaces:**
- Consumes: Repository URL (`https://github.com/verdenef/it120-django.git`), submission guidelines.
- Produces: Turnkey email draft ready for submission to `joshuatubo4@gmail.com`.

- [ ] **Step 1: Create docs/SUBMISSION_EMAIL.md**
  Write the submission email template matching Section V.4:
  - Instructor email: `joshuatubo4@gmail.com`
  - Subject: `Assignment_IT 120-1stSemSY26-27`
  - Pre-filled body with solo contributor breakdown, repository link, placeholder for demonstration video link, and submission checklist confirmation.

- [ ] **Step 2: Run End-to-End Test Suite Verification**
  Run `python manage.py test` to ensure all 81 tests pass.
  Run `git status` to verify clean working tree and untracked files are properly committed or ignored.

- [ ] **Step 3: Commit docs/SUBMISSION_EMAIL.md and Final Verification**
  Commit `docs/SUBMISSION_EMAIL.md` and push to remote repository.

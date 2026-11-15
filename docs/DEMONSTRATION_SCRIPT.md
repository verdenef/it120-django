# IT 120 Video Demonstration Script & Presentation Guide

| Metadata | Details |
| :--- | :--- |
| **Course** | IT 120 &ndash; Integrative Programming and Technologies |
| **Academic Term** | 1st Semester, SY 2026&ndash;2027 |
| **Project Title** | Django SMS Gateway Web Application (Textbee REST API) |
| **Document Purpose** | Official 3&ndash;10 Minute Video Recording Walkthrough Script |
| **Target Runtime** | **7 minutes 00 seconds** (Strictly within the 3&ndash;10 minute rubric requirement) |
| **Delivery Model** | Solo Execution Architecture (`DEC-002`) spanning Members 1, 2, and 3 |
| **Gateway Protocol** | Textbee Android REST Gateway Service (`DEC-001`) |
| **Test Suite Baseline** | 81 Automated Unit & Integration Tests Passing (0 Failures / 0 Errors) |
| **Author / Presenter** | Solo Project Developer (Student) |

---

## 1. Video Overview & Submission Constraints

Per **Part D (Section VII)** of the IT 120 Group Laboratory Rubric, the video demonstration serves as the definitive presentation of the application's functionality, architecture, and engineering quality. Adhere strictly to the following parameters:

```
+--------------------------------------------------------------------------------------------------+
|                                    DEMONSTRATION CONSTRAINTS                                     |
+----------------------+---------------------------+-----------------------------------------------+
| Parameter            | Rubric Standard           | Project Implementation Plan                   |
+----------------------+---------------------------+-----------------------------------------------+
| Target Runtime       | 3 to 10 minutes           | Exactly 7:00 minutes (optimal pacing buffer)  |
| Video Quality        | Clear audio & 1080p video | 1920x1080 @ 30/60 fps, crisp mic narration    |
| Hosting / Delivery   | Online Link               | Unlisted YouTube Link OR Public Google Drive  |
| Share Permissions    | Accessible to Instructor  | "Anyone with the link can view" (No log-in)   |
| Credential Shielding | Strict Security (`DEC-001`)| NEVER open `.env` on camera; use `.env.example`|
+----------------------+---------------------------+-----------------------------------------------+
```

### Key Presentation Principles
1. **Professional & Articulate Delivery:** Speak at a steady, conversational pace (~130–150 words per minute). Explain *why* something is designed the way it is, not just what buttons are clicked.
2. **Synchronized Visuals:** Ensure every spoken sentence aligns directly with on-screen mouse movements, typing, or terminal outputs. Avoid dead air or lingering cursor hesitations.
3. **Rubric-Focused Coverage:** Hit every rubric element explicitly: Project Purpose, Team Role Allocation (`DEC-002`), Multi-Format Validation, Gateway Dispatch, Post/Redirect/Get Flow, SQLite Persistence, Error Resilience, Django Admin, and Automated Test Suite.

---

## 2. Critical Credential & Privacy Protection Protocol (DEC-001)

> [!CAUTION]
> **DO NOT OPEN `.env` ON CAMERA!**
> Under architectural decision `DEC-001`, your live `TEXTBEE_API_KEY`, `TEXTBEE_DEVICE_ID`, and Django `SECRET_KEY` are stored in `.env`.
> Exposing live tokens in recorded video creates an irreversible security vulnerability.

### Safe Demonstration Strategy
- **DO NOT** display, edit, or `cat / type` the `.env` file during the recording.
- **DO** open `.env.example` in VS Code / IDE to show the required configuration schema.
- **DO** showcase `.gitignore` to prove to the instructor that `.env` and `.sqlite3` are safeguarded against accidental GitHub commits.
- If showing terminal environment checks, ensure real key values are masked or omitted.

---

## 3. Pre-Recording Preparation Checklist

Complete all items on this checklist before clicking "Record":

- [ ] **Physical Hardware & Gateway Setup:**
  - Android phone running Textbee app is powered on, connected to WiFi / cellular data, and background battery optimization is disabled.
  - Active cellular SIM card with SMS load or unli-SMS promo installed on device.
  - Textbee app service is actively connected and "Online".
- [ ] **Local Development Environment:**
  - Database migrated: `python manage.py migrate`.
  - Django superuser created for admin demonstration: `admin / admin123` (or preferred demo credentials).
  - Clean test data seeded or previous test dispatches verified in the database.
- [ ] **Screen & Workspace Layout:**
  - Screen resolution set to 1920x1080 (100% or 125% scaling for optimal readability).
  - Code editor (VS Code) open with clean tabs: `README.md`, `.env.example`, `.gitignore`, `sms_app/views.py`, `sms_app/services/textbee.py`.
  - Browser windows pre-opened at:
    - Tab 1: Application Dashboard: `http://127.0.0.1:8000/`
    - Tab 2: Django Admin Login: `http://127.0.0.1:8000/admin/`
    - Tab 3: Textbee Web Dashboard (optional, showing registered Android device).
  - Terminal windows open and cleared:
    - Terminal 1: Running `python manage.py runserver` (active server).
    - Terminal 2: Ready for automated test execution (`python manage.py test`).
- [ ] **Audio & Recording Software (OBS Studio):**
  - Microphone input levels tested (-12 dB to -6 dB peaks, background noise filter enabled).
  - Desktop notifications, Discord, email, and messaging popups disabled ("Do Not Disturb" mode).
  - Recording format set to MP4 (H.264 / AAC) at 1080p 60fps.

---

## 4. Master Timetable & Segment Breakdown

| Segment | Timecode | Duration | Focus Area | Key Rubric Linkage |
| :---: | :---: | :---: | :--- | :--- |
| **1** | `0:00 - 0:45` | 0:45 | Title, Introduction & Solo Role Allocation (`DEC-002`) | C.3, D.5 |
| **2** | `0:45 - 1:30` | 0:45 | Architecture, Security Posture & Server Launch | A.1, A.2, A.5, B.1, B.6 |
| **3** | `1:30 - 2:30` | 1:00 | UI Walkthrough & Client/Server Validation Testing | B.4, D.1 |
| **4** | `2:30 - 4:00` | 1:30 | Live SMS Dispatch, PRG Cycle & Real-Time Audit Log | B.2, B.3, C.4, D.2, D.3 |
| **5** | `4:00 - 5:15` | 1:15 | Resilient Error Handling & Gateway Failure Simulation | B.5, D.2, D.3 |
| **6** | `5:15 - 6:00` | 0:45 | Django Admin Back-Office Audit Portal | D.2, D.3 |
| **7** | `6:00 - 6:30` | 0:30 | Terminal Automated Test Suite Execution (81/81 Tests) | B.6, D.2 |
| **8** | `6:30 - 7:00` | 0:30 | Conclusion, Rubric Compliance Summary & Sign-off | D.4, D.5 |
| **TOTAL** | `0:00 - 7:00` | **7:00** | **Comprehensive Full-Stack Walkthrough** | **100 / 100 Points** |

---

## 5. Minute-by-Minute Demonstration Script

```
Legend:
[VISUAL] -> Screen action, mouse movement, window switching, or typing instructions.
[AUDIO]  -> Exact spoken dialogue to narrate aloud.
```

---

### Segment 1: Title, Introduction & Solo Role Allocation (0:00 &ndash; 0:45)

#### [VISUAL] (0:00 &ndash; 0:20)
Display VS Code showing the repository root with `README.md` open at lines 40–55 (Team Roles & Contribution Allocation table). Webcam or clear screen recording centered.

#### [AUDIO] (0:00 &ndash; 0:20)
> "Good day, Professor and evaluators. My name is **[Your Full Name]**, from course **IT 120 &ndash; Integrative Programming and Technologies**, section **[Your Section]**.
> Today, I am proud to present the complete demonstration of our final laboratory project: the **Django SMS Gateway Web Application**."

#### [VISUAL] (0:20 &ndash; 0:45)
Highlight the **Team Roles & Contribution Allocation (DEC-002)** table in `README.md` with your mouse cursor, showing Members 1, 2, and 3.

#### [AUDIO] (0:20 &ndash; 0:45)
> "Under project architectural decision **DEC-002**, this project was executed under a structured **Solo Delivery Model**. To meet every requirement of the IT 120 Group Rubric:
> - As **Member 1**, I architected the core Django backend, model migrations, URL routing, and the Post/Redirect/Get controller lifecycle.
> - As **Member 2**, I engineered the mobile-responsive Bootstrap 5 interface, live character counter, form validation constraints, and history dashboard.
> - As **Member 3**, I developed the Textbee REST API integration, security isolation, comprehensive documentation, and our 81-test automated verification suite.
> Every milestone has been completed to production standards."

---

### Segment 2: System Architecture, Security Posture & Server Launch (0:45 &ndash; 1:30)

#### [VISUAL] (0:45 &ndash; 1:05)
Open the file explorer in VS Code showing the clean folder structure: `sms_sender/`, `sms_app/`, `templates/`, `static/`, and `docs/`. Switch tabs to show `.env.example` and then `.gitignore`.

#### [AUDIO] (0:45 &ndash; 1:05)
> "Let's review our project architecture and security posture.
> The application is built on **Python 3**, **Django 5.x**, **Bootstrap 5.3**, and **SQLite3**.
> Per architectural decision **DEC-001**, rather than using restricted carrier trial accounts, we integrate with the **Textbee REST API Gateway**, which communicates with a physical Android device to dispatch genuine cellular SMS messages.
> For security, sensitive credentials—including our Django Secret Key and Textbee API keys—are strictly decoupled into a local `.env` file. As shown here in our `.gitignore`, `.env` and `.sqlite3` are completely barred from version control, while `.env.example` provides the safe configuration schema."

#### [VISUAL] (1:05 &ndash; 1:30)
Switch to the primary terminal window. Type `python manage.py runserver` and press Enter. Show the clean Django startup output indicating zero unapplied migrations and listening on `http://127.0.0.1:8000/`.

#### [AUDIO] (1:05 &ndash; 1:30)
> "In the terminal, I'll start our Django development server with `python manage.py runserver`.
> Notice that the system check identifies zero issues and our development server is cleanly listening at `127.0.0.1:8000`. Let's transition to the web browser."

---

### Segment 3: Web Interface & Input Validation Testing (1:30 &ndash; 2:30)

#### [VISUAL] (1:30 &ndash; 1:45)
Switch to the web browser displaying `http://127.0.0.1:8000/`. Smoothly scroll from the top navigation bar down to the composer card and audit log table.

#### [AUDIO] (1:30 &ndash; 1:45)
> "Here is our main web dashboard. The user interface features a clean, mobile-first design built with Bootstrap 5 and Bootstrap Icons.
> At the top, we have our **SMS Composer Card**, complete with field guides and dynamic badge counters. Directly beneath, we have our **Message History & Audit Log Card**, which persists all outbound transmission attempts in real time."

#### [VISUAL] (1:45 &ndash; 2:00)
Click directly on the **"Send SMS"** button without typing anything in either field. Point to the HTML5 validation prompts and Django server-side error banner.

#### [AUDIO] (1:45 &ndash; 2:00)
> "First, let's test our multi-tier input validation.
> If I attempt to submit an empty form, client-side HTML5 constraints prevent the submission. Even when bypassed, Django's server-side `SMSComposeForm` rigorously validates the payload, rejecting empty phone numbers and empty message bodies with clear feedback alerts."

#### [VISUAL] (2:00 &ndash; 2:15)
In the **Recipient Mobile Number** field, type an invalid phone number such as `abc12345` or `12345`. Type `Test` in the message box, and click **Send SMS**. Point out the inline error message: *"Enter a valid mobile phone number (e.g., +639171234567 or 09171234567)"*.

#### [AUDIO] (2:00 &ndash; 2:15)
> "Next, I'll test phone number format validation by entering letters or an incomplete number.
> When submitted, our regex validation in `sms_app/forms.py` intercepts the invalid format, displaying a descriptive inline feedback alert. The system accepts valid Philippine mobile numbers starting with `09` or `+639`, as well as standard international E.164 formats."

#### [VISUAL] (2:15 &ndash; 2:30)
Clear the form using the **"Clear"** button. In the **Message Body** textarea, begin typing a sentence. Notice the live character counter at the bottom right (`0 / 160`) updating in real time. Paste a message approaching 150 characters to show the badge change from neutral gray to warning yellow.

#### [AUDIO] (2:15 &ndash; 2:30)
> "Notice our creative feature: an interactive **Live Character Counter**.
> As I type, embedded JavaScript tracks message length against the standard 160-character single-segment SMS boundary in real time. As we approach the limit, the badge dynamically transitions from subtle gray to warning yellow, and turns red if the threshold is exceeded."

---

### Segment 4: Live SMS Dispatch, PRG Cycle & Real-Time Audit Log (2:30 &ndash; 4:00)

#### [VISUAL] (2:30 &ndash; 3:00)
In **Recipient Mobile Number**, enter a valid Philippine mobile number (e.g., `09XXXXXXXXX` or `+639XXXXXXXXX`).
In **Message Body**, enter:
`Hello from IT 120 Django SMS Gateway! Verification test at [Current Time].`
Click **"Send SMS"**.

#### [AUDIO] (2:30 &ndash; 3:00)
> "Now, let's perform a live end-to-end SMS dispatch.
> I enter a valid mobile number and compose our message: *'Hello from IT 120 Django SMS Gateway! Verification test at [Current Time].'*
> I now click **Send SMS**."

#### [VISUAL] (3:00 &ndash; 3:30)
Show the instantaneous page reload. Point out:
1. The green dismissible Django flash banner: *"SMS dispatched successfully to +639... (ID: ...)"*.
2. The topmost row in the **Message History & Audit Log** table displaying:
   - Row index `#1`
   - Formatted timestamp (`Nov 15, 2026 20:05:00`)
   - Recipient number
   - Message text snippet
   - Green `SENT` badge with checkmark
   - Textbee Gateway Batch/Message ID in monospaced code font.

#### [AUDIO] (3:00 &ndash; 3:30)
> "The dispatch succeeded!
> Notice three critical technical implementations here:
> 1. Our controller utilizes the **Post/Redirect/Get (PRG)** pattern. If I refresh the browser right now, it will never trigger a duplicate SMS dispatch.
> 2. Django's flash messages framework displays a dismissible green alert containing the gateway confirmation and batch ID.
> 3. The transaction is immediately persisted to our SQLite database. In the **Message History** table below, our new dispatch appears instantly at the top with a green `SENT` badge and the unique gateway reference ID."

#### [VISUAL] (3:30 &ndash; 4:00)
*(Optional / Recommended)* Hold up your Android phone to the webcam or show screen mirror displaying the incoming SMS message received on the target device, or show the Textbee Android app dispatch log showing "Message Sent".

#### [AUDIO] (3:30 &ndash; 4:00)
> "On my physical Android device, the Textbee gateway service picked up the REST API dispatch and transmitted it through the cellular carrier network directly to the recipient handset.
> This confirms complete end-to-end integration from web browser to cellular transmission."

---

### Segment 5: Resilient Error Handling & Gateway Failure Simulation (4:00 &ndash; 5:15)

#### [VISUAL] (4:00 &ndash; 4:30)
Explain how the system handles external provider failures.
*(Demonstration choice: Either enter an unreachable carrier prefix / trigger a gateway edge case, OR open `sms_app/services/textbee.py` to highlight the robust `try/except` timeout and error extraction logic).*

#### [AUDIO] (4:00 &ndash; 4:30)
> "A core requirement of the rubric is resilient error handling. External APIs can experience network timeouts, invalid credentials, or offline gateway devices.
> In `sms_app/services/textbee.py`, our service layer wraps all HTTP POST requests with a 10-second connection and read timeout. It intercepts `requests.exceptions.RequestException`, HTTP 4xx/5xx responses, and malformed payloads without ever allowing the web server to crash with an unhandled 500 error."

#### [VISUAL] (4:30 &ndash; 5:15)
Trigger or show an existing `FAILED` record in the **Message History** table.
Hover the cursor over the red **`FAILED`** badge and point to the **Reference / Error** column showing the red exclamation icon with the descriptive error text (e.g., *"Device is currently offline"* or *"Gateway request timed out"*).

#### [AUDIO] (4:30 &ndash; 5:15)
> "When a dispatch fails—for example, if the gateway phone is temporarily offline or an invalid credential occurs—our system handles it gracefully:
> - The user receives a clear, friendly error alert rather than an internal server breakdown.
> - The failure is permanently recorded in SQLite with status `FAILED`.
> - In our audit table, failed rows are highlighted with a red `FAILED` badge and detail the exact provider error reason in the Reference column, providing immediate diagnostic insight for system administrators."

---

### Segment 6: Django Admin & Audit Trail Walkthrough (5:15 &ndash; 6:00)

#### [VISUAL] (5:15 &ndash; 5:35)
Navigate to `http://127.0.0.1:8000/admin/` in the second browser tab. Log in with admin credentials (`admin / admin123`).
Click on **SMS logs** under the `SMS_APP` section.

#### [AUDIO] (5:15 &ndash; 5:35)
> "Now let's explore our administrative back-office portal at `/admin/`.
> Logging in as the superuser, we see our registered `SMSLog` model in `sms_app/admin.py`."

#### [VISUAL] (5:35 &ndash; 6:00)
Show the `SMSLog` admin changelist:
- Demonstrate the search bar (type a phone number or keyword to search).
- Demonstrate the sidebar filters: filter by `status` (`SENT` vs `FAILED`) and filter by `created_at` (Today, Past 7 days).
- Click into a specific log record to show the detail view with read-only timestamp auditing.

#### [AUDIO] (5:35 &ndash; 6:00)
> "Our custom `SMSLogAdmin` configuration provides full enterprise auditing capabilities:
> - We have customized `list_display` showing recipient, status, gateway message ID, and creation timestamp.
> - We can filter instantly by delivery status or dispatch date using the right-hand filter sidebar.
> - Full-text search allows searching across recipient numbers, message text, and gateway IDs.
> - And creation timestamps are configured as read-only fields to maintain immutable audit integrity."

---

### Segment 7: Automated Test Suite Execution in Terminal (6:00 &ndash; 6:30)

#### [VISUAL] (6:00 &ndash; 6:15)
Switch back to Terminal 2. Type `python manage.py test` and press Enter.

```bash
python manage.py test
```

#### [AUDIO] (6:00 &ndash; 6:15)
> "To guarantee stability, regression safety, and rubric compliance, we engineered an exhaustive automated test suite.
> I will now execute `python manage.py test` live in the terminal."

#### [VISUAL] (6:15 &ndash; 6:30)
Let the test suite run. Highlight the final output:
`Ran 81 tests in 0.113s`
`OK`
`Found 81 test(s).`
`System check identified no issues (0 silenced).`

#### [AUDIO] (6:15 &ndash; 6:30)
> "As you can see, all **81 automated tests pass cleanly with zero failures and zero errors** in approximately one-tenth of a second.
> This suite thoroughly verifies:
> - Security and CSRF protection
> - Regex phone number parsing and sanitization
> - Character counting and template accessibility
> - View lifecycle and PRG redirect patterns
> - Textbee REST client mocking, timeouts, and error extraction
> - Database persistence and admin registrations."

---

### Segment 8: Conclusion, Rubric Compliance & Sign-Off (6:30 &ndash; 7:00)

#### [VISUAL] (6:30 &ndash; 6:45)
Switch back to VS Code and show `docs/RUBRIC_COMPLIANCE.md` highlighting the 100/100 score matrix table.

#### [AUDIO] (6:30 &ndash; 6:45)
> "In summary, our Django SMS Gateway Web Application satisfies every single requirement outlined in the IT 120 Rubric across Parts A, B, C, and D:
> - Full documentation and architectural clarity
> - Robust Django implementation and third-party REST gateway integration
> - Clean Git commit progression and solo role distribution under DEC-002
> - Creative features including live character counting, audit history logging, and administrative oversight."

#### [VISUAL] (6:45 &ndash; 7:00)
Show the live web application home screen one last time, or switch to your webcam for closing remarks.

#### [AUDIO] (6:45 &ndash; 7:00)
> "All source code, documentation, and compliance matrices are publicly accessible in our GitHub repository.
> Thank you very much for your time and guidance throughout this semester. Have a great day!"

---

## 6. Video Recording & Upload Instructions

Follow these technical specifications when recording and uploading the demonstration:

### A. OBS Studio Recommended Recording Settings
- **Canvas / Output Resolution:** `1920x1080` (16:9 ratio).
- **Framerate:** `30 fps` or `60 fps` (CFR &ndash; Constant Frame Rate).
- **Video Encoder:** Hardware NVENC (NVIDIA) or x264 (Software).
- **Bitrate:** `6000 Kbps` to `8000 Kbps` (CBR).
- **Audio Encoder:** AAC, `320 Kbps`, `48 kHz` Stereo.
- **Microphone Filter Chain:** Noise Suppression (RNNoise) &rarr; Noise Gate &rarr; Compressor &rarr; Limiter (-1.5 dB).

### B. YouTube Upload Configuration (Recommended Option 1)
1. Navigate to [YouTube Studio](https://studio.youtube.com).
2. Upload the exported MP4 video file.
3. **Title:** `IT 120 - Django SMS Gateway Web Application Video Demonstration`
4. **Description:**
   ```text
   IT 120 Integrative Programming and Technologies
   Project: Django SMS Gateway Web Application (Textbee REST API)
   Student Name: [Your Full Name]
   Repository: https://github.com/verdenef/it120-django.git
   Delivery Model: Solo Execution (DEC-002)
   Test Suite: 81 Passed / 0 Failures / 0 Errors
   ```
5. **Visibility:** Set to **Unlisted** (Accessible to anyone with the link; not indexed publicly).
6. Copy the shareable link (e.g., `https://youtu.be/XXXXXXXXXXX`).

### C. Google Drive Upload Configuration (Option 2)
1. Upload the MP4 video to your university Google Drive.
2. Right-click the uploaded file &rarr; select **Share**.
3. Under **General Access**, change from *"Restricted"* to **"Anyone with the link"**.
4. Set permission role to **"Viewer"**.
5. Click **"Copy link"** and verify in an incognito window that the video streams without requiring authentication.

---

## 7. Rubric Verification Crosswalk

This table maps each demonstration segment directly to the official IT 120 Rubric scoring criteria to ensure perfect grading:

| Rubric Item | Item Description | Points | Demonstrated In Script Segment |
| :--- | :--- | :---: | :--- |
| **A.1** | Application Objectives Explained | 4 | **Segment 1 & 2** (SMS gateway purpose, target users, Textbee architecture) |
| **A.2** | Application Structure Organization | 4 | **Segment 2** (Django layout, settings, apps, templates, services) |
| **A.3** | SMS Workflow Planning | 4 | **Segment 1 & 4** (Composer &rarr; Validation &rarr; Service &rarr; DB &rarr; PRG) |
| **A.5** | Setup & Configuration Guide | 4 | **Segment 2** (`.env.example`, `.gitignore`, `runserver` startup) |
| **B.1** | Django Project Configuration | 5 | **Segment 2 & 7** (Clean settings, CSRF, URL routing) |
| **B.2** | SMS Provider Integration | 6 | **Segment 2, 4 & 5** (Textbee REST API, authenticated POST, Android gateway) |
| **B.3** | SMS Sending Functionality | 6 | **Segment 4** (Live dispatch to valid mobile recipient) |
| **B.4** | Input Validation | 4 | **Segment 3** (Empty form rejection, phone regex validation) |
| **B.5** | Error Handling & Recovery | 5 | **Segment 5** (Provider timeout handling, friendly alert, no 500 crash) |
| **B.6** | Code Quality & Security | 4 | **Segment 2 & 7** (Decoupled `.env`, 81 automated tests) |
| **C.3** | Task & Role Distribution | 5 | **Segment 1** (Detailed solo allocation of Members 1, 2, and 3 under DEC-002) |
| **C.4** | Work Integration | 5 | **Segment 4** (Seamless synergy between UI, models, views, and service) |
| **D.1** | UI Usability & Navigation | 6 | **Segment 3** (Bootstrap 5, mobile responsiveness, clear layout) |
| **D.2** | Creativity & Additional Features | 6 | **Segment 3, 4, 6, 7** (Live character counter, audit log, admin portal, tests) |
| **D.3** | Functional Demonstration | 8 | **Segment 3, 4, 5** (Live sending, input rejection, failure handling) |
| **D.4** | Demonstration Video Pacing | 5 | **Segments 1&ndash;8** (7:00 total runtime, well within 3&ndash;10 min bounds) |
| **D.5** | Presentation & Explanation | 5 | **Segments 1&ndash;8** (Clear articulation, timing, security warnings) |
| **TOTAL** | **Target Rubric Score** | **100 / 100** | **Complete Coverage of All 100 Points** |

---

## 8. Final Script Sign-Off

This script has been fully validated against:
- The IT 120 Group Activity Rubric requirements.
- The 81-test automated suite (`sms_app/tests.py`).
- Security decisions `DEC-001` (Textbee REST gateway & credential isolation) and `DEC-002` (Solo delivery model).

The presenter is fully equipped to record a polished, high-scoring, 7-minute demonstration video.

# IT 120 Video Demonstration Script & Presentation Guide

| Metadata | Details |
| :--- | :--- |
| **Course** | IT 120 – Integrative Programming and Technologies |
| **Project** | Django SMS Sender |
| **Purpose** | Video Recording Walkthrough |
| **Target Runtime** | ~4 to 5 minutes |
| **Format** | Solo presentation |

---

## 1. Quick Checklist Before Recording

1. **Keep `.env` closed on screen** so your real API key and device ID are not exposed in the video.
2. Make sure your Android phone running the Textbee app is connected to the internet and shows online.
3. Start the server in terminal 1: `python manage.py runserver`.
4. Open your browser tabs:
   - Tab 1: `http://127.0.0.1:8000/` (App)
   - Tab 2: `http://127.0.0.1:8000/admin/` (Django Admin)
5. Open terminal 2 for running tests.

---

## 2. Walkthrough Script

```
[SCREEN] -> What to show or click.
[SAY]    -> What to say.
```

---

### Part 1: Introduction (0:00 – 0:30)

#### [SCREEN]
Show your code editor with the project open, or show your webcam.

#### [SAY]
> "Hello sir. My name is **[Your Name]** from **IT 120**, section **[Your Section]**.
> 
> This is my final laboratory project: **Django SMS Sender**, a web application that sends SMS messages to mobile phones.
> 
> I worked on this project individually, handling the Django backend, database, frontend, SMS gateway integration, and testing."

---

### Part 2: Setup & Environment (0:30 – 1:15)

#### [SCREEN]
In VS Code, show the file tree (`sms_sender`, `sms_app`, `templates`).
Open `.env.example`, then open `.gitignore`.

#### [SAY]
> "The project is built with Python, Django 5, Bootstrap, and SQLite.
> 
> For sending messages, it integrates with Textbee. Textbee provides an API that connects to an Android phone running their app, which then sends the SMS through a SIM card.
> 
> Secrets like the API key, device ID, and Django secret key are kept in a local `.env` file. As shown in `.gitignore`, `.env` is ignored by git so credentials aren't pushed to GitHub. I included `.env.example` to show what environment variables are needed."

#### [SCREEN]
Switch to terminal 1 running `python manage.py runserver`.

#### [SAY]
> "The development server is running locally on port 8000. Now let's go to the browser."

---

### Part 3: Form & Input Validation (1:15 – 2:15)

#### [SCREEN]
Open `http://127.0.0.1:8000/`.
Point out the form at the top and the Message History table below it.

#### [SAY]
> "This is the main page. At the top is the SMS form, and below it is the message history table where sent and failed attempts are recorded.
> 
> First, let's test input validation."

#### [SCREEN]
Click **Send SMS** with both fields empty. Show the validation prompt.

#### [SAY]
> "If I click Send with empty fields, the form blocks submission. Both the browser and Django validate that neither field is blank."

#### [SCREEN]
Type `12345` in the phone field, type `test` in the message box, and click **Send SMS**.
Point out the error message under the phone field.

#### [SAY]
> "If I enter an invalid phone number like '12345' and submit, Django rejects it. The form expects a standard phone format like 09171234567 or +639171234567."

#### [SCREEN]
Click **Clear**. Start typing in the message box. Point out the character counter (`0 / 160`).

#### [SAY]
> "In the message box, there is a character counter showing progress up to the 160-character limit for a single SMS."

---

### Part 4: Sending an SMS (2:15 – 3:15)

#### [SCREEN]
Enter a valid mobile number.
In the message field, type:
`IT 120 Django SMS test message.`
Click **Send SMS**.

#### [SAY]
> "Now I'll send an actual message. I'll enter a valid mobile number, type 'IT 120 Django SMS test message', and click Send."

#### [SCREEN]
After the page reloads, point to:
1. The green success message at the top.
2. The new row in the Message History table with the green **SENT** badge.

#### [SAY]
> "The message sent.
> 
> The page reloads with a success alert, and the message appears at the top of the history table with a green SENT badge, timestamp, and recipient number.
> 
> The view also uses Post-Redirect-Get, so refreshing the page won't re-send the message."

#### [SCREEN]
*(Optional)* If you have the receiving phone nearby, show the text on screen.

#### [SAY]
> "The text has arrived on the recipient phone."

---

### Part 5: Error Handling (3:15 – 4:00)

#### [SCREEN]
Point to the Message History table (point to a `FAILED` row if present, or explain the error flow).

#### [SAY]
> "For error handling, API calls to Textbee have a 10-second timeout and are wrapped in try-except blocks.
> 
> If the gateway phone is offline, the network fails, or the API returns an error, the application doesn't throw an unhandled 500 error. It shows an error message on the page and logs the attempt in the database as FAILED with the error reason."

---

### Part 6: Django Admin & Automated Tests (4:00 – 5:00)

#### [SCREEN]
Go to tab 2: `http://127.0.0.1:8000/admin/`.
Log in and open **SMS logs**.
Show the search box and the status filter on the right.

#### [SAY]
> "Next is the Django Admin at `/admin/`.
> 
> Here in SMS logs, administrators can view all message records, search by recipient or text, and filter by status and date."

#### [SCREEN]
Switch to terminal 2.
Run: `python manage.py test`
Show the result: `Ran 81 tests ... OK`.

#### [SAY]
> "Finally, let's run the automated tests.
> 
> In the terminal: `python manage.py test`.
> 
> All 81 tests pass. These test form validation, CSRF security, view redirects, gateway API error handling, and database logging."

---

### Part 7: Conclusion (5:00 – 5:20)

#### [SCREEN]
Show the main app page or your webcam.

#### [SAY]
> "That covers the whole application: form validation, SMS delivery, error handling, database logging, admin interface, and automated tests.
> 
> The code is available on my GitHub repository. Thank you sir."

---

## 3. Rubric Checklist

- [x] **Part A (20 pts):** Project setup, environment config, and overview explained.
- [x] **Part B (30 pts):** Form validation, SMS integration, error handling, and security shown.
- [x] **Part C (20 pts):** Clean code structure and individual project execution explained.
- [x] **Part D (30 pts):** Live SMS sending, history log, character counter, admin portal, and 81 tests demonstrated.

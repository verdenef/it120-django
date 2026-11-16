# IT 120 Video Demonstration Script & Presentation Guide

| Metadata | Details |
| :--- | :--- |
| **Course** | IT 120 – Integrative Programming and Technologies |
| **Project** | Django SMS Gateway Application |
| **Purpose** | 3–10 Minute Video Recording Walkthrough |
| **Target Runtime** | ~5 to 6 minutes (well within the 3–10 minute requirement) |
| **Format** | Solo presentation by student |

---

## 1. Quick Recording Tips & Security Rules

1. **Do not open `.env` on camera.**
   - Your real Textbee API key and device ID are in `.env`.
   - Instead, show `.env.example` and `.gitignore` to show how secrets are protected.
2. **Before hitting Record:**
   - Make sure your Android phone with Textbee is on, connected to the internet, and the Textbee app says connected/online.
   - Run the server in a terminal: `python manage.py runserver`.
   - Have your browser tabs ready:
     - Tab 1: `http://127.0.0.1:8000/` (Main App)
     - Tab 2: `http://127.0.0.1:8000/admin/` (Django Admin)
   - Have a second terminal ready to run the tests (`python manage.py test`).

---

## 2. Walkthrough Script (Step-by-Step)

```
Guide:
[SCREEN] -> What you should click, show, or type on screen.
[SAY]    -> What you say out loud. Keep it conversational and natural.
```

---

### Part 1: Introduction (0:00 – 0:40)

#### [SCREEN]
Show your code editor with the project files open, or have your webcam on.

#### [SAY]
> "Hello sir! My name is **[Your Name]**, from **IT 120**, section **[Your Section]**.
> 
> Today I’m demonstrating my final project: a Django web application that sends real SMS messages to mobile phones.
> 
> Since I worked on this project individually, I handled all parts of development myself: building the Django backend and database, designing the web interface and form validation, integrating the SMS gateway, and writing automated tests to verify everything works properly."

---

### Part 2: Project Setup & Security (0:40 – 1:30)

#### [SCREEN]
In VS Code, show the file list on the left: `sms_sender`, `sms_app`, `templates`, and `manage.py`.
Click open `.env.example`, then click `.gitignore`.

#### [SAY]
> "Here’s how the project is set up:
> 
> The app is built with Python, Django 5, Bootstrap for styling, and SQLite for the database.
> 
> To send actual text messages without paying for expensive carrier accounts, I used Textbee. Textbee provides a REST API that talks to an Android phone running their companion app, which then sends the SMS over a normal cellular network.
> 
> For security, sensitive information like the API key, device ID, and Django secret key are stored in a local `.env` file. You can see here in `.gitignore` that `.env` and the SQLite database are never committed to GitHub. Instead, I provided `.env.example` with blank placeholders so anyone cloning the repo knows what variables to configure."

#### [SCREEN]
Switch to your terminal. Point to the terminal running `python manage.py runserver`.

#### [SAY]
> "The development server is running locally on port 8000 with zero errors, so let's jump over to the browser."

---

### Part 3: Web Interface & Form Validation (1:30 – 2:40)

#### [SCREEN]
Open the browser at `http://127.0.0.1:8000/`.
Scroll down to show the SMS form and the Message History table below it.

#### [SAY]
> "Here is the main dashboard. It's clean and responsive on mobile and desktop.
> 
> At the top is the compose form where you enter the recipient's phone number and the message. Down below is the Message History table, which tracks every text message attempt, whether it succeeded or failed.
> 
> Let's test the input validation."

#### [SCREEN]
Leave both fields empty and click **Send SMS**. Point out the required warnings.

#### [SAY]
> "If I click Send without filling in anything, the browser stops it immediately. Even if someone disables browser validation, Django validates it on the server and displays an error message."

#### [SCREEN]
In the phone number field, type something invalid like `12345` or `abc`. Put `Test` in the message box and click **Send SMS**.
Point out the error: *"Enter a valid mobile phone number (e.g., +639171234567 or 09171234567)"*.

#### [SAY]
> "Now let's try an invalid phone number, like letters or just a few digits. When I click Send, the form rejects it. It specifically looks for standard Philippine mobile numbers starting with 09 or +639, or international numbers in standard format."

#### [SCREEN]
Click the **Clear** button. In the Message field, start typing a sentence. Point to the character counter at the bottom right (`0 / 160`).

#### [SAY]
> "There's also a live character counter at the bottom right of the message box. Standard text messages are 160 characters, so as I type, it updates in real time and warns you if you're getting close to that limit."

---

### Part 4: Sending a Real SMS (2:40 – 4:00)

#### [SCREEN]
Enter your real mobile number (or a test phone you have with you).
In the message body, write:
`Hello from IT 120 Django SMS! Testing at [mention current time].`
Click **Send SMS**.

#### [SAY]
> "Now let's send an actual SMS.
> 
> I'll enter a valid phone number and type: 'Hello from IT 120 Django SMS! Testing now.'
> 
> I'll click Send SMS."

#### [SCREEN]
Wait a second for the page to refresh. Point to:
1. The green alert at the top: *"SMS dispatched successfully..."*
2. The new row in the Message History table with the green **SENT** badge and the timestamp.

#### [SAY]
> "The message was sent successfully!
> 
> Notice a few things:
> First, Django shows a green success banner at the top with the delivery confirmation.
> Second, we're using the standard Post-Redirect-Get pattern, meaning if I refresh the page right now, it won't accidentally send the message twice.
> And third, look at the Message History table below. Our new message was saved directly into SQLite with the recipient, the message snippet, the timestamp, and a green SENT badge."

#### [SCREEN]
*(Optional)* If your phone is beside you, show the received SMS on screen or hold it up to the camera.

#### [SAY]
> "And right here on my phone, the SMS arrived via the cellular network. The connection between Django, the Textbee gateway, and the Android phone is working end-to-end."

---

### Part 5: Error Handling (4:00 – 5:00)

#### [SCREEN]
Point to the Message History table. (If you already have a `FAILED` row from testing, point to it. Or explain what happens when the gateway is offline).
Hover over the red **FAILED** badge or the error text in the table.

#### [SAY]
> "Another important requirement is error handling. External APIs and mobile networks can drop out or time out.
> 
> In the backend code, all requests to Textbee have a 10-second timeout and are wrapped in exception handlers. If the phone is offline, the internet cuts out, or the API returns an error, the website doesn't crash with an ugly 500 error page.
> 
> Instead, it shows a friendly error message to the user and records the attempt as FAILED in the history table, including the exact error message so an administrator can see what went wrong."

---

### Part 6: Django Admin & Automated Tests (5:00 – 6:00)

#### [SCREEN]
Switch to Tab 2: `http://127.0.0.1:8000/admin/`.
Log into the Django Admin. Click on **SMS logs**.
Show the list, search bar, and status filter on the right.

#### [SAY]
> "I also registered the message log model in the Django Admin interface.
> 
> In `/admin/`, administrators can view all sent and failed messages, search by phone number or message text, filter by status or date, and view full details. The timestamps are read-only so the history cannot be tampered with."

#### [SCREEN]
Switch to your second terminal window.
Type `python manage.py test` and press Enter.
Show the output: `Ran 81 tests ... OK`.

#### [SAY]
> "Finally, to make sure everything is stable and reliable, I wrote a comprehensive automated test suite.
> 
> I'll run `python manage.py test`.
> 
> All 81 tests pass in less than a second. These tests cover phone number validation, CSRF security, view redirects, mock gateway API calls and timeouts, and database logging."

---

### Part 7: Conclusion (6:00 – 6:30)

#### [SCREEN]
Switch back to the main app homepage or switch to your webcam.

#### [SAY]
> "To wrap up: the application meets all the project requirements—from form validation and SMS delivery to error handling, database tracking, and thorough testing.
> 
> The complete code and documentation are available on my public GitHub repository.
> 
> Thank you sir for your time and guidance this semester! Have a good day."

---

## 3. Rubric Quick Check (100 / 100 Points Covered)

| Rubric Area | What You Demonstrated |
| :--- | :--- |
| **Part A (20 pts): Requirements & Setup** | Explained project purpose, showed `.env.example`, `.gitignore`, and clean project structure. |
| **Part B (30 pts): Django Code & Validation** | Showed phone validation regex, 160-char counter, PRG pattern, and error recovery without 500 crashes. |
| **Part C (20 pts): Git & Solo Contribution** | Explained solo project execution clearly, showed clean structure and commit-ready code. |
| **Part D (30 pts): Features & Demo** | Demonstrated live SMS dispatch, SMS history audit table, Django Admin search/filters, and 81 passing tests in ~6 minutes. |

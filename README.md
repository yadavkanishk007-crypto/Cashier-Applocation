Flask Money Collection App
--------------------------

Overview
--------
This is a web-based application built with Flask to manage members and their payments
for a money collection system. It supports user authentication, member management,
payment tracking, and automated email notifications.

Features
--------
- User Signup, Login, and Logout with secure password hashing
- Add, view, and delete members
- Add and view payment records linked to members
- Search members and payments
- Send payment confirmation emails
- Send automated payment reminders to unpaid members

Requirements
------------
- Python 3.x
- Flask
- pyodbc
- Flask-Mail
- Werkzeug
- MySQL database with proper schema 

Setup Instructions
------------------
1. Install Python dependencies:
   pip install Flask pyodbc Flask-Mail Werkzeug

2. Prepare the MySQL Database:
   - Confirm the database credentials in app(username, database name , password)
   - Ensure tables: users, members, payments are created.

3. Configure Email:
   - Update the email credentials in app.py (MAIL_USERNAME, MAIL_PASSWORD).
   - The app uses Gmail SMTP with TLS on port 587.

4. Run the application:
   python app.py

5. Access the app:
   Open your web browser and go to:
   http://localhost:5000/

Usage
-----
- Create a user account via the Signup page.
- Log in with your credentials.
- Add members via the dashboard form.
- Record payments linked to members.
- Send payment reminders with one click.
- Delete members if needed.

Security Notes
--------------
- Passwords are hashed securely.
- Sessions protect restricted pages.
- Email credentials are stored in the code; for production, use environment variables.
- Input validation is minimal; use caution with inputs.

Known Limitations
-----------------
- Uses Microsoft Access DB, which may not scale well for many users.
- No pagination on member or payment lists.
- No CSRF protection implemented.
- No password reset feature.

Contact
-------
For questions or improvements, please contact:
Email: ykanishk453@gmail.com

----------------------------------
Thank you for using the Flask Money Collection App!
----------------------------------

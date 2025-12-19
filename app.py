from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import traceback

app = Flask(__name__)
app.secret_key = '8413245853#@8/7qswef4acSaxe@#^8731dwqasfW'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '645a905B'
app.config['MYSQL_DB'] = 'money_collection_db'

def get_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        print("MySQL DB connection successful")
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(f"DB connection failed: {err}")
        return None

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='Admin',
    MAIL_PASSWORD='vtfdydwshfllbouu',
    MAIL_DEFAULT_SENDER='ykanishk453@gmail.com'
)
mail = Mail(app)

def send_email(to, subject, body):
    try:
        msg = Message(subject, recipients=[to])
        msg.body = body
        mail.send(msg)
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email to {to}: {e}")
        print(traceback.format_exc())

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
@login_required
def index():
    search_query = request.args.get('search', '').strip().lower()
    conn = get_connection()
    if not conn:
        flash("Database connection error.")
        return render_template('index.html', members=[], payments=[], search=search_query)

    cur = conn.cursor(dictionary=True)
    try:
        if search_query:
            query = """
                SELECT ID, `Name`, Email, Phone
                FROM members
                WHERE LOWER(`Name`) LIKE %s
            """
            cur.execute(query, (f'%{search_query}%',))
        else:
            cur.execute("SELECT ID, `Name`, Email, Phone FROM members")
        members = cur.fetchall()

        if search_query:
            query = """
                SELECT p.PayID, p.MemberID, m.`Name`, p.`Month`, p.Amount, p.PayDate
                FROM payments AS p
                INNER JOIN members AS m ON p.MemberID = m.ID
                WHERE
                    LOWER(m.`Name`) LIKE %s OR
                    LOWER(p.`Month`) LIKE %s OR
                    CAST(p.Amount AS CHAR) LIKE %s OR
                    YEAR(p.PayDate) LIKE %s
                ORDER BY p.PayDate DESC
            """
            params = (
                f'%{search_query}%',
                f'%{search_query}%',
                f'%{search_query}%',
                f'%{search_query}%'
            )
            cur.execute(query, params)
        else:
            cur.execute("""
                SELECT p.PayID, p.MemberID, m.`Name`, p.`Month`, p.Amount, p.PayDate
                FROM payments AS p
                INNER JOIN members AS m ON p.MemberID = m.ID
                ORDER BY p.PayDate DESC
            """)
        payments = cur.fetchall()

    except Exception as e:
        flash(f"Error loading data: {e}")
        print(traceback.format_exc())
        members, payments = [], []
    finally:
        cur.close()
        conn.close()

    return render_template('index.html', members=members, payments=payments, search=search_query)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for('signup'))

        conn = get_connection()
        if not conn:
            flash("Database connection error.")
            return redirect(url_for('signup'))

        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT ID FROM users WHERE Username = %s", (username,))
            if cur.fetchone():
                flash("Username already taken.")
                return redirect(url_for('signup'))

            hashed_pw = generate_password_hash(password)
            cur.execute("INSERT INTO users (Username, Password) VALUES (%s, %s)", (username, hashed_pw))
            conn.commit()
            flash("Account created! Please log in.")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Signup failed: {e}")
            print(traceback.format_exc())
        finally:
            cur.close()
            conn.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_connection()
        if not conn:
            flash("Database connection error.")
            return redirect(url_for('login'))

        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT ID, Password FROM users WHERE Username = %s", (username,))
            user = cur.fetchone()

            if user and check_password_hash(user['Password'], password):
                session['user_id'] = user['ID']
                session['username'] = username
                flash("Logged in successfully.")
                return redirect(url_for('index'))
            else:
                flash("Invalid username or password.")
        except Exception as e:
            flash(f"Login failed: {e}")
            print(traceback.format_exc())
        finally:
            cur.close()
            conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for('login'))

@app.route('/add_member', methods=['POST'])
@login_required
def add_member():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()

    if not name:
        flash("Name is required.")
        return redirect(url_for('index'))

    conn = get_connection()
    if not conn:
        flash("Database connection error.")
        return redirect(url_for('index'))

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("INSERT INTO members (`Name`, Email, Phone) VALUES (%s, %s, %s)", (name, email, phone))
        conn.commit()
        flash("Member added successfully.")
    except Exception as e:
        flash(f"Failed to add member: {e}")
        print(traceback.format_exc())
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/add_payment', methods=['POST'])
@login_required
def add_payment():
    try:
        member_id = int(request.form['member_id'])
        month = request.form['month'].strip()
        amount = float(request.form['amount'])
    except Exception:
        flash("Invalid payment input.")
        return redirect(url_for('index'))

    conn = get_connection()
    if not conn:
        flash("Database connection error.")
        return redirect(url_for('index'))

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "INSERT INTO payments (MemberID, `Month`, Amount, PayDate) VALUES (%s, %s, %s, %s)",
            (member_id, month, amount, datetime.now())
        )
        conn.commit()

        cur.execute("SELECT `Name`, Email FROM members WHERE ID = %s", (member_id,))
        member = cur.fetchone()
        
        if member and member['Email']:
            subject = "Payment Confirmation"
            body = f"Hi {member['Name']},\n\nWe received your payment of ₹{amount} for {month}.\nThank you!"
            send_email(member['Email'], subject, body)

        flash("Payment recorded successfully.")
    except Exception as e:
        flash(f"Failed to add payment: {e}")
        print(traceback.format_exc())
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('index'))

@app.route('/delete_member/<int:member_id>', methods=['POST'])
@login_required
def delete_member(member_id):
    conn = get_connection()
    if not conn:
        flash("Database connection error.")
        return redirect(url_for('index'))

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("DELETE FROM members WHERE ID = %s", (member_id,))
        conn.commit()
        flash("Member deleted successfully.")
    except Exception as e:
        flash(f"Failed to delete member: {e}")
        print(traceback.format_exc())
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('index'))

@app.route('/send_reminders')
@login_required
def send_reminders():
    conn = get_connection()
    if not conn:
        flash("Database connection error.")
        return redirect(url_for('index'))

    current_month = datetime.now().strftime('%B %Y')
    reminders_sent = 0

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT DISTINCT MemberID FROM payments WHERE `Month` = %s", (current_month,))
        paid_member_ids = {row['MemberID'] for row in cur.fetchall()}

        cur.execute("SELECT ID, `Name`, Email FROM members")
        all_members = cur.fetchall()

        for member in all_members:
            if member['ID'] not in paid_member_ids and member['Email']:
                subject = f"Payment Reminder - {current_month}"
                body = (
                    f"Hi {member['Name']},\n\n"
                    f"This is a auto generated friendly reminder to complete your payment for {current_month}.\n"
                    f"Please ignore if already paid.\n\nThank you!"
                )
                send_email(member['Email'], subject, body)
                reminders_sent += 1

        flash(f"Reminders sent to {reminders_sent} member(s).")
    except Exception as e:
        flash(f"Failed to send reminders: {e}")
        print(traceback.format_exc())
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

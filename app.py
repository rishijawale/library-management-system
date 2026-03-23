from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

# DB Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="library_db"
)
cursor = conn.cursor()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT user_id FROM Users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# ---------------- VIEW BOOKS ----------------
@app.route("/books")
def books():
    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()
    return render_template("books.html", books=books)

# ---------------- ISSUE BOOK ----------------
@app.route("/issue/<int:book_id>")
def issue(book_id):
    user_id = session["user_id"]

    cursor.execute("""
        INSERT INTO Loans (user_id, book_id, issue_date, due_date, status)
        VALUES (%s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'issued')
    """, (user_id, book_id))

    cursor.execute("""
        UPDATE Books SET available_copies = available_copies - 1
        WHERE book_id=%s
    """, (book_id,))

    conn.commit()
    return redirect("/books")

# ---------------- RETURN BOOK ----------------
@app.route("/return/<int:loan_id>")
def return_book(loan_id):
    cursor.execute("SELECT book_id FROM Loans WHERE loan_id=%s", (loan_id,))
    book_id = cursor.fetchone()[0]

    cursor.execute("""
        UPDATE Loans SET return_date=CURDATE(), status='returned'
        WHERE loan_id=%s
    """, (loan_id,))

    cursor.execute("""
        UPDATE Books SET available_copies = available_copies + 1
        WHERE book_id=%s
    """, (book_id,))

    conn.commit()
    return redirect("/dashboard")

# ---------------- OVERDUE ----------------
@app.route("/overdue")
def overdue():
    if "user_id" not in session:
        return redirect("/")

    cursor.execute("""
        SELECT loan_id, user_id, book_id, due_date
        FROM Loans
        WHERE due_date < CURDATE() AND status='issued'
    """)
    
    data = cursor.fetchall()
    return render_template("overdue.html", loans=data)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
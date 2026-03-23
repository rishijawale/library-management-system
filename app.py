from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DB CONNECTION ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT user_id FROM Users WHERE email=? AND password=?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["user_id"]
            return redirect("/dashboard")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# ---------------- VIEW BOOKS ----------------
@app.route("/books")
def books():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()
    conn.close()

    return render_template("books.html", books=books)

# ---------------- ISSUE BOOK ----------------
@app.route("/issue/<int:book_id>")
def issue(book_id):
    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Loans (user_id, book_id, issue_date, due_date, status)
        VALUES (?, ?, DATE('now'), DATE('now', '+7 days'), 'issued')
    """, (user_id, book_id))

    cursor.execute("""
        UPDATE Books 
        SET available_copies = available_copies - 1
        WHERE book_id=?
    """, (book_id,))

    conn.commit()
    conn.close()

    return redirect("/books")

# ---------------- RETURN BOOK ----------------
@app.route("/return/<int:loan_id>")
def return_book(loan_id):
    if "user_id" not in session:
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT book_id FROM Loans WHERE loan_id=?", (loan_id,))
    result = cursor.fetchone()

    if result:
        book_id = result["book_id"]

        cursor.execute("""
            UPDATE Loans 
            SET return_date=DATE('now'), status='returned'
            WHERE loan_id=?
        """, (loan_id,))

        cursor.execute("""
            UPDATE Books 
            SET available_copies = available_copies + 1
            WHERE book_id=?
        """, (book_id,))

        conn.commit()

    conn.close()
    return redirect("/dashboard")

# ---------------- OVERDUE ----------------
@app.route("/overdue")
def overdue():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT loan_id, user_id, book_id, due_date
        FROM Loans
        WHERE due_date < DATE('now') AND status='issued'
    """)

    data = cursor.fetchall()
    conn.close()

    return render_template("overdue.html", loans=data)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
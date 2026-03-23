import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE Books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    available_copies INTEGER
)
""")

cursor.execute("""
CREATE TABLE Loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    book_id INTEGER,
    issue_date TEXT,
    due_date TEXT,
    return_date TEXT,
    status TEXT
)
""")

# sample data
cursor.execute("INSERT INTO Users (email, password) VALUES ('admin@gmail.com', '1234')")
cursor.execute("INSERT INTO Books (title, author, available_copies) VALUES ('Python Basics', 'Rushi', 5)")

conn.commit()
conn.close()

print("Database created successfully ✅")
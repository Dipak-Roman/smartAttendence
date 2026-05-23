from flask import Flask, request, render_template
import sqlite3
-ip------
app = Flask(__name__)

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/register', methods=['POST'])
def register():
    role = request.form['role']
    roll_no = request.form['roll_no']
    password = request.form['password']

    conn = sqlite3.connect("your_database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        roll_no TEXT,
        password TEXT
    )
    """)

    cursor.execute(
        "INSERT INTO users (role, roll_no, password) VALUES (?, ?, ?)",
        (role, roll_no, password)
    )

    conn.commit()
    conn.close()

    return "User Added Successfully"

if __name__ == '__main__':
    app.run(debug=True)

    hii hell
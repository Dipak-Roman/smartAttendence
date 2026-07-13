import cv2
import numpy as np
import face_recognition
import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import cv2
import pickle
import numpy as np
import face_recognition
import subprocess
from datetime import datetime



app = Flask(__name__)
CORS(app)

# ==============================
# Load the trained model (ONLY ONCE)
# ==============================

with open("model/encodings.pkl", "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]




# ---------------- DATABASE ---------------- #

def init_db():
    conn = sqlite3.connect("pucsd.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        class_name TEXT,
        roll TEXT UNIQUE,
        password TEXT
    )
    """)

    # teachers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        roll TEXT UNIQUE,
        password TEXT
    )
    """)

    # lectures table 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lectures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        faculty TEXT,
        subject TEXT,
        start TEXT,
        end TEXT
    )
    """)

    #attendence table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll TEXT NOT NULL,
    lecture_id INTEGER NOT NULL,
    subject TEXT,
    faculty TEXT, 
    time TEXT,
    status TEXT,
    UNIQUE(roll, subject, lecturei_d)
    )
    """)

    conn.commit()
    conn.close()


# ---------------- SIGNUP API ---------------- #

@app.route('/api/signup', methods=['POST'])
def signup():

    data = request.get_json()

    role = data.get('role')
    name = data.get('name')
    email = data.get('email')
    roll = data.get('roll')
    password = data.get('password')

    try:
        conn = sqlite3.connect("pucsd.db")
        cursor = conn.cursor()

        # Check if roll number already exists
        if role == "student":
            std = data.get('std')

            cursor.execute(
                "SELECT * FROM students WHERE roll = ?",
                (roll,)
            )

            existing_user = cursor.fetchone()
            print("user : ", existing_user)


            if existing_user:
                conn.close()
                return jsonify({
                    "success": False,
                    "message": "Roll number already registered"
                }), 400

            else :
                cursor.execute("""
                    INSERT INTO students
                    (name, email, class_name, roll, password)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, email, std, roll, password))

        else:
            cursor.execute(
                "SELECT * FROM teachers WHERE roll = ?",
                (roll,)
            )

            existing_user = cursor.fetchone()
            print("user : ", existing_user)

            if existing_user:
                conn.close()
                return jsonify({
                    "success": False,
                    "message": "Roll number already registered"
                }), 400

            cursor.execute("""
                INSERT INTO teachers
                (name, email, roll, password)
                VALUES (?, ?, ?, ?)
            """, (name, email, roll, password))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "name": name
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
    
@app.route('/api/login', methods=['POST'])
def login():

    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    role = data.get('role')


    conn = sqlite3.connect("pucsd.db")

    cursor = conn.cursor()

    if(role == "student"):
        cursor.execute("""
        SELECT * FROM students
        WHERE roll = ?
        AND password = ?
        """, (username, password))
    else:
        cursor.execute("""
        SELECT * FROM teachers
        WHERE roll = ?
        AND password = ?
        """, (username, password))

    user = cursor.fetchone()

    conn.close()

    if user:
        return jsonify({
            "name": username,
            "message": "Login successful"
        })

    else:
        return jsonify({
            "message": "Invalid Username or Password"
        })


@app.route('/api/addlecture', methods=['POST'])
def addlecture():
    data = request.get_json()
    
    subject = data.get('subject')
    faculty = data.get('faculty')
    start = data.get('start')
    end = data.get('end')

    try:
        conn = sqlite3.connect("pucsd.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO lectures
        (faculty, subject, start, end) 
        VALUES(?, ?, ?, ?) 
        """,(faculty, subject, start, end))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "lecture added successfully"
        })

    except Exception as e:
        return jsonify({
            "message": str(e)
        })
    
@app.route('/api/lectures/<teacher_roll>', methods=['GET'])
def get_teacher_lectures(teacher_roll):

    conn = sqlite3.connect("pucsd.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, subject, faculty, start, end
        FROM lectures
        WHERE faculty = ?
        ORDER BY start
    """, (teacher_roll,))

    lectures = cursor.fetchall()

    conn.close()

    data = []

    for lec in lectures:
        data.append({
            "id": lec[0],
            "subject": lec[1],
            "faculty": lec[2],
            "start": lec[3],
            "end": lec[4]
        })

    return jsonify(data)

@app.route('/api/lectures', methods=['GET'])
def get_lectures():

    conn = sqlite3.connect("pucsd.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, subject, faculty, start, end
        FROM lectures
        ORDER BY start
    """)

    lectures = cursor.fetchall()
    conn.close()

    data = []

    for lec in lectures:
        data.append({
            "id": lec[0],
            "subject": lec[1],
            "faculty": lec[2],
            "start": lec[3],
            "end": lec[4]
        })

    return jsonify(data)

@app.route('/api/deletelecture/<int:id>', methods=['DELETE'])
def delete_lecture(id):

    conn = sqlite3.connect("pucsd.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM lectures WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Lecture deleted"
    })


@app.route("/api/attendance", methods=["POST"])
def mark_attendance():

    data = request.get_json()

    # name = data.get("name")

    roll = data.get("roll")
    lecture_id = data.get("lecture_id")
    subject = data.get("subject")
    faculty = data.get("faculty")

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    conn = sqlite3.connect("pucsd.db")
    cursor = conn.cursor()

    # Prevent duplicate attendance
    cursor.execute("""
        SELECT * FROM attendance
        WHERE roll=?
        AND lecture_id=?
    """,(roll,lecture_id))

    if cursor.fetchone():

        conn.close()

        return jsonify({
            "message":"Attendance already marked"
        })

    cursor.execute("""
        INSERT INTO attendance
        (roll,lecture_id, subject, faculty ,time ,status)

        VALUES(?,?,?,?,?,?)
    """,(roll, lecture_id, subject, faculty, current_time, "Present"))

    conn.commit()
    conn.close()

    return jsonify({
        "message":"Attendance Marked"
    })


@app.route("/api/captureface", methods=["POST"])
def capture_face():

    data = request.get_json()

    roll = data["roll"]

    subprocess.run([
        "python3",
        "capture_faces.py",
        roll
    ])

    return jsonify({
        "message":"Face captured successfully"
    })


from flask import jsonify
import subprocess

@app.route("/api/train", methods=["POST"])
def train_model():

    try:

        result = subprocess.run(
            ["python3", "train_model.py"],
            capture_output=True,
            text=True,
            check=True
        )

        return jsonify({
            "success": True,
            "message": "Model trained successfully!",
            "output": result.stdout
        })

    except subprocess.CalledProcessError as e:

        return jsonify({
            "success": False,
            "error": e.stderr
        }), 500


@app.route("/api/recognize", methods=["POST"])
def recognize():

    if "image" not in request.files:
        return jsonify({
            "success": False,
            "message": "No image received"
        })

    file = request.files["image"]

    image = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(image, cv2.IMREAD_COLOR)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    locations = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, locations)

    if len(encodings) == 0:
        return jsonify({
            "success": False,
            "message": "No face detected"
        })

    face_encoding = encodings[0]

    matches = face_recognition.compare_faces(
        known_encodings,
        face_encoding,
        tolerance=0.5
    )

    distances = face_recognition.face_distance(
        known_encodings,
        face_encoding
    )

    if len(distances) == 0:
        return jsonify({
            "success": False,
            "message": "Unknown student"
        })

    best = np.argmin(distances)

    if not matches[best]:
        return jsonify({
            "success": False,
            "message": "Unknown student"
        })

    roll = known_names[best]

    conn = sqlite3.connect("pucsd.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM students WHERE roll=?",
        (roll,)
    )

    student = cursor.fetchone()

    conn.close()

    if student is None:
        return jsonify({
            "success": False,
            "message": "Student not found"
        })

    return jsonify({
        "success": True,
        "roll": roll,
        "name": student[0]
    })


from datetime import datetime

@app.route("/api/todays_lectures", methods=["GET"])
def todays_lectures():

    current_time = datetime.now().strftime("%H:%M")

    conn = sqlite3.connect("pucsd.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, subject, faculty, start, end
        FROM lectures
        WHERE end >= ?
        ORDER BY start
    """, (current_time,))

    rows = cursor.fetchall()

    conn.close()

    lectures = []

    for row in rows:
        lectures.append({
            "id": row[0],
            "subject": row[1],
            "faculty": row[2],
            "start": row[3],
            "end": row[4]
        })

    return jsonify(lectures)

@app.route("/api/report/<int:lecture_id>", methods=["GET"])
def report(lecture_id):

    conn = sqlite3.connect("pucsd.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            attendance.roll,
            students.name,
            attendance.subject,
            attendance.time,
            attendance.status
        FROM attendance
        JOIN students
        ON attendance.roll = students.roll
        WHERE attendance.lecture_id = ?
        ORDER BY attendance.roll
    """, (lecture_id,))

    rows = cursor.fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])



# ---------------- RUN SERVER ---------------- #

if __name__ == '__main__':
    init_db() 
    app.run(debug=True)
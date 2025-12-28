from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("storage.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    conn = get_db_connection()
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    conn.close()
    return render_template("home.html", total_students=total_students)


@app.route("/students")
def students():
    conn = get_db_connection()
    students = conn.execute("""
        SELECT * FROM students ORDER BY year, department
    """).fetchall()
    conn.close()
    return render_template("students.html", students=students, title="All Students")


@app.route("/students/year/<int:year>")
def students_by_year(year):
    conn = get_db_connection()
    students = conn.execute("""
        SELECT * FROM students WHERE year=?
    """, (year,)).fetchall()
    conn.close()
    return render_template("students.html", students=students, title=f"Year {year}")


@app.route("/students/branch/<branch>")
def students_by_branch(branch):
    conn = get_db_connection()
    students = conn.execute("""
        SELECT * FROM students WHERE department=?
    """, (branch,)).fetchall()
    conn.close()
    return render_template("students.html", students=students, title=f"{branch} Students")


@app.route("/subjects")
def subjects():
    conn = get_db_connection()
    subjects = conn.execute("""
        SELECT subject_name, department, year
        FROM subjects
        ORDER BY department, year
    """).fetchall()
    conn.close()
    return render_template("subjects.html", subjects=subjects)


@app.route("/add-subject", methods=["GET", "POST"])
def add_subject():
    if request.method == "POST":
        subject_id = request.form["subject_id"]
        subject_name = request.form["subject_name"]
        department = request.form["department"]
        year = request.form["year"]

        conn = get_db_connection()

        # insert subject
        conn.execute("""
            INSERT INTO subjects (subject_id, subject_name, department, year)
            VALUES (?, ?, ?, ?)
        """, (subject_id, subject_name, department, year))

        # auto-create marks for existing students
        students = conn.execute("""
            SELECT student_id FROM students
            WHERE department=? AND year=?
        """, (department, year)).fetchall()

        for s in students:
            conn.execute("""
                INSERT INTO marks (student_id, subject_id, marks)
                VALUES (?, ?, NULL)
            """, (s["student_id"], subject_id))

        conn.commit()
        conn.close()
        return redirect(url_for("subjects"))

    return render_template("add_subject.html")

@app.route("/student-summary")
def student_summary():
    conn = get_db_connection()
    data = conn.execute("""
        SELECT
            s.student_name,
            s.department,
            s.year,
            ROUND(AVG(m.marks), 2) AS avg_marks
        FROM students s
        LEFT JOIN marks m ON s.student_id = m.student_id
        GROUP BY s.student_id
        ORDER BY avg_marks DESC
    """).fetchall()
    conn.close()
    return render_template("student_summary.html", data=data)

@app.route("/subject-performance")
def subject_performance():
    conn = get_db_connection()
    data = conn.execute("""
        SELECT
            sub.subject_name,
            sub.department,
            sub.year,
            ROUND(AVG(m.marks), 2) AS avg_marks
        FROM subjects sub
        LEFT JOIN marks m ON sub.subject_id = m.subject_id
        GROUP BY sub.subject_id
        ORDER BY sub.department, sub.year
    """).fetchall()
    conn.close()
    return render_template("subject_performance.html", data=data)


@app.route("/dashboard")
def dashboard():
    conn = get_db_connection()
    data = conn.execute("""
        SELECT
            s.student_name,
            s.department,
            s.year,
            sub.subject_name,
            m.marks
        FROM students s
        JOIN subjects sub
          ON sub.department = s.department AND sub.year = s.year
        LEFT JOIN marks m
          ON m.student_id = s.student_id AND m.subject_id = sub.subject_id
        ORDER BY s.student_name
    """).fetchall()
    conn.close()
    return render_template("dashboard.html", data=data)

@app.route("/manage-marks", methods=["GET", "POST"])
def manage_marks():
    conn = get_db_connection()

    if request.method == "POST":
        student_id = request.form["student_id"]
        subject_id = request.form["subject_id"]
        marks = request.form["marks"]

        # update if exists, else insert
        conn.execute("""
            INSERT INTO marks (student_id, subject_id, marks)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, subject_id)
            DO UPDATE SET marks=excluded.marks
        """, (student_id, subject_id, marks))

        conn.commit()

    students = conn.execute("""
        SELECT student_id, student_name FROM students
        ORDER BY student_name
    """).fetchall()

    subjects = conn.execute("""
        SELECT subject_id, subject_name, department, year FROM subjects
        ORDER BY department, year
    """).fetchall()

    conn.close()
    return render_template(
        "manage_marks.html",
        students=students,
        subjects=subjects
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

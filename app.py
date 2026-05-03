import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from database import init_db, save_attendance, get_report
from face_engine import recognize_faces

app = Flask(__name__)
app.secret_key = "smart_attendance_secret_key_2026"

UPLOAD_FOLDER = os.path.join("static", "uploads")
FACE_DATA_DIR = "face_data"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
LECTURES = ["L1", "L2", "L3", "L4", "L5", "L6"]

# ── Hardcoded admin credentials (change these) ────────────────────────────
ADMIN_ID = "admin"
ADMIN_PASSWORD = "admin123"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ── Login ─────────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        admin_id = request.form.get("admin_id", "").strip()
        password = request.form.get("password", "").strip()

        if admin_id == ADMIN_ID and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            session["admin_id"] = admin_id
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid Admin ID or Password."

    return render_template("login.html", error=error)


# ── Logout ────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── Dashboard ─────────────────────────────────────────────────────────────
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    result = None

    if request.method == "POST":
        lecture = request.form.get("lecture")
        file = request.files.get("group_photo")

        if not lecture or lecture not in LECTURES:
            flash("Please select a valid lecture.", "error")
            return redirect(url_for("dashboard"))

        if not file or file.filename == "":
            flash("Please upload a group photo.", "error")
            return redirect(url_for("dashboard"))

        if not allowed_file(file.filename):
            flash("Only JPG and PNG images are allowed.", "error")
            return redirect(url_for("dashboard"))

        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)

        try:
            present_list, absent_list = recognize_faces(save_path, FACE_DATA_DIR)
            save_attendance(present_list, absent_list, lecture)

            result = {
                "lecture": lecture,
                "total": len(present_list) + len(absent_list),
                "present": present_list,
                "absent": absent_list,
            }
        except Exception as e:
            flash(f"Recognition error: {str(e)}", "error")

    return render_template("dashboard.html", lectures=LECTURES, result=result)


# ── Attendance Report ─────────────────────────────────────────────────────
@app.route("/report")
@login_required
def report():
    report_data = get_report()
    return render_template("report.html", report=report_data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
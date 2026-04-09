# SmartAttend — Face Recognition Attendance System

A Python + Flask web application that marks student attendance automatically from a group photo using AI face recognition.

---

## Project Structure

```
smart_attendance_system/
│
├── app.py                  ← Flask app (routes, login, sessions)
├── face_engine.py          ← Face detection & recognition (InsightFace)
├── database.py             ← Attendance read/write using CSV
├── requirements.txt        ← Python dependencies
├── attendance.csv          ← Auto-created on first run
│
├── face_data/              ← Student photo database
│   ├── Ishank/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   ├── Rahul/
│   │   └── img1.jpg
│   └── (one folder per student)
│
├── static/
│   └── uploads/            ← Uploaded group photos saved here
│
└── templates/
    ├── login.html
    ├── dashboard.html
    └── report.html
```

---

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

> On first run, InsightFace will automatically download the `buffalo_l` model (~300 MB). Make sure you have internet access.

### 2. Add Student Photos

Create one folder per student inside `face_data/`. Add **3–5 clear photos** per student (close-up face, different angles/lighting):

```
face_data/
├── Ishank/
│   ├── img1.jpg
│   ├── img2.jpg
│   └── img3.jpg
└── Rahul/
    ├── img1.jpg
    └── img2.jpg
```

> Folder name = student name that appears in attendance.

### 3. Run the App

```bash
python app.py
```

Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Login Credentials

Default credentials are set in `app.py`:

```python
ADMIN_ID = "admin"
ADMIN_PASSWORD = "admin123"
```

Change these before deploying.

---

## How to Use

1. **Login** with your admin credentials
2. On the **Dashboard**, select a lecture (L1–L6)
3. Upload a group photo of the class
4. Click **Mark Attendance →**
5. The system detects all faces, matches them to registered students, and shows Present / Absent lists
6. Attendance is saved to `attendance.csv`
7. View historical records on the **Attendance Report** page

---

## Key Behaviours

- **Re-marking a lecture**: If you mark attendance for the same lecture on the same day again, the old record is **overwritten** — no duplicates.
- **Attendance CSV**: Stored at `attendance.csv` in the project root. Columns: `date, lecture, student_name, status`
- **Absent list**: Any registered student not detected in the photo is automatically marked Absent.

---

## Technology Stack

| Component | Technology |
|---|---|
| Web Framework | Flask |
| Face Detection | RetinaFace (via InsightFace) |
| Face Recognition | ArcFace — `buffalo_l` model |
| Attendance Storage | CSV (pandas) |
| Frontend | HTML + CSS (no frameworks) |

---

## Tips for Better Recognition

- Use **3–5 registration photos** per student, not just one
- Photos should be well-lit, front-facing close-ups
- For group photos, ensure the room is well-lit
- The system automatically upscales small images for better detection of distant faces
- Recognition threshold is set to `0.4` cosine similarity — increase to `0.45` if you get too many false positives

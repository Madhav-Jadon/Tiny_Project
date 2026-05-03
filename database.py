import os
import pandas as pd
from datetime import date

CSV_PATH = "attendance.csv"
COLUMNS = ["date", "lecture", "student_name", "status"]


def init_db():
    """Create the CSV file with headers if it doesn't exist."""
    if not os.path.exists(CSV_PATH):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_PATH, index=False)


def _load():
    """Load the CSV into a DataFrame."""
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_csv(CSV_PATH)


def save_attendance(present_list, absent_list, lecture):
    """
    Save attendance for a given lecture on today's date.
    If the same lecture was already marked today, it OVERWRITES (no duplicates).
    """
    today = date.today().strftime("%d-%m-%Y")
    df = _load()

    # Remove existing entries for this date + lecture (overwrite behaviour)
    df = df[~((df["date"] == today) & (df["lecture"] == lecture))]

    new_rows = []
    for name in present_list:
        new_rows.append({"date": today, "lecture": lecture, "student_name": name, "status": "Present"})
    for name in absent_list:
        new_rows.append({"date": today, "lecture": lecture, "student_name": name, "status": "Absent"})

    if new_rows:
        new_df = pd.DataFrame(new_rows, columns=COLUMNS)
        df = pd.concat([df, new_df], ignore_index=True)

    df.to_csv(CSV_PATH, index=False)


def get_report():
    """
    Returns attendance grouped by date (newest first),
    with present/absent counts and names per lecture.
    """
    df = _load()
    if df.empty:
        return []

    dates = sorted(df["date"].unique(), reverse=True)

    report = []
    for d in dates:
        day_df = df[df["date"] == d]
        lectures = sorted(day_df["lecture"].unique())

        lecture_data = []
        for lec in lectures:
            lec_df = day_df[day_df["lecture"] == lec]
            present_names = lec_df[lec_df["status"] == "Present"]["student_name"].tolist()
            absent_names  = lec_df[lec_df["status"] == "Absent"]["student_name"].tolist()

            lecture_data.append({
                "lecture":       lec,
                "present":       len(present_names),
                "absent":        len(absent_names),
                "present_names": sorted(present_names),
                "absent_names":  sorted(absent_names),
            })

        report.append({"date": d, "lectures": lecture_data})

    return report
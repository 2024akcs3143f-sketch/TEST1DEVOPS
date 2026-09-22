import json
from datetime import datetime
from pathlib import Path


DATA_FILE = Path(__file__).parent / "attendance_log.json"


def load_data():
    """Load the student and attendance data from the JSON file."""
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"students": [], "attendance": []}

    # Keep the expected lists available if the file has incomplete data.
    data.setdefault("students", [])
    data.setdefault("attendance", [])
    return data


def save_data(data):
    """Save student and attendance data to the JSON file."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def create_student():
    """Ask for student details and add a new student to the roster."""
    name = input("Enter student name: ").strip()
    if not name:
        print("Student name cannot be empty.")
        return

    student_id = input("Enter student ID: ").strip()
    if not student_id:
        print("Student ID cannot be empty.")
        return

    data = load_data()
    for student in data["students"]:
        if student.get("student_id") == student_id:
            print("A student with that ID already exists.")
            return

    data["students"].append({"student_id": student_id, "name": name})
    save_data(data)
    print("Student created successfully.")


def check_in_student():
    """Record today's attendance for a student in the roster."""
    student_id = input("Enter student ID: ").strip()
    if not student_id:
        print("Student ID cannot be empty.")
        return

    data = load_data()
    student = next(
        (item for item in data["students"] if item.get("student_id") == student_id),
        None,
    )
    if student is None:
        print("Student not found.")
        return

    status = input("Enter status (Present or Late): ").strip().lower()
    if status not in ("present", "late"):
        print("Invalid status. Please enter Present or Late.")
        return

    current_time = datetime.now()
    data["attendance"].append(
        {
            "student_id": student["student_id"],
            "name": student["name"],
            "date": current_time.strftime("%Y-%m-%d"),
            "time": current_time.strftime("%H:%M:%S"),
            "status": status.title(),
        }
    )
    save_data(data)
    print("Student checked in successfully.")


def get_today_checkins():
    """Display all attendance records for today's date."""
    today = datetime.now().strftime("%Y-%m-%d")
    data = load_data()
    today_checkins = [
        record for record in data["attendance"] if record.get("date") == today
    ]

    if not today_checkins:
        print("No students have checked in today.")
        return

    print("Today's Check-Ins:")
    for record in today_checkins:
        print(
            f"Student ID: {record.get('student_id', '')} | "
            f"Name: {record.get('name', '')} | "
            f"Status: {record.get('status', '')} | "
            f"Time: {record.get('time', '')}"
        )

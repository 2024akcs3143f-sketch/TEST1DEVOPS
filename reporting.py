from collections import Counter, defaultdict
from datetime import datetime, timedelta

from roster import load_data, save_data


ATTENDED_STATUSES = {"Present", "Late"}


def record_absence(student_id, absence_date=None):
    """Save an absence for a student and return a message for the user."""
    data = load_data()
    student = next(
        (item for item in data["students"] if item.get("student_id") == student_id),
        None,
    )
    if student is None:
        return False, "Student not found."

    absence_date = absence_date or datetime.now().strftime("%Y-%m-%d")
    try:
        datetime.strptime(absence_date, "%Y-%m-%d")
    except ValueError:
        return False, "Invalid date. Please use YYYY-MM-DD."

    already_recorded = any(
        record.get("student_id") == student_id
        and record.get("date") == absence_date
        for record in data["attendance"]
    )
    if already_recorded:
        return False, "Attendance has already been recorded for that student on that date."

    data["attendance"].append(
        {
            "student_id": student["student_id"],
            "name": student["name"],
            "date": absence_date,
            "time": "",
            "status": "Absent",
        }
    )
    save_data(data)
    return True, "Absence recorded successfully."


def mark_student_absent():
    """Ask for a student and date, then record the absence."""
    student_id = input("Enter student ID: ").strip()
    if not student_id:
        print("Student ID cannot be empty.")
        return

    absence_date = input(
        "Enter absence date (YYYY-MM-DD), or press Enter for today: "
    ).strip()
    success, message = record_absence(student_id, absence_date or None)
    print(message)


def get_attendance_rate(student_id, data=None):
    """Return a student's attendance rate as a percentage."""
    data = data or load_data()
    records = [
        record
        for record in data["attendance"]
        if record.get("student_id") == student_id
    ]
    if not records:
        return 0.0

    attended_days = sum(
        record.get("status") in ATTENDED_STATUSES for record in records
    )
    return attended_days / len(records) * 100


def get_chronic_absentees(data=None, threshold=85.0):
    """Return students whose recorded attendance rate is below the threshold."""
    data = data or load_data()
    chronic_absentees = []
    for student in data["students"]:
        rate = get_attendance_rate(student.get("student_id"), data)
        if rate < threshold:
            chronic_absentees.append(
                {
                    "student_id": student.get("student_id", ""),
                    "name": student.get("name", ""),
                    "rate": rate,
                }
            )
    return chronic_absentees


def show_attendance_report():
    """Display attendance rates and students below 85 percent."""
    data = load_data()
    if not data["students"]:
        print("No students have been created yet.")
        return

    print("Attendance Rates:")
    for student in data["students"]:
        rate = get_attendance_rate(student.get("student_id"), data)
        print(
            f"Student ID: {student.get('student_id', '')} | "
            f"Name: {student.get('name', '')} | Attendance Rate: {rate:.2f}%"
        )

    chronic_absentees = get_chronic_absentees(data)
    print("Chronic Absentees (below 85%):")
    if not chronic_absentees:
        print("None")
    else:
        for student in chronic_absentees:
            print(
                f"Student ID: {student['student_id']} | "
                f"Name: {student['name']} | Rate: {student['rate']:.2f}%"
            )


def get_absence_patterns(data=None):
    """Return absence weekdays and consecutive absence streaks by student."""
    data = data or load_data()
    absences_by_student = defaultdict(list)
    for record in data["attendance"]:
        if record.get("status") != "Absent":
            continue
        try:
            absence_date = datetime.strptime(record.get("date", ""), "%Y-%m-%d").date()
        except ValueError:
            continue
        absences_by_student[record.get("student_id")].append(absence_date)

    students_by_id = {
        student.get("student_id"): student for student in data["students"]
    }
    patterns = []
    for student_id, dates in absences_by_student.items():
        dates = sorted(set(dates))
        weekday_counts = Counter(date.strftime("%A") for date in dates)
        streaks = []
        streak_start = dates[0]
        previous_date = dates[0]
        for absence_date in dates[1:]:
            if absence_date != previous_date + timedelta(days=1):
                streaks.append((streak_start, previous_date))
                streak_start = absence_date
            previous_date = absence_date
        streaks.append((streak_start, previous_date))

        patterns.append(
            {
                "student_id": student_id,
                "name": students_by_id.get(student_id, {}).get("name", ""),
                "weekday_counts": dict(weekday_counts),
                "streaks": [
                    {
                        "start": start.strftime("%Y-%m-%d"),
                        "end": end.strftime("%Y-%m-%d"),
                        "length": (end - start).days + 1,
                    }
                    for start, end in streaks
                ],
            }
        )
    return patterns


def show_absence_patterns():
    """Display repeated absence weekdays and consecutive absence streaks."""
    patterns = get_absence_patterns()
    if not patterns:
        print("No absence patterns have been recorded.")
        return

    print("Absence Patterns and Streaks:")
    for pattern in patterns:
        repeated_days = [
            f"{day} ({count})"
            for day, count in pattern["weekday_counts"].items()
            if count > 1
        ]
        repeated_text = ", ".join(repeated_days) if repeated_days else "None"
        print(
            f"Student ID: {pattern['student_id']} | Name: {pattern['name']} | "
            f"Repeated weekdays: {repeated_text}"
        )
        for streak in pattern["streaks"]:
            if streak["length"] > 1:
                print(
                    f"  Absence streak: {streak['start']} to {streak['end']} "
                    f"({streak['length']} days)"
                )
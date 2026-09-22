from roster import create_student, check_in_student, get_today_checkins


def main():
    while True:
        print("\nKAB STUDENT ATTENDANCE REGISTER")
        print("1. Create Student")
        print("2. Check In Student")
        print("3. View Today's Check-Ins")
        print("7. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            create_student()
        elif choice == "2":
            check_in_student()
        elif choice == "3":
            get_today_checkins()
        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Invalid option. Please choose 1, 2, 3, or 7.")


if __name__ == "__main__":
    main()

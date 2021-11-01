import sys
from database import db, models
from template import composer
from pathlib import Path


def verify_signature() -> bool:
    signature_path = 'database/signature.jpg'
    pass


def main():
    if len(sys.argv) < 2:
        print("'help' to get information about how to use this script.")
        return

    command = sys.argv[1]

    if command == 'help':
        print("'run' to use the script.")
        print("'init' to set up the database for the first.")

    elif command == 'init':
        first_name = input("First name: ")
        last_name = input("Last name: ")
        hospital_name = input("Hospital: ")

        user = models.User(first_name=first_name, last_name=last_name, hospital_name=hospital_name)
        db.put_user(user)

    elif command == 'run':
        user = db.get_user()
        if not user:
            print("You have to initialize first with 'init'")
            print("Please put a picture of your signature in the database directory. Saved as 'signature.jpg'")
        else:
            start_date = input("Shift start date in format 'd/m/y': ")
            start_time = input("Shift start time in format 'h:m': ")
            end_date = input("Shift end date in format 'd/m/y': ")
            end_time = input("Shift end time in format 'h:m': ")
            t = models.TimeSheet(user, start_date, start_time, end_date, end_time)
            composer.compose(t)
            print("Composition complete. Html can be found in 'temp.html', pdf can be found in 'out/")

    elif command == 'exit':
        quit()
    elif command == '/s':
        print("Running")
    else:
        print("'help' to get help for the program")


if __name__ == '__main__':
    main()

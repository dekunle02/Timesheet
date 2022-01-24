import sys
import subprocess
from database import db, models
from template import composer
from pathlib import Path

SIGNATURE_DIRECTORY = Path(__file__).parents[0] / 'database' / 'signature.jpg'
COMMANDS = ('init', 'edit', 'view', 'clear', 'run', 'help')
GENERIC_MESSAGE = 'use the "help" command to see how to use this script'
NO_USER_MESSAGE = 'no user information found in the database\nuse the init command to enter user details.'
NO_SIGNATURE_MESSAGE = 'no signature.jpg file found in the database directory\n'
EDIT_MESSAGE = 'Leave blank if you do not wish to modify a field'
HELP_MESSAGE = 'To use this script, run the following commands\n' \
               'init -> to enter your bio data\n' \
               'edit -> edit your given biodata\n' \
               'view -> view your biodata\n' \
               'clear -> clears the database\n' \
               'run -> generate the timesheet\n' \
               '***signature.jpg should be placed in the project database folder***\n' \
               '***ENSURE YOU RUN init the first time you use this script***\n'
DISTURBANCE_PROMPT = 'would you like to add a night disturbance? y or n: \n'
DISTURBANCE_REPEAT_PROMPT = 'would you like to add another night disturbance? y or n: \n'



def main():
    if len(sys.argv) < 2:
        print(GENERIC_MESSAGE)
        return

    command = sys.argv[1]
    if not command in COMMANDS:
        print(GENERIC_MESSAGE)
        return
    elif command == 'help':
        print(HELP_MESSAGE)
        return
    elif command == 'init':
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        hospital_name = input("Hospital: ").strip()
        user = models.User(first_name=first_name, last_name=last_name, hospital_name=hospital_name)
        db.put_user(user)
        print("**saved**")
        return
    user = db.get_user()
    if not db.get_user():
        print(NO_USER_MESSAGE)
        return
    if not SIGNATURE_DIRECTORY.exists():
        print(NO_SIGNATURE_MESSAGE)
        return

    if command == 'edit':
        print(EDIT_MESSAGE)
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        hospital_name = input("Hospital: ").strip()
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if hospital_name:
            user.hospital_name = hospital_name
        db.put_user(user)
        print("**update completed**")
    elif command == 'view':
        print(user.to_dict())
    elif command == 'clear':
        db.drop()
        print('**database dropped**')
    elif command == 'run':
        start_date = input("Shift start date in format 'd/m/y': \n").strip()
        start_time = input("Shift start time in format 'h:m': \n").strip()
        number_of_days = int(input(
            "How many days was your shift (enter a digit, do not include the first day in your count): \n").strip())
        end_time = input("Shift end time in format 'h:m': ").strip()
        t = models.TimeSheet(user, start_date, start_time, number_of_days, end_time)
        disturbance_prompt = input(DISTURBANCE_PROMPT).strip()
        while disturbance_prompt != 'n' and disturbance_prompt == 'y':
            date = input("what is the date ['d/m/y']: \n")
            time = input("what time of the night were you called [hh:mm]: ")
            duration = input("what was the duration: ")
            reason = input("what was the reason: ")
            n = models.NightDisturbance(
                date=date,
                duration=duration,
                reason=reason,
                time=time
            )
            t.add_night_disturbance(n)
            print(DISTURBANCE_REPEAT_PROMPT)
            disturbance_prompt = input().strip()
        composer.produce(timesheet=t)
        subprocess.run(["yarn", "start"])
        print("\n**check the out folder in the project directory for the html and png")
    else:
        print(GENERIC_MESSAGE)


if __name__ == '__main__':
    main()

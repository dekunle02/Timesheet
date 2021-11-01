import json
from pathlib import Path
import os
from database.models import User

DATABASE_FILE_DIRECTORY = Path(__file__).resolve().parents[0] / 'db.json'
USER_KEY = 'user'

DEFAULT_DATA = {
    USER_KEY: {}
}


def get_database() -> dict:
    if not DATABASE_FILE_DIRECTORY.exists():
        with open(DATABASE_FILE_DIRECTORY, 'w+') as f:
            json.dump(DEFAULT_DATA, f)
        return DEFAULT_DATA
    else:
        with open(DATABASE_FILE_DIRECTORY, 'r') as f:
            return json.load(f)


def get_user():
    db: dict = get_database()
    if db.get(USER_KEY):
        user_obj: User = User.from_dict(db.get(USER_KEY))
        return user_obj
    else:
        return None


def put_user(user: User):
    db: dict = get_database()
    db[USER_KEY] = user.to_dict()
    with open(DATABASE_FILE_DIRECTORY, 'w') as f:
        json.dump(db, f)


def drop():
    os.remove(DATABASE_FILE_DIRECTORY)

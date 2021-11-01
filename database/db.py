import json
from pathlib import Path

from database.models import User
from constants import DATABASE_FILE_NAME, USER_KEY


DEFAULT_DATA = {
    USER_KEY: {}
}


def get_database() -> dict:
    db_directory = Path(DATABASE_FILE_NAME)
    if not db_directory.exists():
        with open(DATABASE_FILE_NAME, 'w+') as f:
            json.dump(DEFAULT_DATA, f)
        return DEFAULT_DATA
    else:
        with open(DATABASE_FILE_NAME, 'r') as f:
            return json.load(f)


def get_user() -> User:
    db: dict = get_database()
    try:
        user_obj: User = User.from_dict(db.get(USER_KEY))
        return user_obj
    except:
        return None


def put_user(user: User):
    db: dict = get_database()
    db[USER_KEY] = user.to_dict()
    with open(DATABASE_FILE_NAME, 'w') as f:
        json.dump(db, f)


def modify_user(user: User, **kwargs):
    user_dict: dict = user.to_dict()
    for k in kwargs:
        user_dict[k] = kwargs[k]
    user_obj: User = User.from_dict(user_dict)
    put_user(user_obj)


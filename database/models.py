import json
from datetime import date, datetime
from dataclasses import dataclass


@dataclass
class User:
    first_name: str
    last_name: str
    hospital_name: str

    def __str__(self) -> str:
        return f"Name: {self.first_name} {self.last_name}. Hospital: {self.hospital_name}"

    def to_json(self) -> json:
        return json.dump({
            "first_name": self.first_name,
            "last_name": self.last_name,
            "hospital_name": self.hospital_name
        })

    @classmethod
    def from_json(cls, json_object: json):
        obj_dict: dict = json.loads(json_object)
        return cls(
            first_name=obj_dict.get('first_name'),
            last_name=obj_dict.get('last_name'),
            hospital_name=obj_dict.get('hospital_name')
        )


class NightDisturbance:
    def __init__(self, date, time, duration, reason) -> None:
        self.date = date
        self.time = time
        self.duration = duration
        self.reason = reason


class TimeSheet:
    def __init__(self, user: User, start_time: datetime, end_time: str) -> None:
        self.user = user
        self.start_time = start_time
        self.end_time = end_time
        self.night_disturbances = []



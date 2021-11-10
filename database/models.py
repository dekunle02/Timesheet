import json
import copy
from datetime import date, datetime, timedelta
from dataclasses import dataclass


@dataclass
class User:
    first_name: str
    last_name: str
    hospital_name: str

    def __str__(self) -> str:
        return f"Name: {self.first_name} {self.last_name}. Hospital: {self.hospital_name}"

    def to_dict(self) -> json:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "hospital_name": self.hospital_name
        }

    @classmethod
    def from_dict(cls, obj_dict: dict):
        return cls(
            first_name=obj_dict.get('first_name'),
            last_name=obj_dict.get('last_name'),
            hospital_name=obj_dict.get('hospital_name')
        )


@dataclass
class NightDisturbance:
    date: str
    time: str
    duration: str
    reason: str


class TimeSheet:
    def __init__(self, user: User, start_date: str, start_time: str, number_of_days: int, end_time: str) -> None:
        self.user = user
        self.start_date: datetime = datetime.strptime(start_date, '%d/%m/%Y')
        self.number_of_days: int = number_of_days
        self.start_time: str = start_time
        self.end_time: str = end_time
        self.night_disturbances = []

    def add_night_disturbance(self, disturbance: NightDisturbance) -> None:
        disturbance_dict = {
            'date': disturbance.date,
            'time': disturbance.time,
            'duration': disturbance.duration,
            'reason': disturbance.reason
        }
        self.night_disturbances.append(disturbance_dict)

    def calculate_work_data(self) -> dict:
        work_data = {}
        next_date = copy.deepcopy(self.start_date)
        final_date = self.start_date + timedelta(days=self.number_of_days)

        work_entries = []
        entry_id: int = 1
        while next_date <= final_date:
            row_data = {'id': entry_id, 'date': next_date}
            if next_date == self.start_date:
                row_data['start_time'] = self.start_time
                row_data['end_time'] = '00:00'
                row_data['hours'] = self.calculate_total_hours(_from=self.start_time)
            elif next_date == final_date:
                row_data['start_time'] = '00:00'
                row_data['end_time'] = self.end_time
                row_data['hours'] = self.calculate_total_hours(_to=self.end_time)
            else:
                row_data['start_time'] = '00:00'
                row_data['end_time'] = '00:00'
                row_data['hours'] = 24
            work_entries.append(row_data)
            next_date += timedelta(days=1)
            entry_id += 1
        total_hours = sum([entry['hours'] for entry in work_entries])
        work_data['entries'] = work_entries
        work_data['total_hours'] = total_hours
        return work_data

    @property
    def data(self) -> dict:
        return {
            'bio': self.user.to_dict(),
            'table_data': self.calculate_work_data(),
            'night_disturbances': self.night_disturbances
        }
        pass

    @staticmethod
    def calculate_total_hours(_from: str = '00:00', _to: str = '24:00') -> float:
        hr, min = _from.split(":")
        from_min = int(hr) * 60 + int(min)
        hr, min = _to.split(":")
        to_min = int(hr) * 60 + int(min)
        total_min = to_min - from_min
        return total_min / 60




import json
import typing
import uuid
from datetime import datetime, time, timedelta
from importlib import resources

from dateutil.relativedelta import relativedelta

from . import db_handler


class Period(typing.TypedDict):
    start: datetime
    end: datetime


class Periodicity(typing.TypedDict):
    amount: int
    unit: typing.Literal["days", "weeks", "months", "years"]


PERIODICITY_UNITS = {
    "days": lambda amount=1: timedelta(days=amount),
    "weeks": lambda amount=1: timedelta(weeks=amount),
    "months": lambda amount=1: relativedelta(months=amount),
    "years": lambda amount=1: relativedelta(years=amount),
}


class Habit:
    """
    Class representing a habit

    Attrs:
        uuid (str): unique identifier for the habit
        name (str): name of the habit
        periodicity (Periodicity): length of a period for the habit
        notes (str): optional notes for the habit
        start_date (datetime): date the habit was started; start of the first period

        completed (bool): whether the habit was completed in this period
        streak (int): number of consecutive periods the habit was completed up to now

        periods (list[Period]): historical periods based on periodicity (persisted)
        completions (list[datetime]): completion timestamps (persisted)
    """

    def __init__(
        self,
        habit_uuid: str,
        name: str = "",
        periodicity: Periodicity = {"amount": 1, "unit": "days"},
        notes: str = "",
    ):

        self.uuid: str = habit_uuid
        self.name: str = name
        self.periodicity: Periodicity = periodicity
        self.notes: str = notes

        self.start_date: datetime = datetime.combine(
            now().date(), time.min
        )  # today at 12 am

        self.periods: list[Period] = []
        self.periods.append(self._next_period())

        self.completions: list[datetime] = []

    def update(self, attributes: dict):
        """Update the habit's details"""
        self.name = attributes.get("name") or self.name
        self.periodicity = attributes.get("periodicity") or self.periodicity
        self.notes = attributes.get("notes") or self.notes

    def toggle_completed(self):
        """Mark the habit complete/incomplete for the current period"""
        if not self.completed:
            self.completions.append(now())  # add completion
        else:
            period = self.get_period()
            self.completions = [
                completion
                for completion in self.completions
                if not (period["start"] <= completion < period["end"])
            ]  # remove completions in current period

    def get_completed(self, period: Period = None) -> bool:
        """Return whether the habit was completed in the given period"""
        if period is None:
            period = self.get_period()
        return any(
            period["start"] <= completion < period["end"]
            for completion in self.completions
        )  # any completion in this period

    def get_streak(self, until: datetime = None) -> int:
        """Return the streak up to a given datetime"""
        if until is None:
            until = now()
        periods_sorted = sorted(
            self.periods, key=lambda period: period["start"], reverse=True
        )  # newest to oldest
        streak = 0
        for period in periods_sorted:
            if period["start"] > until:  # skip future periods
                continue
            if (
                period["end"] > until
            ):  # count period containing "until" without breaking streak
                if self.get_completed(period):
                    streak += 1
                continue
            if not self.get_completed(period):  # streak broken
                break
            streak += 1
        return streak

    def get_period(self, at: datetime = None) -> Period:
        """Return the period that contains the given datetime"""
        if at is None:
            at = now()
        while self.periods and self.periods[-1]["end"] <= at:
            self.periods.append(self._next_period())
        for period in self.periods:
            if period["start"] <= at < period["end"]:
                return period
        raise RuntimeError("No period covers the given datetime")

    def _periodicity_delta(self) -> timedelta | relativedelta:
        """Return a timedelta or relativedelta of the habit's periodicity"""
        amount = self.periodicity["amount"]
        unit = self.periodicity["unit"]
        return PERIODICITY_UNITS[unit](amount)

    def _next_period(self) -> Period:
        """Return the next period based on the last period and periodicity"""
        if self.periods:
            start = self.periods[-1]["end"]
        else:
            start = self.start_date
        end = start + self._periodicity_delta()
        return {"start": start, "end": end}

    @property
    def completed(self) -> bool:
        return self.get_completed()

    @property
    def streak(self) -> int:
        return self.get_streak()


class HabitStorage:
    def __init__(self):
        self.habits: dict[str, Habit] = {}

    def get_habit(self, habit_uuid: str) -> Habit | None:
        """Get a habit by UUID"""
        return self.habits.get(habit_uuid)

    def get_habits(self, filter: typing.Callable = None) -> dict[str, Habit]:
        """Get all habits that match a given filter"""
        if filter is None:
            return dict(self.habits)
        return {uuid: habit for uuid, habit in self.habits.items() if filter(habit)}

    def create_habit(self, attributes: dict):
        """Create a new habit with a new UUID"""
        habit_uuid = attributes.get("uuid") or str(uuid.uuid4())
        self.habits[habit_uuid] = Habit(
            habit_uuid,
            attributes.get("name"),
            attributes.get("periodicity"),
            attributes.get("notes"),
        )

    def delete_habit(self, habit_uuid: str):
        """Delete a habit by UUID"""
        self.habits.pop(habit_uuid, None)


HABITS: HabitStorage = HabitStorage()


def load_habits():
    """Load all habits from database"""
    global HABITS
    HABITS = HabitStorage()

    raw = db_handler.load_all()

    for habit_uuid, data in raw.items():
        habit = data["habit"]

        attributes = {
            "uuid": habit_uuid,
            "name": habit["name"],
            "periodicity": {
                "amount": habit["periodicity_amount"],
                "unit": habit["periodicity_unit"],
            },
            "notes": habit["notes"],
        }
        HABITS.create_habit(attributes)

        habit_obj = HABITS.get_habit(habit_uuid)
        habit_obj.start_date = datetime.fromisoformat(habit["start_date"])
        habit_obj.periods = [
            {
                "start": datetime.fromisoformat(period["start"]),
                "end": datetime.fromisoformat(period["end"]),
            }
            for period in data["periods"]
        ]
        habit_obj.completions = [
            datetime.fromisoformat(completion) for completion in data["completions"]
        ]


def save_habits():
    """Save all habits to database"""
    data = {}

    for habit_uuid, habit in HABITS.get_habits().items():
        data[habit_uuid] = {
            "habit": {
                "name": habit.name,
                "periodicity_amount": habit.periodicity["amount"],
                "periodicity_unit": habit.periodicity["unit"],
                "notes": habit.notes,
                "start_date": habit.start_date.isoformat(),
            },
            "periods": [
                {
                    "start": period["start"].isoformat(),
                    "end": period["end"].isoformat(),
                }
                for period in habit.periods
            ],
            "completions": [
                completion.isoformat() for completion in habit.completions
            ],
        }

    db_handler.save_all(data)


def now():
    return datetime.now()


def first_start():
    """Return the start date of the earliest habit"""
    if not HABITS.get_habits():
        return now()
    return min(habit.start_date for habit in HABITS.get_habits().values())


def seed_sample_data(file_path: str = "sample_data.json"):
    file_path = resources.files("habittracker.data").joinpath(file_path)
    with open(file_path, "r") as f:
        default_habits = json.load(f)

    base = now() - timedelta(weeks=4)

    for attributes in default_habits:
        HABITS.create_habit(attributes)
        habit = next(
            h for h in HABITS.get_habits().values() if h.name == attributes["name"]
        )
        habit.start_date = base
        habit.periods = []
        while habit.periods == [] or habit.periods[-1]["end"] < base + timedelta(days=28):
            habit.periods.append(habit._next_period())

        for day_offset in attributes.get("completions", []):
            habit.completions.append(
                habit.start_date + timedelta(days=day_offset, hours=10)
            )

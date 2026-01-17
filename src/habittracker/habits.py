import uuid
import typing
from datetime import datetime, timedelta, time
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
    "years": lambda amount=1: relativedelta(years=amount)
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

        _periods (list[Period]): historical periods based on periodicity (persisted)
        _completions (list[datetime]): completion timestamps (persisted)
    """
    
    def __init__(self,
        habit_uuid: str,
        name: str = "",
        periodicity: Periodicity = {"amount": 1, "unit": "days"},
        notes: str = ""
    ):

        self.uuid: str = habit_uuid
        self.name: str = name
        self.periodicity: Periodicity = periodicity
        self.notes: str = notes

        self.start_date: datetime = datetime.combine(now().date(), time.min)  # today at 12 am

        self._periods: list[Period] = []
        self._periods.append(self._next_period())

        self._completions: list[datetime] = []

    def update(self, attributes: dict):
        """Update the habit's details"""
        self.name = attributes.get("name") or self.name
        self.periodicity = attributes.get("periodicity") or self.periodicity
        self.notes = attributes.get("notes") or self.notes

    def toggle_completed(self):
        """Mark the habit complete/incomplete for the current period"""
        if not self.completed:
            self._completions.append(now())  # add completion
        else:
            period = self.get_period()
            self._completions = [
                completion for completion in self._completions
                if not (period["start"] <= completion < period["end"])
            ]  # remove completions in current period

    def get_completed(self, period: Period = None) -> bool:
        """Return whether the habit was completed in the given period"""
        if period is None: period = self.get_period()
        return any(period["start"] <= completion < period["end"] for completion in self._completions)  # any completion in this period

    def get_streak(self, until: datetime = None) -> int:
        """Return the streak up to a given datetime"""
        if until is None: until = now()
        periods_sorted = sorted(self._periods, key=lambda period: period["start"], reverse=True)  # newest to oldest
        streak = 0
        for period in periods_sorted:
            if period["start"] > until:  # skip future periods
                continue
            if period["end"] > until:  # count period containing "until" without breaking streak
                if self.get_completed(period):
                    streak += 1
                continue
            if not self.get_completed(period):  # streak broken
                break
            streak += 1
        return streak

    def get_period(self, at: datetime = None) -> Period:
        """Return the period that contains the given datetime"""
        if at is None: at = now()
        while self._periods and self._periods[-1]["end"] <= at:
            self._periods.append(self._next_period())
        for period in self._periods:
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
        if self._periods:
            start = self._periods[-1]["end"]
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
        if filter is None: return dict(self.habits)
        return {uuid: habit for uuid, habit in self.habits.items() if filter(habit)}

    def create_habit(self, attributes: dict):
        """Create a new habit with a new UUID"""
        habit_uuid = attributes.get("uuid") or str(uuid.uuid4())
        self.habits[habit_uuid] = Habit(habit_uuid, attributes.get("name"), attributes.get("periodicity"), attributes.get("notes"))

    def delete_habit(self, habit_uuid: str):
        """Delete a habit by UUID"""
        self.habits.pop(habit_uuid, None)

HABITS: HabitStorage = HabitStorage()



def create_default_habits():
    default_habits = [
        {"name": "Exercise", "periodicity": {"amount": 2, "unit": "days"}, "notes": "Go for a run or do a workout"},
        {"name": "Read a book", "periodicity": {"amount": 1, "unit": "weeks"}, "notes": "Finish at least one chapter"},
        {"name": "Meditate", "periodicity": {"amount": 1, "unit": "days"}, "notes": "For at least 10 minutes"},
        {"name": "Write journal", "periodicity": {"amount": 1, "unit": "days"}, "notes": "Reflect on the day's events"},
        {"name": "Practice coding", "periodicity": {"amount": 1, "unit": "days"}, "notes": "Solve at least one coding problem"},
    ]
    for attributes in default_habits:
        HABITS.create_habit(attributes)



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
            "periodicity": {"amount": habit["periodicity_amount"], "unit": habit["periodicity_unit"]},
            "notes": habit["notes"],
        }
        HABITS.create_habit(attributes)

        habit_obj = HABITS.get_habit(habit_uuid)
        habit_obj.start_date = datetime.fromisoformat(habit["start_date"])
        habit_obj._periods = [
            {
                "start": datetime.fromisoformat(period["start"]),
                "end": datetime.fromisoformat(period["end"]),
            }
            for period in data["periods"]
        ]
        habit_obj._completions = [
            datetime.fromisoformat(completion) for completion in data["completions"]
        ]

def save_habits():
    """Save all habits to database"""
    global HABITS
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
                for period in habit._periods
            ],
            "completions": [
                completion.isoformat() for completion in habit._completions
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
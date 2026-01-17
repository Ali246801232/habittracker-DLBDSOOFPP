import pytest
from datetime import datetime

from src.habittracker import habits

@pytest.fixture(autouse=True)
def reset_habits():
    """Reset global HABITS dict before each test to avoid interference."""
    habits.HABITS.habits.clear()
    yield
    habits.HABITS.habits.clear()

def test_create_habit():
    """Test creating a new habit."""
    attributes = {"name": "Exercise", "periodicity": {"amount": 1, "unit": "days"}, "notes": "Daily workout"}
    habits.HABITS.create_habit(attributes)
    assert len(habits.HABITS.habits) == 1
    habit = list(habits.HABITS.habits.values())[0]
    assert habit.name == "Exercise"
    assert habit.periodicity == {"amount": 1, "unit": "days"}
    assert habit.notes == "Daily workout"

def test_toggle_completed_adds_completion(monkeypatch):
    """Test that toggle_completed adds a completion if not already completed."""
    fixed_now = datetime(2023, 1, 1, 12, 0)
    monkeypatch.setattr(habits, 'now', lambda: fixed_now)
    habit = habits.Habit("test-uuid", "Test Habit")
    assert not habit.completed
    habit.toggle_completed()
    assert habit.completed
    assert len(habit._completions) == 1
    assert habit._completions[0] == fixed_now

def test_toggle_completed_removes_if_already_completed():
    """Test that toggle_completed removes completion if already completed."""
    habit = habits.Habit("test-uuid", "Test Habit")
    current_period = habit.get_period()
    completion_time = current_period["start"] + (current_period["end"] - current_period["start"]) / 2
    habit._completions.append(completion_time)
    assert habit.completed
    habit.toggle_completed()
    assert len(habit._completions) == 0

def test_get_streak(monkeypatch):
    """Test streak calculation."""
    fixed_now = datetime(2023, 1, 3, 12, 0)
    monkeypatch.setattr(habits, 'now', lambda: fixed_now)

    habit = habits.Habit("test-uuid", "Test Habit")
    habit._completions = [datetime(2023, 1, 1, 12, 0), datetime(2023, 1, 2, 12, 0)]
    habit._periods = [
        {"start": datetime(2023, 1, 1), "end": datetime(2023, 1, 2)},
        {"start": datetime(2023, 1, 2), "end": datetime(2023, 1, 3)},
        {"start": datetime(2023, 1, 3), "end": datetime(2023, 1, 4)},
    ]
    assert habit.get_streak() == 2

def test_get_period(monkeypatch):
    """Test getting the current period."""
    fixed_now = datetime(2023, 1, 2, 10, 0)
    monkeypatch.setattr(habits, 'now', lambda: fixed_now)
    habit = habits.Habit("test-uuid", "Test Habit")
    period = habit.get_period()
    assert period["start"] == datetime(2023, 1, 2, 0, 0)
    assert period["end"] == datetime(2023, 1, 3, 0, 0)

def test_completion_expires(monkeypatch):
    """Test that completion expires after the period ends."""
    now_1 = datetime(2023, 1, 1, 12, 0)
    now_2 = datetime(2023, 1, 15, 12, 0)
    monkeypatch.setattr(habits, 'now', lambda: now_1)
    habit = habits.Habit("test-uuid", "Test Habit", {"amount": 1, "unit": "weeks"})
    habit.toggle_completed()
    assert habit.completed is True
    assert habit.get_streak() == 1
    monkeypatch.setattr(habits, 'now', lambda: now_2)
    assert habit.completed is False
    assert habit.get_streak() == 0

def test_default_habits_creation():
    """Test creation of default habits."""
    habits.HABITS.habits.clear()
    habits.create_default_habits()
    assert len(habits.HABITS.habits) == 5
    names = [habit.name for habit in habits.HABITS.habits.values()]
    assert "Exercise" in names
    assert "Read a book" in names
    assert "Meditate" in names
    assert "Write journal" in names
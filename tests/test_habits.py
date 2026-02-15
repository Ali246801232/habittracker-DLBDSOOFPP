"""Test habit creation, management, and tracking"""

import pytest
import uuid
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
    habits.seed_sample_data()

    assert len(habits.HABITS.habits) == 5

    habit_by_name = {h.name: h for h in habits.HABITS.habits.values()}
    expected_streaks = {
        "Exercise": 1,
        "Read a book": 0,
        "Meditate": 3,
        "Write journal": 1,
        "Practice coding": 11,
    }
    for name, expected_streak in expected_streaks.items():
        assert name in habit_by_name, f"Missing habit: {name}"
        assert habit_by_name[name].streak == expected_streak

def test_update_habit_name():
    """Test updating a habit's name without affecting other attributes"""
    original_notes = "Original notes"
    original_periodicity = {"amount": 1, "unit": "days"}
    habit = habits.Habit("test-uuid", "Old Name", periodicity=original_periodicity, notes=original_notes)
    habit.update({"name": "New Name"})
    assert habit.name == "New Name"
    assert habit.notes == original_notes
    assert habit.periodicity == original_periodicity

def test_update_habit_notes():
    """Test updating a habit's notes"""
    original_name = "Test Habit"
    habit = habits.Habit("test-uuid", original_name, notes="Old notes")
    habit.update({"notes": "Updated notes"})
    assert habit.notes == "Updated notes"
    assert habit.name == original_name
    """Test updating a habit's periodicity"""
    habit = habits.Habit("test-uuid", "Test", periodicity={"amount": 1, "unit": "days"})
    new_period = {"amount": 2, "unit": "weeks"}
    habit.update({"periodicity": new_period})
    assert habit.periodicity == new_period

def test_update_multiple_attributes():
    """Test updating multiple attributes at once"""
    habit = habits.Habit("test-uuid", "Original", notes="Old notes")
    updates = {
        "name": "Updated",
        "notes": "New notes",
        "periodicity": {"amount": 7, "unit": "days"}
    }
    habit.update(updates)
    assert habit.name == "Updated"
    assert habit.notes == "New notes"
    assert habit.periodicity["amount"] == 7

def test_period_duration_matches_periodicity():
    """Test that period duration matches the specified periodicity"""
    habit = habits.Habit("test-uuid", "Test", periodicity={"amount": 7, "unit": "days"})
    period = habit.get_period()
    duration = period["end"] - period["start"]
    # Should be approximately 7 days
    assert duration.days == 7

def test_habit_name_empty_string():
    """Test creating a habit with empty name"""
    habit = habits.Habit("test-uuid", "")
    assert habit.name == ""

def test_habit_with_very_long_name():
    """Test habit with very long name"""
    long_name = "A" * 1000
    habit = habits.Habit("test-uuid", long_name)
    assert habit.name == long_name
    assert len(habit.name) == 1000

def test_habit_with_special_characters_in_name():
    """Test habit with special characters"""
    special_name = "Habit!@#$%^&*()_+-={}[]|:;<>?,./~`"
    habit = habits.Habit("test-uuid", special_name)
    assert habit.name == special_name

def test_habit_with_unicode_in_name():
    """Test habit with unicode characters"""
    unicode_name = "习惯追踪 🎯 Σ Ω"
    habit = habits.Habit("test-uuid", unicode_name)
    assert habit.name == unicode_name

def test_periodicity_with_large_amounts():
    """Test periodicity with large amount values"""
    period = {"amount": 365, "unit": "days"}
    habit = habits.Habit("test-uuid", "Yearly", periodicity=period)
    assert habit.periodicity["amount"] == 365

def test_habits_have_unique_uuids():
    """Test that habits have unique UUIDs"""
    uuid1 = str(uuid.uuid4())
    uuid2 = str(uuid.uuid4())
    habit1 = habits.Habit(uuid1, "Habit 1")
    habit2 = habits.Habit(uuid2, "Habit 2")
    
    assert habit1.uuid != habit2.uuid
    assert habit1.uuid == uuid1
    assert habit2.uuid == uuid2

def test_uuid_format():
    """Test that UUID is in valid format"""
    test_uuid = str(uuid.uuid4())
    habit = habits.Habit(test_uuid, "Test")
    # Should be valid UUID format
    parsed_uuid = uuid.UUID(habit.uuid)
    assert str(parsed_uuid) == habit.uuid

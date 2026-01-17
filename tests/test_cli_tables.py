import pytest
from unittest.mock import MagicMock

from src.habittracker import habits
from src.habittracker.cli.habit_manager import HabitManager
from src.habittracker.cli.analytics_viewer import AnalyticsViewer


@pytest.fixture(autouse=True)
def app_with_sample_habits(monkeypatch):
    """Add sample habits and mock Application"""
    # prompt_toolkit does not like being in a test environment
    monkeypatch.setattr(
        "src.habittracker.cli.habit_table.Application",
        MagicMock()
    )
    
    # Sample habits
    habits.HABITS.habits.clear()
    habits.HABITS.habits = {
        "uuid1": habits.Habit("uuid1", "Habit One", {"amount": 1, "unit": "days"}, "Notes for habit one"),
        "uuid2": habits.Habit("uuid2", "Habit Two", {"amount": 2, "unit": "weeks"}, "Notes for habit two"),
        "uuid3": habits.Habit("uuid3", "Habit Three but really really really really really really really really really really long", {"amount": 3, "unit": "months"}, "Notes for habit three"),
        "uuid4": habits.Habit("uuid4", "Habit Four", {"amount": 4, "unit": "years"}, "Really really really really really really really really really really really long notes for habit four to test wrapping"),
        "uuid5": habits.Habit("uuid5", "Habit Five", {"amount": 1, "unit": "days"}),
        "uuid6": habits.Habit("uuid6", "Habit Six", {"amount": 1, "unit": "days"}),
        "uuid7": habits.Habit("uuid7", "Habit Seven", {"amount": 1, "unit": "days"}),
    }
    habits.HABITS.habits["uuid1"].toggle_completed()
    habits.HABITS.habits["uuid2"].toggle_completed()

    yield

    habits.HABITS.habits.clear()

def test_display_habit_manager(app_with_sample_habits):
    """Test rendering of HabitManager table with sample habits."""
    app = HabitManager()
    app._reload_table()
    fragments = app._render()
    full_output = "".join([fragment[1] for fragment in fragments])

    # Columns
    assert "Habit" in full_output
    assert "Periodicity" in full_output
    assert "Notes" in full_output
    assert "Completed" in full_output
    assert "Streak" in full_output

    # Habit rows with pagination
    assert "Habit One" in full_output and full_output.count("Habit One") == 1
    assert "Habit Two" in full_output and full_output.count("Habit Two") == 1
    assert "Habit Three" in full_output and full_output.count("Habit Three") == 1
    assert "Habit Four" in full_output and full_output.count("Habit Four") == 1
    assert "Habit Five" not in full_output
    assert "Habit Six" not in full_output
    assert "Habit Seven" not in full_output
    
    # Text wrapping
    assert "really" in full_output \
        and "Really" in full_output \
        and "really really really really really really really really really really" not in full_output

    # Completed status
    assert "[ ]" in full_output and full_output.count("[ ]") == 2
    assert "[X]" in full_output and full_output.count("[X]") == 2

    # Footer
    assert "← Page 1/2 →" in full_output
    assert "[New Habit]" in full_output
    assert "[Quit]" in full_output

def test_display_analytics_viewer(app_with_sample_habits):
    """Test rendering of AnalyticsViewer table with sample habits."""
    app = AnalyticsViewer()
    app._reload_table()
    fragments = app._render()
    full_output = "".join([fragment[1] for fragment in fragments])
    
    # Habit rows with pagination
    assert "Habit One" in full_output and full_output.count("Habit One") == 1
    assert "Habit Two" in full_output and full_output.count("Habit Two") == 1
    assert "Habit Three" in full_output and full_output.count("Habit Three") == 1
    assert "Habit Four" in full_output and full_output.count("Habit Four") == 1
    assert "Habit Five" not in full_output
    assert "Habit Six" not in full_output
    assert "Habit Seven" not in full_output
    
    # Text wrapping
    assert "really" in full_output \
        and "Really" in full_output \
        and "really really really really really really really really really really" not in full_output

    # Columns
    assert "Habit" in full_output
    assert "Periodicity" in full_output
    assert "Notes" in full_output
    assert "Streak" in full_output
    assert "Highest Streak" in full_output
    assert "Completion Rate" in full_output

    # Footer    
    assert "← Page 1/2 →" in full_output
    assert "[Overall Analytics]" in full_output
    assert "[Filter Habits]" in full_output
    assert "[Quit]" in full_output
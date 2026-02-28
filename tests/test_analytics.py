"""Test analytics functions for habits and groups of habits"""

import pytest
from datetime import datetime

from src.habittracker import habits, analytics

@pytest.fixture
def sample_habit():
    """Create a sample habit for testing."""
    habit = habits.Habit("test-uuid", "Test Habit")
    habit.periods = [
        {"start": datetime(2023, 1, 1), "end": datetime(2023, 1, 2)},
        {"start": datetime(2023, 1, 2), "end": datetime(2023, 1, 3)},
        {"start": datetime(2023, 1, 3), "end": datetime(2023, 1, 4)},
    ]
    habit.completions = [datetime(2023, 1, 1, 12, 0), datetime(2023, 1, 2, 12, 0)] 
    return habit

def test_habit_analytics_highest_streak(sample_habit):
    """Test highest streak calculation."""
    analytics_obj = analytics.HabitAnalytics(sample_habit)
    assert analytics_obj.highest_streak() == 2

def test_habit_analytics_completion_rate(sample_habit):
    """Test completion rate calculation."""
    analytics.set_period(datetime(2023, 1, 1), datetime(2023, 1, 4))
    analytics_obj = analytics.HabitAnalytics(sample_habit)
    rate = analytics_obj.completion_rate()
    assert rate == 2 / 3  # 2 completions in 3 periods

def test_group_analytics(sample_habit):
    """Test group analytics with multiple habits."""
    analytics.set_period(datetime(2023, 1, 1), datetime(2023, 1, 4))
    habit2 = habits.Habit("test-uuid2", "Test Habit 2")
    habit2.periods = sample_habit.periods
    habit2.completions = [datetime(2023, 1, 1, 12, 0)] 

    group = analytics.GroupAnalytics([sample_habit, habit2])
    assert group.highest_streak() == 2  # highest streak (2 from sample_habit)
    assert group.completed_periods() == 3  # completed  periods for both habits (2+1)
    assert group.total_periods() == 6  # periods for both habits (3+3)
    avg_rate = group.average_completion_rate()
    assert avg_rate == ((2/3) + (1/3)) / 2  # Average of both habits' rates

def test_analytics_no_completions():
    """Test analytics with a habit that has no completions"""
    habit = habits.Habit("test-uuid", "Never Done")
    habit.periods = [
        {"start": datetime(2023, 1, 1), "end": datetime(2023, 1, 2)},
    ]
    habit.completions = []
    analytics.set_period(datetime(2023, 1, 1), datetime(2023, 1, 2))
    analytics_obj = analytics.HabitAnalytics(habit)
    
    assert analytics_obj.highest_streak() == 0
    assert analytics_obj.completion_rate() == 0.0

def test_analytics_all_periods_completed():
    """Test analytics with all periods completed"""
    habit = habits.Habit("test-uuid", "Always Done", periodicity={"amount": 1, "unit": "days"})
    habit.periods = [
        {"start": datetime(2023, 1, 1), "end": datetime(2023, 1, 2)},
        {"start": datetime(2023, 1, 2), "end": datetime(2023, 1, 3)},
    ]
    habit.completions = [
        datetime(2023, 1, 1, 12, 0),
        datetime(2023, 1, 2, 12, 0),
    ]
    # Set the analytics period to match the test data
    analytics.set_period(datetime(2023, 1, 1), datetime(2023, 1, 3))
    
    analytics_obj = analytics.HabitAnalytics(habit)
    
    assert analytics_obj.highest_streak() == 2
    assert analytics_obj.completion_rate() == 1.0

def test_group_analytics_empty():
    """Test group analytics with no habits"""
    group_analytics = analytics.GroupAnalytics([])
    assert group_analytics.total_periods() == 0
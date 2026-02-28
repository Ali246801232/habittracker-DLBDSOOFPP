from . import habits

SINCE = habits.first_start()
UNTIL = habits.now()


def set_period(since=None, until=None):
    global SINCE, UNTIL
    SINCE = since or habits.first_start()
    UNTIL = until or habits.now()

class HabitAnalytics:
    def __init__(self, habit: habits.Habit):
        self.habit = habit

    def highest_streak(self) -> int:
        """Return the highest streak achieved up for the habit"""
        highest = 0
        current = 0
        streak_valid = False

        for period in sorted(self.habit.periods, key=lambda period: period["start"]):  # oldest to newest
            if period["start"] > UNTIL:  # last relevant period reached
                break

            completed = self.habit.get_completed(period)

            if completed:
                current += 1
                if period["end"] > SINCE:  # exclude streaks ending before "since"
                    streak_valid = True
                if streak_valid:
                    highest = max(highest, current)

            elif period["end"] <= UNTIL:  # only reset if fully before UNTIL
                current = 0
                streak_valid = False

        return highest

    def total_periods(self) -> int:
        """Return the total number of periods for the habit in the set time frame"""
        count = 0
        for period in self.habit.periods:
            if period["end"] < SINCE:
                continue
            if period["start"] > UNTIL:
                break
            count += 1
        return count

    def completed_periods(self) -> int:
        """Return the number of completed periods for the habit in the set time frame"""
        count = 0
        for period in self.habit.periods:
            if period["end"] < SINCE:
                continue
            if period["start"] > UNTIL:
                break
            if self.habit.get_completed(period):
                count += 1
        return count

    def completion_rate(self) -> float:
        """Return the completion rate for the habit in the set time frame"""
        total = self.total_periods()
        if total == 0:
            return 0.0
        completed = self.completed_periods()
        return completed / total


class GroupAnalytics:
    def __init__(self, habits: list[habits.Habit]):
        self.habits = habits

    def highest_streak(self) -> int:
        """Return the highest streak achieved among all habits"""
        highest = 0
        for habit in self.habits:
            habit_analytics = HabitAnalytics(habit)
            highest = max(highest, habit_analytics.highest_streak())
        return highest

    def total_periods(self) -> int:
        """Return the total number of periods among all habits in the set time frame"""
        total = 0
        for habit in self.habits:
            habit_analytics = HabitAnalytics(habit)
            total += habit_analytics.total_periods()
        return total

    def completed_periods(self) -> int:
        """Return the number of completed periods among all habits in the set time frame"""
        completed = 0
        for habit in self.habits:
            habit_analytics = HabitAnalytics(habit)
            completed += habit_analytics.completed_periods()
        return completed

    def average_completion_rate(self) -> float:
        """Return the average completion rate among all habits in the set time frame"""
        if not self.habits:
            return 0.0
        total_rate = 0.0
        for habit in self.habits:
            habit_analytics = HabitAnalytics(habit)
            total_rate += habit_analytics.completion_rate()
        return total_rate / len(self.habits)

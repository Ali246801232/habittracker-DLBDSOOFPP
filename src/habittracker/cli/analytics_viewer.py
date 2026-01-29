from datetime import datetime, time

from prompt_toolkit import HTML
from prompt_toolkit import print_formatted_text as print
from prompt_toolkit import prompt

from .. import analytics, habits
from .habit_table import HabitTable
from .utils import calendar_picker, clear_screen, radio_list


class AnalyticsViewer(HabitTable):
    """Paginated table to view habit anallytics"""

    def __init__(self):
        super().__init__()
        self._ACTIONS = {
            "None": self._action_none,
            "Overall Analytics": self._action_overall_analytics,
            "Filter Habits": self._action_filter_habits,
            "Quit": self._action_quit,
        }
        self._BUTTONS = ["Overall Analytics", "Filter Habits", "Quit"]
        self._ROW_ACTION = "None"
        self._FILTER = None
        self._COLUMNS = {
            "Habit": {
                "width": 20,
                "value": lambda habit: habit.name,
                "align": "left",
            },
            "Notes": {
                "width": 40,
                "value": lambda habit: habit.notes,
                "align": "left",
            },
            "Periodicity": {
                "width": 13,
                "value": lambda habit: f"{habit.periodicity["amount"]} {habit.periodicity["unit"]}",
                "align": "center",
            },
            "Streak": {
                "width": 8,
                "value": lambda habit: str(habit.get_streak(analytics.UNTIL)),
                "align": "center",
            },
            "Highest Streak": {
                "width": 16,
                "value": lambda habit: str(
                    analytics.HabitAnalytics(habit).highest_streak()
                ),
                "align": "center",
            },
            "Completion Rate": {
                "width": 17,
                "value": lambda habit: f"{analytics.HabitAnalytics(habit).completion_rate() * 100:.2f}%",
                "align": "center",
            },
        }
        analytics.set_period()

    def _action_none(self):
        clear_screen()
        return False

    def _action_overall_analytics(self):
        clear_screen()
        group_analytics = analytics.GroupAnalytics(list(self.DATA.values()))
        highest_streak = group_analytics.highest_streak()
        average_completion_rate = group_analytics.average_completion_rate()
        print(HTML("<b>Overall Analytics:</b>"))
        print(HTML(f"  <b>Highest Streak Among All Habits:</b> {highest_streak}"))
        print(
            HTML(
                f"  <b>Average Completion Rate:</b> {average_completion_rate * 100:.2f}%"
            )
        )
        print()
        input("Press Enter to return to the table.")
        clear_screen()
        return False

    def _action_filter_habits(self):
        clear_screen()
        print("Filter by:")
        choice = radio_list(["Periodicity", "Date", "Remove Filters", "Back"])

        clear_screen()

        match choice:
            case "Periodicity":
                print(HTML("<b>Period unit:</b>"))
                periodicity_unit = radio_list(list(habits.PERIODICITY_UNITS.keys()))
                while True:
                    count_input = prompt(
                        HTML("<b>Period count:</b> "), default="1"
                    ).strip()
                    if not count_input:
                        periodicity_amount = 1
                        break
                    if count_input.isdigit() and int(count_input) > 0:
                        periodicity_amount = int(count_input)
                        break
                    print("Please enter a positive integer.")

                self._FILTER = lambda habit: habit.periodicity == {
                    "amount": periodicity_amount,
                    "unit": periodicity_unit,
                }

            case "Date":
                print(HTML("<b>Start date:</b>"))
                analytics.SINCE = datetime.combine(
                    calendar_picker(
                        min_date=habits.first_start().date(),
                        max_date=habits.now().date(),
                    ),
                    time.min,
                )
                print("")
                print(HTML("<b>End date:</b>"))
                analytics.UNTIL = datetime.combine(
                    calendar_picker(
                        min_date=habits.first_start().date(),
                        max_date=habits.now().date(),
                    ),
                    time.max,
                )

            case "Remove Filters":
                self._FILTER = None
                analytics.SINCE = habits.first_start()
                analytics.UNTIL = habits.now()

            case "Back":
                return False

        clear_screen()

    def _action_quit(self):
        return True

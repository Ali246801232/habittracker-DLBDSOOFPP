from prompt_toolkit import prompt, HTML, print_formatted_text as print

from .. import habits
from .cli_utils import radio_list, clear_screen
from .habit_table import HabitTable

class HabitManager(HabitTable):
    """Paginated table to display and manage habits"""

    def __init__(self):
        super().__init__()
        self._ACTIONS = {
            "Edit Habit": self._action_edit_habit,
            "New Habit": self._action_new_habit,
            "Quit": self._action_quit
        }
        self._ROW_ACTION = "Edit Habit"
        self._BUTTONS = ["New Habit", "Quit"]
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
            "Completed": {
                "width": 11,
                "value": lambda habit: "[X]" if habit.completed else "[ ]",
                "align": "center",
            },
            "Streak": {
                "width": 8,
                "value": lambda habit: str(habit.streak),
                "align": "center",
            },
        }


    def _action_edit_habit(self):
        habit = self._get_selected_habit()
        editor = HabitEditor(habit)
        editor.run()
        return False

    def _action_new_habit(self):
        editor = HabitEditor()
        editor.run()
        return False
    
    def _action_quit(self):
        return True


class HabitEditor:
    """Interface to edit an existing habit or create a new one"""

    def __init__(self, habit: habits.Habit = None):
        self.habit = habit

    def run(self):
        if self.habit is None:
            self._create_habit()
        else:
            self._edit_habit()
        clear_screen()

    def _create_habit(self):
        """Create a new habit"""
        attributes = self._input_habit_details()
        habits.HABITS.create_habit(attributes)
        habits.save_habits()

    def _edit_habit(self):
        """Edit an existing habit"""
        while True:
            if self.habit is None:
                return

            options = [
                ("Mark complete" if not self.habit.completed else "Mark incomplete"),
                "Edit habit",
                "Delete habit",
                "Back",
            ]

            clear_screen()
            print("Select an action for the habit:")
            choice = radio_list(options)
            clear_screen()
            
            match choice:
                case "Mark complete" | "Mark incomplete":
                    self.habit.toggle_completed()
                    habits.save_habits()

                case "Edit habit":
                    attributes = self._input_habit_details()
                    self.habit.update(attributes)
                    habits.save_habits()

                case "Delete habit":
                    print("Are you sure you want to delete this habit?")
                    if radio_list(["Yes", "No"]) == "Yes":
                        habits.HABITS.delete_habit(self.habit.uuid)
                        habits.save_habits()
                        return

                case "Back":
                    habits.save_habits()
                    return


    def _input_habit_details(self):
        """Input and return habit details"""
        # Defaults
        if self.habit:
            defaults = {
                "name": self.habit.name,
                "periodicity": self.habit.periodicity,
                "notes": self.habit.notes
            }
        else:
            defaults = {
                "name": "",
                "periodicity": {"amount": 1, "unit": "days"},
                "notes": ""
            }

        while True:
            clear_screen()
            
            # Name
            name = prompt(HTML("<b>Habit Name:</b> "), default=defaults["name"]).strip() or defaults["name"]

            # Period unit
            print(HTML("<b>Period unit:</b>"))
            periodicity_unit = radio_list(list(habits.PERIODICITY_UNITS.keys()), default=defaults["periodicity"]["unit"])

            # Period count
            while True:
                count_input = prompt(HTML(f"<b>Period count:</b> "), default=str(defaults["periodicity"]["amount"])).strip()
                if not count_input:
                    periodicity_amount = defaults["periodicity"]["amount"]
                    break
                try:
                    periodicity_amount = int(count_input)
                    if periodicity_amount > 0:
                        break
                    else:
                        print("Please enter a positive integer.")
                except ValueError:
                    print("Please enter a valid integer.")

            # Notes
            notes = prompt(HTML("<b>Notes:</b> "), default=defaults["notes"]).strip() or defaults["notes"]

            # Confirm details and return
            print(HTML(f"<b>Habit</b>: {name}"))
            print(HTML(f"<b>Notes</b>: {notes}"))
            print(HTML(f"<b>Periodicity</b>: Every {periodicity_amount} {periodicity_unit}"))
            print("Are these details correct?")
            if radio_list(["Yes", "No"]) == "Yes":
                return {
                    "name": name,
                    "periodicity": {"amount": periodicity_amount, "unit": periodicity_unit},
                    "notes": notes
                }
            else:
                if self.habit:
                    return defaults
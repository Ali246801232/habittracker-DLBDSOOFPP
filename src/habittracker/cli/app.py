from importlib import resources

from prompt_toolkit import HTML
from prompt_toolkit import print_formatted_text as print

from .. import __version__ as VERSION
from .analytics_viewer import AnalyticsViewer
from .habit_manager import HabitManager
from .utils import clear_screen, radio_list

GITHUB_REPO = "Ali246801232/habittracker-DLBDSOOFPP"


class HabitTrackerApp:
    def run(self):
        clear_screen()
        choice = ""
        while choice != "Quit":
            choice = self._display_menu()
            clear_screen()
            match choice:
                case "Habits":
                    self._habit_manager()
                case "Analytics":
                    self._analytics_viewer()
                case "Help":
                    self._help()
            clear_screen()

    def _display_menu(self):
        """Display main menu"""
        options = ["Habits", "Analytics", "Help", "Quit"]

        print(HTML(f"Welcome to <b>Habit Tracker</b> v{VERSION}!"))
        print("\nPlease select an option:")
        choice = radio_list(options)

        return choice

    def _habit_manager(self):
        """Start the habit manager"""
        HabitManager().run()

    def _analytics_viewer(self):
        """Start the analytics viewer"""
        AnalyticsViewer().run()

    def _help(self):
        """Display help information"""
        try:
            help_path = resources.files("habittracker.data").joinpath("help.txt")
            with open(help_path, "r") as f:
                print(HTML(f.read()))
        except FileNotFoundError:
            print("Help file not found.")
        input("\nPress Enter to return to the menu.")
        clear_screen()

from .habits import load_habits, create_default_habits
from .db_handler import initialize_database, is_first_run
from .cli.app import HabitTrackerApp

def main():
    initialize_database()
    load_habits()
    if is_first_run():
        create_default_habits()
    cli_app = HabitTrackerApp()
    cli_app.run()
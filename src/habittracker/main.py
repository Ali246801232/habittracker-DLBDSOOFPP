from .habits import load_habits, seed_sample_data
from .db_handler import initialize_database, is_first_run
from .cli.app import HabitTrackerApp

def main():
    initialize_database()
    load_habits()
    if is_first_run():
        seed_sample_data()
    cli_app = HabitTrackerApp()
    cli_app.run()
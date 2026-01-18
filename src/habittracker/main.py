from .cli.app import HabitTrackerApp
from .db_handler import initialize_database, is_first_run
from .habits import load_habits, seed_sample_data


def main():
    initialize_database()
    load_habits()
    if is_first_run():
        seed_sample_data()
    cli_app = HabitTrackerApp()
    cli_app.run()

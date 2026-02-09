from .cli.app import HabitTrackerApp
from .db_handler import initialize_database, is_first_run, set_db_path
from .habits import load_habits, seed_sample_data


def main():
    set_db_path()

    first_run = is_first_run()

    initialize_database()
    load_habits()

    if first_run:
        seed_sample_data()

    cli_app = HabitTrackerApp()
    cli_app.run()

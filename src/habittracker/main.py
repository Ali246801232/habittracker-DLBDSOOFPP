from .cli.app import HabitTrackerApp
from .db_handler import initialize_database, is_first_run, set_db_path
from .habits import load_habits, seed_sample_data

import argparse
from . import test_harness

def main():
    parser = argparse.ArgumentParser(prog="habittracker")
    parser.add_argument(
        "-m",
        "--manual-test",
        dest="manual",
        action="store_true",
        help="launch the manual testing harness instead of the normal app",
    )
    args = parser.parse_args()

    if args.manual:
        test_harness.run()
        return

    set_db_path()

    first_run = is_first_run()

    initialize_database()
    load_habits()

    if first_run:
        seed_sample_data()

    cli_app = HabitTrackerApp()
    cli_app.run()

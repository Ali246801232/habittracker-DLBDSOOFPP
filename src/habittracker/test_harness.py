import os
import tempfile
from datetime import datetime, date, timedelta

from . import habits
from .db_handler import initialize_database, set_db_path
from .habits import load_habits
from .cli.app import HabitTrackerApp
from .cli.utils import clear_screen, radio_list, calendar_picker


def run():
    # create temporary database file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmp_path = tmp.name
    tmp.close()
    set_db_path(tmp_path)
    initialize_database()
    first_run = True

    # track offset
    base_real_date = datetime.now().date()
    fake_today: date = base_real_date
    original_now = habits.now
    def fake_now():
        if fake_today is None:
            return datetime.now()
        return datetime.combine(fake_today, datetime.now().time())
    habits.now = fake_now

    # main menu
    try:
        while True:
            print(f"Now: {habits.now().date()}")
            choice = radio_list(["Run App", "Change Date", "Reset Database", "Exit"])
            clear_screen()

            if choice == "Exit":
                break

            elif choice == "Run App":
                initialize_database()
                load_habits()
                if first_run:
                    habits.seed_sample_data()
                    first_run = False
                HabitTrackerApp().run()

            elif choice == "Change Date":
                print("Select new current date:")
                new_date = calendar_picker(
                    default=fake_today or base_real_date,
                    min_date=habits.first_start().date(),
                    max_date=date.max,
                )
                if new_date:
                    fake_today = new_date

            elif choice == "Reset Database":
                try:
                    os.remove(tmp_path)
                except FileNotFoundError:
                    pass
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
                tmp_path = tmp.name
                tmp.close()
                set_db_path(tmp_path)

            clear_screen()

    # reset state on exit or error
    finally:
        habits.now = original_now
        try:
            os.remove(tmp_path)
        except Exception:
            pass
# HabitTracker

A Python-based CLI habit tracking app to create, track, and analyze habits over time. 

## Quick Start

1. Install Python 3.9+ from [the official website](https://www.python.org/downloads/).

2. Clone the repository:
    ```ps
    git clone https://github.com/Ali246801232/habittracker-DLBDSOOFPP.git habittracker
    cd habittracker
    ```

3. Set up a virtual environment (optional but recommended):
    ```ps
    python -m venv venv
    .\venv\Scripts\activate
    ```

4. Install the app as a package:
    ```ps
    pip install .
    ```

5. Run HabitTracker:
    ```ps
    habittracker
    ```

## Usage

Upon launching the app, you will see the main menu:
```
Welcome to Habit Tracker v0.0.1!

Please select an option:
● Habits
○ Analytics
○ Help
○ Quit
```

---

Selecting `Habits` will open a table interface to view and manage your habits, similar to the following:
```
   ┏━━━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━┯━━━━━━━━━━━┯━━━━━━━━┓
   ┃       Habit        │                 Notes                  │ Periodicity │ Completed │ Streak ┃
   ┣━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━┿━━━━━━━━━━━┿━━━━━━━━┫
>> ┃ Exercise           │ Go for a run or do a workout           │    2 days   │    [ ]    │   1    ┃ <<
   ┠────────────────────┼────────────────────────────────────────┼─────────────┼───────────┼────────┨
   ┃ Read a book        │ Finish at least one chapter            │   1 weeks   │    [ ]    │   1    ┃
   ┠────────────────────┼────────────────────────────────────────┼─────────────┼───────────┼────────┨
   ┃ Meditate           │ For at least 10 minutes                │    1 days   │    [ ]    │   0    ┃
   ┠────────────────────┼────────────────────────────────────────┼─────────────┼───────────┼────────┨
   ┃ Write journal      │ Reflect on the day's events            │    1 days   │    [ ]    │   0    ┃
   ┗━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━┷━━━━━━━━━━━┷━━━━━━━━┛
   ← Page 1/2 →                                                                  [New Habit]    [Quit]
```

Then, to interact with the table, you can:
- Create a new habit by pressing the `New Habit` button.
- Press ENTER with a habit selected to mark it complete/incomplete, modify it, or delete it.
- Return to the main menu by pressing the `Quit` button.

---

Selecting `Analytics` will open a table interface, similar to the following:
```
   ┏━━━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━┯━━━━━━━━┯━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━┓
   ┃       Habit        │                 Notes                  │ Periodicity │ Streak │ Highest Streak │ Completion Rate ┃
   ┣━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━┿━━━━━━━━┿━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━┫
>> ┃ Exercise           │ Go for a run or do a workout           │    2 days   │   1    │       1        │     100.00%     ┃ <<
   ┠────────────────────┼────────────────────────────────────────┼─────────────┼────────┼────────────────┼─────────────────┨
   ┃ Read a book        │ Finish at least one chapter            │   1 weeks   │   1    │       1        │     100.00%     ┃
   ┠────────────────────┼────────────────────────────────────────┼─────────────┼────────┼────────────────┼─────────────────┨
   ┃ Meditate           │ For at least 10 minutes                │    1 days   │   0    │       0        │      0.00%      ┃
   ┠────────────────────┼────────────────────────────────────────┼─────────────┼────────┼────────────────┼─────────────────┨
   ┃ Write journal      │ Reflect on the day's events            │    1 days   │   0    │       0        │      0.00%      ┃
   ┗━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━┷━━━━━━━━┷━━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━┛
   ← Page 1/2 →                                                             [Overall Analytics]    [Filter Habits]    [Quit]
```

Then, to interact with the table, you can:
- View the analytics of all habits within the filter by pressing `Overall Analytics`.
- Filter habits by pressing `Filter Habits` (by periodicity or dates).
- Return to the main menu by pressing `Quit`.

---

Selecting `Help` will display a summarized version of instructions.

Selecting `Quit` will exit the app.

## Example Workflow

import calendar
import os
from datetime import date, timedelta

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def radio_list(options: list, default=None):
    """Display an inline radio list with the given options and return the selected option"""
    if default is not None and default in options:
        selected_index = options.index(default)
    else:
        selected_index = 0

    def get_menu_text():
        lines = []
        for i, option in enumerate(options):
            prefix = "● " if i == selected_index else "○ "
            lines.append(prefix + option)
        return "\n".join(lines)

    kb = KeyBindings()

    @kb.add("up")
    def move_up(event):
        nonlocal selected_index
        selected_index = (selected_index - 1) % len(options)
        window.content.text = get_menu_text()

    @kb.add("down")
    def move_down(event):
        nonlocal selected_index
        selected_index = (selected_index + 1) % len(options)
        window.content.text = get_menu_text()

    @kb.add("enter")
    def select_option(event):
        event.app.exit(result=options[selected_index])

    control = FormattedTextControl(get_menu_text(), show_cursor=False)
    window = Window(content=control)
    layout = Layout(window)
    app = Application(layout=layout, key_bindings=kb)

    return app.run()


def calendar_picker(
    default: date = None, min_date: date = None, max_date: date = None
) -> date:
    """Displays a interactive calender and returns the selected date"""
    today = date.today()
    current = default or today

    year, month, selected_day = current.year, current.month, current.day

    kb = KeyBindings()
    result = None

    def _clamp(y, m, d):
        nonlocal year, month, selected_day
        dt = date(y, m, d)
        if min_date:
            dt = max(dt, min_date)
        if max_date:
            dt = min(dt, max_date)
        year, month, selected_day = dt.year, dt.month, dt.day

    def _change_month(delta):
        nonlocal year, month, selected_day
        month = (month - 1 + delta) % 12 + 1
        year += (month - 1 + delta) // 12 if delta > 0 else -((-delta - month) // 12)
        selected_day = 1
        _clamp(year, month, selected_day)

    def _move(delta_days):
        nonlocal year, month, selected_day
        try:
            new_date = date(year, month, selected_day) + timedelta(days=delta_days)
            if min_date:
                new_date = max(new_date, min_date)
            if max_date:
                new_date = min(new_date, max_date)
            year, month, selected_day = new_date.year, new_date.month, new_date.day
        except ValueError:
            _change_month(1 if delta_days > 0 else -1)
            _clamp(year, month, selected_day)

    def get_text():
        cal = calendar.monthcalendar(year, month)
        header = f"{calendar.month_name[month]} {year}".center(28)
        weekdays = " Mo  Tu  We  Th  Fr  Sa  Su"

        def day_text(d):
            if d == 0:
                return "    "
            dt = date(year, month, d)
            if (min_date and dt < min_date) or (max_date and dt > max_date):
                return " ## "
            if d == selected_day:
                return f"[{d:02d}]"
            return f" {d:02d} "

        week_lines = ["".join(day_text(d) for d in week) for week in cal]
        return "\n".join([header, weekdays, *week_lines])

    @kb.add("left")
    def _(event):
        _move(-1)

    @kb.add("right")
    def _(event):
        _move(1)

    @kb.add("up")
    def _(event):
        _move(-7)

    @kb.add("down")
    def _(event):
        _move(7)

    @kb.add("enter")
    def _(event):
        nonlocal result
        result = date(year, month, selected_day)
        event.app.exit()

    control = FormattedTextControl(get_text, show_cursor=False)
    window = Window(content=control, always_hide_cursor=True)
    layout = Layout(HSplit([window]))
    app = Application(layout=layout, key_bindings=kb)

    app.run()
    return result

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window

import textwrap
import math

from .. import habits
from typing import Callable

class HabitTable:
    """Paginated table to display habits"""
    DATA: dict = {}
    _FILTER: Callable | None = None
    _COLUMNS: dict[str, dict] = {}
    _PADDING: int = 1
    _ROWS_PER_PAGE: int = 4
    _BUTTONS: list[tuple] = []
    _ACTIONS: dict[str, Callable] = {}
    _ROW_ACTION: str = ""
    _action: str = ""

    def __init__(self):
        # App setup
        self.kb = KeyBindings()
        self._setup_keybindings()
        self.control = FormattedTextControl(self._render, show_cursor=False)
        self.window = Window(content=self.control)
        self.app = Application(layout=Layout(self.window), key_bindings=self.kb)

    def run(self):
        with_action = True
        quit = False
        while with_action and not quit:
            self._reload_table()
            with_action = self.app.run()
            if with_action:
                quit = self._ACTIONS[self._action]()

    def exit(self, with_action=False):
        habits.save_habits()
        self.app.exit(result=with_action)

    def _reload_table(self):
        """Reset table"""
        self.DATA = habits.HABITS.get_habits(self._FILTER) if self._FILTER else habits.HABITS.get_habits()
        self.habit_ids = list(self.DATA.keys())
        self.selected_row = 0
        self.page = 0
        self.on_buttons = not(bool(self.DATA))  # start on buttons if no habits
        self.selected_button = 0
        self._action = None
        
        if self.on_buttons and self._BUTTONS:
            self._action = self._BUTTONS[self.selected_button]
        elif self._ROW_ACTION:
            self._action = self._ROW_ACTION

    def _setup_keybindings(self):
        """Setup key bindings for navigation and _ACTIONS"""

        @self.kb.add("up")
        def _up(event):
            if not self.habit_ids and not self._BUTTONS:
                return  # nothing to do
            max_row = min(self._ROWS_PER_PAGE, len(self.habit_ids) - self.page * self._ROWS_PER_PAGE) - 1
            if self.on_buttons and self.DATA:
                self.on_buttons = False
                self.selected_row = max_row
                self._action = self._ROW_ACTION
            elif self.selected_row == 0:
                if self._BUTTONS:
                    self.on_buttons = True
                    self._action = self._BUTTONS[self.selected_button]
            else:
                self.selected_row -= 1

        @self.kb.add("down")
        def _down(event):
            if not self.habit_ids and not self._BUTTONS:
                return
            max_row = min(self._ROWS_PER_PAGE, len(self.habit_ids) - self.page * self._ROWS_PER_PAGE) - 1
            if self.on_buttons and self.DATA:
                self.on_buttons = False
                self.selected_row = 0
                self._action = self._ROW_ACTION
            elif self.selected_row == max_row:
                if self._BUTTONS:
                    self.on_buttons = True
                    self._action = self._BUTTONS[self.selected_button]
            else:
                self.selected_row += 1

        @self.kb.add("left")
        def _left(event):
            if not self.habit_ids and not self._BUTTONS:
                return
            max_page = max(math.ceil(len(self.habit_ids) / self._ROWS_PER_PAGE) - 1, 0)
            max_button = len(self._BUTTONS) - 1
            if self.on_buttons and self._BUTTONS:
                self.selected_button = (self.selected_button - 1) % (max_button + 1)
                self._action = self._BUTTONS[self.selected_button]
            else:
                self.page = self.page - 1 if self.page > 0 else max_page
                self.selected_row = 0

        @self.kb.add("right")
        def _right(event):
            if not self.habit_ids and not self._BUTTONS:
                return
            max_page = max(math.ceil(len(self.habit_ids) / self._ROWS_PER_PAGE) - 1, 0)
            max_button = len(self._BUTTONS) - 1
            if self.on_buttons and self._BUTTONS:
                self.selected_button = (self.selected_button + 1) % (max_button + 1)
                self._action = self._BUTTONS[self.selected_button]
            else:
                self.page = self.page + 1 if self.page < max_page else 0
                self.selected_row = 0

        @self.kb.add("enter")
        def _enter(event):
            self.exit(with_action=True)

        @self.kb.add("c-q")
        def _force_quit(event):
            self.exit()
        
        @self.kb.add("c-q")
        def _force_quit(event):
            self.exit()

    def _hline(self, left, mid, right, straight):
        """Construct a horizontal table separator"""
        parts = []
        for i, h in enumerate(self._COLUMNS.keys()):
            parts.append(straight * self._COLUMNS[h]["width"])
            if i < len(self._COLUMNS.keys()) - 1:
                parts.append(mid)
        return left + "".join(parts) + right

    def _row(self, cells):
        """Construct a table row"""
        out = "┃"
        for i, h in enumerate(self._COLUMNS.keys()):
            sep = "┃" if i == len(self._COLUMNS.keys()) - 1 else "│"
            out += " " + cells[h].ljust(self._COLUMNS[h]["width"] - 2*self._PADDING) + " " + sep
        return out

    def _render(self):        
        """Render the habit table with headers, currently visible rows, and a footer"""
        fragments = []

        # Pagination
        start = self.page * self._ROWS_PER_PAGE
        end = start + self._ROWS_PER_PAGE
        visible = self.habit_ids[start:end]

        # Header row
        fragments.append(("", "   " + self._hline("┏", "┯", "┓", "━") + "\n"))
        header_cells = {header: (header.center(self._COLUMNS[header]["width"] - 2*self._PADDING)) for header in self._COLUMNS.keys()}
        fragments.append(("", "   " + self._row(header_cells) + "\n"))
        fragments.append(("", "   " + self._hline("┣", "┿", "┫", "━") + "\n"))

        # Habit rows
        for idx, uuid in enumerate(visible):
            habit = self.DATA[uuid]
            wrapped_cells = {
                name: [
                    (line.ljust(spec["width"] - 2) if spec["align"] == "left" 
                    else line.rjust(spec["width"] - 2) if spec["align"] == "right" 
                    else line.center(spec["width"] - 2))
                    for line in (textwrap.wrap(spec["value"](habit), spec["width"] - 2) or [""])
                ]
                for name, spec in self._COLUMNS.items()
            }

            lines = max(len(wrapped_cells[col]) for col in wrapped_cells)

            for i in range(lines):
                cells = {
                    col: wrapped_cells[col][i] if i < len(wrapped_cells[col]) else ""
                    for col in wrapped_cells
                }
                if self.selected_row == idx and i == 0 and not self.on_buttons:
                    prefix = ">> "
                    suffix = " <<"
                else:
                    prefix = "   "
                    suffix = ""
                fragments.append(("", prefix + self._row(cells) + suffix + "\n"))

            if idx < len(visible) - 1:
                fragments.append(("", "   " + self._hline("┠", "┼", "┨", "─") + "\n"))

        fragments.append(("", "   " + self._hline("┗", "┷", "┛", "━") + "\n"))

        # Buttons
        pieces = []
        for i, label in enumerate(self._BUTTONS):
            if i == 0:
                pieces.append(">> " if i == self.selected_button and self.on_buttons else "   ")
            pieces.append(f"[{label}]")
            if i < len(self._BUTTONS) - 1:
                if i == self.selected_button and self.on_buttons:
                    pieces.append(" << ")
                elif i + 1 == self.selected_button and self.on_buttons:
                    pieces.append(" >> ")
                else:
                    pieces.append("    ")
            else:
                pieces.append(" <<" if i == self.selected_button and self.on_buttons else "   ")
        buttons = "".join(pieces)

        # Footer
        total_pages = max(math.ceil(len(self.habit_ids) / self._ROWS_PER_PAGE), 1)
        total_width = sum(spec["width"] for spec in self._COLUMNS.values()) + 2*len(self._COLUMNS.keys()) + 3
        page_count = f"   ← Page {self.page + 1}/{total_pages} → "
        padding = total_width - len(page_count) - len(buttons)
        if padding >= 0:
            footer = page_count + (" " * padding) + buttons
        else:
            footer = page_count + buttons

        fragments.append(("", footer))

        return fragments

    def _get_selected_habit(self) -> str:
        """Return the selected habit"""
        if self.on_buttons:
            return None
        start = self.page * self._ROWS_PER_PAGE
        end = min(start + self._ROWS_PER_PAGE, len(self.habit_ids))
        if 0 <= self.selected_row < (end - start):
            return self.DATA.get(self.habit_ids[start + self.selected_row])
        return None
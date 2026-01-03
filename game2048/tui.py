"""TUI rendering and input handling using curses."""

import curses
from .game import Game2048, Direction


# Box-drawing characters for the grid
BOX = {
    'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝',
    'h': '═', 'v': '║',
    'lt': '╠', 'rt': '╣', 'tt': '╦', 'bt': '╩',
    'x': '╬',
}

# Color configuration: (foreground, background)
# Designed to match the original 2048 color scheme
TILE_STYLES = {
    0:    (0, 0),       # Empty - dimmed
    2:    (1, 0),       # Dark text on light bg
    4:    (2, 0),
    8:    (3, 0),
    16:   (4, 0),
    32:   (5, 0),
    64:   (6, 0),
    128:  (7, 0),
    256:  (8, 0),
    512:  (9, 0),
    1024: (10, 0),
    2048: (11, 0),
}


def setup_colors() -> None:
    """Initialize color pairs for the game."""
    curses.start_color()
    curses.use_default_colors()

    # Color pairs for tiles (trying to approximate 2048 colors)
    curses.init_pair(0, 8, -1)                              # Empty (gray)
    curses.init_pair(1, curses.COLOR_BLACK, 7)              # 2 - white bg
    curses.init_pair(2, curses.COLOR_BLACK, 7)              # 4 - cream
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_YELLOW)   # 8 - orange
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_YELLOW)   # 16 - orange-red
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)      # 32 - red
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_RED)      # 64 - red
    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_YELLOW)   # 128 - yellow
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_YELLOW)   # 256 - yellow
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_YELLOW)   # 512 - gold
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_GREEN)   # 1024 - bright
    curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_GREEN)   # 2048 - gold!
    curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_MAGENTA) # > 2048

    # UI colors
    curses.init_pair(20, curses.COLOR_CYAN, -1)    # Title
    curses.init_pair(21, curses.COLOR_YELLOW, -1)  # Score
    curses.init_pair(22, curses.COLOR_WHITE, -1)   # Grid
    curses.init_pair(23, curses.COLOR_GREEN, -1)   # Win message
    curses.init_pair(24, curses.COLOR_RED, -1)     # Game over


def get_tile_color(value: int) -> int:
    """Get the color pair for a tile value."""
    if value == 0:
        return curses.color_pair(0) | curses.A_DIM
    elif value in TILE_STYLES:
        pair_num = TILE_STYLES[value][0]
        return curses.color_pair(pair_num) | curses.A_BOLD
    else:
        return curses.color_pair(12) | curses.A_BOLD


class GameUI:
    """Curses-based UI for 2048."""

    CELL_WIDTH = 8
    CELL_HEIGHT = 3

    # ASCII art title
    TITLE = [
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓",
        "┃   ____   ___  _  _    ___    ┃",
        "┃  |___ \\ / _ \\| || |  ( _ )   ┃",
        "┃    __) | | | | || |_ / _ \\   ┃",
        "┃   / __/| |_| |__   _| (_) |  ┃",
        "┃  |_____|\\___/   |_|  \\___/   ┃",
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛",
    ]

    def __init__(self, stdscr):
        """Initialize the UI."""
        self.stdscr = stdscr
        self.game = Game2048()
        self.best_score = 0
        self._setup()

    def _setup(self) -> None:
        """Configure curses settings."""
        curses.curs_set(0)
        self.stdscr.keypad(True)
        self.stdscr.timeout(-1)
        setup_colors()

    def _safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        """Safely add string, handling screen boundaries."""
        height, width = self.stdscr.getmaxyx()
        if 0 <= y < height and 0 <= x < width:
            try:
                self.stdscr.addstr(y, x, text[:width - x], attr)
            except curses.error:
                pass

    def _safe_addch(self, y: int, x: int, ch: str, attr: int = 0) -> None:
        """Safely add character, handling screen boundaries."""
        height, width = self.stdscr.getmaxyx()
        if 0 <= y < height and 0 <= x < width - 1:
            try:
                self.stdscr.addstr(y, x, ch, attr)
            except curses.error:
                pass

    def _draw_title(self, start_y: int, center_x: int) -> int:
        """Draw the ASCII art title. Returns the next y position."""
        title_width = len(self.TITLE[0])
        x = center_x - title_width // 2

        for i, line in enumerate(self.TITLE):
            self._safe_addstr(start_y + i, x, line, curses.color_pair(20) | curses.A_BOLD)

        return start_y + len(self.TITLE) + 1

    def _draw_scores(self, y: int, center_x: int) -> int:
        """Draw score display. Returns the next y position."""
        # Update best score
        if self.game.score > self.best_score:
            self.best_score = self.game.score

        score_box = f"┌{'─' * 12}┬{'─' * 12}┐"
        score_row = f"│ SCORE      │ BEST       │"
        value_row = f"│ {self.game.score:<10} │ {self.best_score:<10} │"
        score_end = f"└{'─' * 12}┴{'─' * 12}┘"

        box_width = len(score_box)
        x = center_x - box_width // 2

        self._safe_addstr(y, x, score_box, curses.color_pair(21))
        self._safe_addstr(y + 1, x, score_row, curses.color_pair(21) | curses.A_DIM)
        self._safe_addstr(y + 2, x, value_row, curses.color_pair(21) | curses.A_BOLD)
        self._safe_addstr(y + 3, x, score_end, curses.color_pair(21))

        return y + 5

    def _draw_grid(self, start_y: int, start_x: int) -> None:
        """Draw the game grid with box-drawing characters."""
        grid_color = curses.color_pair(22) | curses.A_DIM

        # Calculate dimensions
        inner_width = self.CELL_WIDTH
        inner_height = self.CELL_HEIGHT

        # Draw top border
        top = BOX['tl'] + (BOX['h'] * inner_width + BOX['tt']) * 3 + BOX['h'] * inner_width + BOX['tr']
        self._safe_addstr(start_y, start_x, top, grid_color)

        # Draw rows
        for row in range(self.game.size):
            cell_y = start_y + 1 + row * (inner_height + 1)

            # Draw cell content rows
            for dy in range(inner_height):
                line = BOX['v']
                for col in range(self.game.size):
                    value = self.game.board[row][col]
                    cell_content = self._get_cell_content(value, dy)
                    line += cell_content + BOX['v']
                self._safe_addstr(cell_y + dy, start_x, line[0], grid_color)

                # Draw each cell with its own color
                x_pos = start_x + 1
                for col in range(self.game.size):
                    value = self.game.board[row][col]
                    cell_content = self._get_cell_content(value, dy)
                    color = get_tile_color(value)
                    self._safe_addstr(cell_y + dy, x_pos, cell_content, color)
                    x_pos += inner_width
                    self._safe_addstr(cell_y + dy, x_pos, BOX['v'], grid_color)
                    x_pos += 1

            # Draw separator (except after last row)
            if row < self.game.size - 1:
                sep_y = cell_y + inner_height
                sep = BOX['lt'] + (BOX['h'] * inner_width + BOX['x']) * 3 + BOX['h'] * inner_width + BOX['rt']
                self._safe_addstr(sep_y, start_x, sep, grid_color)

        # Draw bottom border
        bottom_y = start_y + 1 + self.game.size * (inner_height + 1) - 1
        bottom = BOX['bl'] + (BOX['h'] * inner_width + BOX['bt']) * 3 + BOX['h'] * inner_width + BOX['br']
        self._safe_addstr(bottom_y, start_x, bottom, grid_color)

    def _get_cell_content(self, value: int, row_in_cell: int) -> str:
        """Get the content for a cell at a specific row within the cell."""
        if row_in_cell == self.CELL_HEIGHT // 2:
            # Center row - show value
            if value == 0:
                return ' ' * self.CELL_WIDTH
            else:
                return str(value).center(self.CELL_WIDTH)
        else:
            # Other rows - just padding
            return ' ' * self.CELL_WIDTH

    def _draw_instructions(self, y: int, center_x: int) -> None:
        """Draw game instructions."""
        instructions = [
            "╭───────────────────────────────────╮",
            "│  ← ↑ ↓ →  or  W A S D  to move   │",
            "│      R = Restart   Q = Quit      │",
            "╰───────────────────────────────────╯",
        ]

        box_width = len(instructions[0])
        x = center_x - box_width // 2

        for i, line in enumerate(instructions):
            attr = curses.A_DIM if i in (1, 2) else 0
            self._safe_addstr(y + i, x, line, attr)

    def _draw_game_over_overlay(self) -> None:
        """Draw game over or win overlay."""
        height, width = self.stdscr.getmaxyx()

        if self.game.won:
            messages = [
                "╔═══════════════════════════════╗",
                "║                               ║",
                "║      ★ ★ ★  YOU WIN!  ★ ★ ★   ║",
                "║                               ║",
                "║      You reached 2048!        ║",
                "║                               ║",
                f"║      Final Score: {self.game.score:<10} ║",
                "║                               ║",
                "║   Press R to play again       ║",
                "║   Press Q to quit             ║",
                "║                               ║",
                "╚═══════════════════════════════╝",
            ]
            color = curses.color_pair(23) | curses.A_BOLD
        else:
            messages = [
                "╔═══════════════════════════════╗",
                "║                               ║",
                "║         GAME  OVER            ║",
                "║                               ║",
                f"║      Final Score: {self.game.score:<10} ║",
                f"║      Best Score:  {self.best_score:<10} ║",
                "║                               ║",
                "║   Press R to try again        ║",
                "║   Press Q to quit             ║",
                "║                               ║",
                "╚═══════════════════════════════╝",
            ]
            color = curses.color_pair(24) | curses.A_BOLD

        box_width = len(messages[0])
        box_height = len(messages)
        start_x = (width - box_width) // 2
        start_y = (height - box_height) // 2

        for i, line in enumerate(messages):
            self._safe_addstr(start_y + i, start_x, line, color)

    def draw(self) -> None:
        """Draw the entire game screen."""
        self.stdscr.clear()

        height, width = self.stdscr.getmaxyx()
        center_x = width // 2

        # Calculate grid dimensions
        grid_width = 1 + (self.CELL_WIDTH + 1) * self.game.size
        grid_height = 1 + (self.CELL_HEIGHT + 1) * self.game.size

        # Calculate starting positions
        total_height = len(self.TITLE) + 1 + 5 + grid_height + 1 + 4
        start_y = max(1, (height - total_height) // 2)

        # Draw components
        y = self._draw_title(start_y, center_x)
        y = self._draw_scores(y, center_x)

        grid_x = center_x - grid_width // 2
        self._draw_grid(y, grid_x)

        instructions_y = y + grid_height + 1
        self._draw_instructions(instructions_y, center_x)

        # Draw overlay if game ended
        if self.game.game_over or self.game.won:
            self._draw_game_over_overlay()

        self.stdscr.refresh()

    def handle_input(self) -> bool:
        """Handle keyboard input. Returns False if user wants to quit."""
        key = self.stdscr.getch()

        key_map = {
            curses.KEY_UP: Direction.UP,
            curses.KEY_DOWN: Direction.DOWN,
            curses.KEY_LEFT: Direction.LEFT,
            curses.KEY_RIGHT: Direction.RIGHT,
            ord('w'): Direction.UP,
            ord('W'): Direction.UP,
            ord('s'): Direction.DOWN,
            ord('S'): Direction.DOWN,
            ord('a'): Direction.LEFT,
            ord('A'): Direction.LEFT,
            ord('d'): Direction.RIGHT,
            ord('D'): Direction.RIGHT,
        }

        if key in (ord('q'), ord('Q')):
            return False

        if key in (ord('r'), ord('R')):
            self.game.reset()
            return True

        if key in key_map and not (self.game.game_over or self.game.won):
            self.game.move(key_map[key])

        return True

    def run(self) -> int:
        """Run the game loop. Returns final score."""
        while True:
            self.draw()
            if not self.handle_input():
                break
        return self.game.score


def run_game(stdscr=None) -> int:
    """Run the 2048 game."""
    if stdscr is None:
        return curses.wrapper(_run_game_wrapper)
    else:
        ui = GameUI(stdscr)
        return ui.run()


def _run_game_wrapper(stdscr) -> int:
    """Wrapper function for curses.wrapper."""
    ui = GameUI(stdscr)
    return ui.run()

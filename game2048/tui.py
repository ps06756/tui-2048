"""TUI rendering and input handling using curses."""

import curses
import os
from .game import Game2048, Direction


def setup_colors() -> None:
    """Initialize color pairs matching the original 2048 game."""
    curses.start_color()
    curses.use_default_colors()  # Enable transparent background with -1

    # Check if terminal supports 256 colors AND can change colors
    use_256 = curses.COLORS >= 256 and curses.can_change_color()

    if use_256:
        # Define custom colors approximating 2048's color scheme
        # Format: curses.init_color(color_number, r, g, b) where values are 0-1000

        # Background colors
        curses.init_color(20, 738, 678, 629)   # Board bg #bbada0
        curses.init_color(21, 804, 757, 706)   # Empty cell #cdc1b4

        # Tile backgrounds
        curses.init_color(22, 933, 894, 855)   # 2: #eee4da
        curses.init_color(23, 929, 878, 784)   # 4: #ede0c8
        curses.init_color(24, 949, 694, 475)   # 8: #f2b179
        curses.init_color(25, 961, 584, 388)   # 16: #f59563
        curses.init_color(26, 965, 486, 373)   # 32: #f67c5f
        curses.init_color(27, 965, 369, 231)   # 64: #f65e3b
        curses.init_color(28, 929, 812, 447)   # 128: #edcf72
        curses.init_color(29, 929, 800, 380)   # 256: #edcc61
        curses.init_color(30, 929, 784, 314)   # 512: #edc850
        curses.init_color(31, 929, 773, 247)   # 1024: #edc53f
        curses.init_color(32, 929, 761, 180)   # 2048: #edc22e
        curses.init_color(33, 235, 227, 178)   # >2048: #3c3a32

        # Text colors
        curses.init_color(40, 467, 431, 396)   # Dark text #776e65
        curses.init_color(41, 976, 965, 949)   # Light text #f9f6f2

        # Color pairs: (foreground, background)
        curses.init_pair(1, 40, 21)    # Empty
        curses.init_pair(2, 40, 22)    # 2
        curses.init_pair(3, 40, 23)    # 4
        curses.init_pair(4, 41, 24)    # 8
        curses.init_pair(5, 41, 25)    # 16
        curses.init_pair(6, 41, 26)    # 32
        curses.init_pair(7, 41, 27)    # 64
        curses.init_pair(8, 41, 28)    # 128
        curses.init_pair(9, 41, 29)    # 256
        curses.init_pair(10, 41, 30)   # 512
        curses.init_pair(11, 41, 31)   # 1024
        curses.init_pair(12, 41, 32)   # 2048
        curses.init_pair(13, 41, 33)   # >2048

        # UI colors
        curses.init_pair(20, 40, 20)   # Board background
        curses.init_pair(21, 41, -1)   # Title
        curses.init_pair(22, 41, 24)   # Score box (orange-ish)
        curses.init_pair(23, 40, -1)   # Instructions
    else:
        # Fallback for 8/16 color terminals
        # Color pairs using basic colors
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Empty
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)     # 2
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)     # 4
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_YELLOW)    # 8
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_YELLOW)    # 16
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_RED)       # 32
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_RED)       # 64
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_YELLOW)    # 128
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_YELLOW)    # 256
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_YELLOW)   # 512
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_GREEN)    # 1024
        curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_GREEN)    # 2048
        curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_MAGENTA)  # >2048

        # UI colors
        curses.init_pair(20, curses.COLOR_WHITE, -1)   # Board
        curses.init_pair(21, curses.COLOR_WHITE, -1)   # Title
        curses.init_pair(22, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Score
        curses.init_pair(23, curses.COLOR_WHITE, -1)   # Instructions


def get_tile_color(value: int) -> int:
    """Get the color pair for a tile value."""
    color_map = {
        0: 1, 2: 2, 4: 3, 8: 4, 16: 5, 32: 6, 64: 7,
        128: 8, 256: 9, 512: 10, 1024: 11, 2048: 12
    }
    pair = color_map.get(value, 13)
    attr = curses.A_BOLD if value >= 8 else 0
    return curses.color_pair(pair) | attr


class GameUI:
    """Curses-based UI for 2048 matching the web version."""

    # Cell dimensions (terminal chars are ~2:1 height:width, so width ~2x height for square look)
    CELL_WIDTH = 8
    CELL_HEIGHT = 3

    # Padding from top-left
    MARGIN_X = 2
    MARGIN_Y = 1

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

    def _draw_header(self) -> int:
        """Draw the title and score boxes. Returns next y position."""
        x = self.MARGIN_X
        y = self.MARGIN_Y

        # Title "2048"
        title = "2048"
        self._safe_addstr(y, x, title, curses.color_pair(21) | curses.A_BOLD)

        # Score boxes to the right of the title
        score_x = x + len(title) + 4

        # SCORE box
        score_label = " SCORE "
        score_value = f" {self.game.score} "
        self._safe_addstr(y, score_x, score_label, curses.color_pair(22))
        self._safe_addstr(y + 1, score_x, score_value.center(len(score_label)),
                         curses.color_pair(22) | curses.A_BOLD)

        # BEST box
        if self.game.score > self.best_score:
            self.best_score = self.game.score

        best_x = score_x + len(score_label) + 2
        best_label = "  BEST  "
        best_value = f" {self.best_score} "
        self._safe_addstr(y, best_x, best_label, curses.color_pair(22))
        self._safe_addstr(y + 1, best_x, best_value.center(len(best_label)),
                         curses.color_pair(22) | curses.A_BOLD)

        # Subtitle
        subtitle = "Join the tiles, get to 2048!"
        self._safe_addstr(y + 3, x, subtitle, curses.color_pair(23) | curses.A_DIM)

        return y + 5

    def _draw_board(self, start_y: int) -> int:
        """Draw the game board. Returns next y position."""
        x = self.MARGIN_X
        y = start_y

        board_width = self.game.size * self.CELL_WIDTH + (self.game.size + 1)
        board_height = self.game.size * self.CELL_HEIGHT + (self.game.size + 1)

        # Draw each cell
        for row in range(self.game.size):
            for col in range(self.game.size):
                cell_x = x + 1 + col * (self.CELL_WIDTH + 1)
                cell_y = y + 1 + row * (self.CELL_HEIGHT + 1)
                self._draw_cell(cell_y, cell_x, self.game.board[row][col])

        # Draw grid borders
        border_color = curses.color_pair(20)

        # Horizontal lines
        for row in range(self.game.size + 1):
            line_y = y + row * (self.CELL_HEIGHT + 1)
            line = "─" * board_width
            self._safe_addstr(line_y, x, line, border_color)

        # Vertical lines and corners
        for row in range(self.game.size):
            for cell_row in range(self.CELL_HEIGHT):
                line_y = y + 1 + row * (self.CELL_HEIGHT + 1) + cell_row
                for col in range(self.game.size + 1):
                    line_x = x + col * (self.CELL_WIDTH + 1)
                    self._safe_addstr(line_y, line_x, "│", border_color)

        # Corner pieces
        for row in range(self.game.size + 1):
            for col in range(self.game.size + 1):
                corner_y = y + row * (self.CELL_HEIGHT + 1)
                corner_x = x + col * (self.CELL_WIDTH + 1)

                if row == 0 and col == 0:
                    char = "┌"
                elif row == 0 and col == self.game.size:
                    char = "┐"
                elif row == self.game.size and col == 0:
                    char = "└"
                elif row == self.game.size and col == self.game.size:
                    char = "┘"
                elif row == 0:
                    char = "┬"
                elif row == self.game.size:
                    char = "┴"
                elif col == 0:
                    char = "├"
                elif col == self.game.size:
                    char = "┤"
                else:
                    char = "┼"

                self._safe_addstr(corner_y, corner_x, char, border_color)

        return y + board_height + 1

    def _draw_cell(self, y: int, x: int, value: int) -> None:
        """Draw a single cell with its value."""
        color = get_tile_color(value)

        # Fill the entire cell with background color
        for dy in range(self.CELL_HEIGHT):
            self._safe_addstr(y + dy, x, " " * self.CELL_WIDTH, color)

        # Draw the value centered in the cell
        if value > 0:
            value_str = str(value)
            value_x = x + (self.CELL_WIDTH - len(value_str)) // 2
            value_y = y + self.CELL_HEIGHT // 2
            self._safe_addstr(value_y, value_x, value_str, color)

    def _draw_instructions(self, y: int) -> None:
        """Draw game instructions."""
        x = self.MARGIN_X

        # Controls box
        self._safe_addstr(y, x, "CONTROLS", curses.color_pair(21) | curses.A_BOLD)
        self._safe_addstr(y + 1, x, "  Move tiles:  Arrow Keys  or  W A S D", curses.color_pair(23))
        self._safe_addstr(y + 2, x, "  New game:    R", curses.color_pair(23))
        self._safe_addstr(y + 3, x, "  Quit:        Q", curses.color_pair(23))

    def _draw_game_over_overlay(self) -> None:
        """Draw game over or win overlay."""
        height, width = self.stdscr.getmaxyx()

        # Calculate overlay position (over the board)
        board_width = self.game.size * self.CELL_WIDTH + (self.game.size + 1)
        board_height = self.game.size * self.CELL_HEIGHT + (self.game.size + 1)

        overlay_x = self.MARGIN_X + board_width // 2 - 15
        overlay_y = 6 + board_height // 2 - 3

        if self.game.won:
            msg1 = "    You Win!    "
            msg2 = f"  Score: {self.game.score}  "
            color = curses.color_pair(12) | curses.A_BOLD
        else:
            msg1 = "   Game Over!   "
            msg2 = f"  Score: {self.game.score}  "
            color = curses.color_pair(6) | curses.A_BOLD

        msg3 = " R=Retry  Q=Quit "

        box_width = max(len(msg1), len(msg2), len(msg3)) + 4

        # Draw box
        self._safe_addstr(overlay_y, overlay_x, "┌" + "─" * (box_width - 2) + "┐", color)
        self._safe_addstr(overlay_y + 1, overlay_x, "│" + msg1.center(box_width - 2) + "│", color)
        self._safe_addstr(overlay_y + 2, overlay_x, "│" + msg2.center(box_width - 2) + "│", color)
        self._safe_addstr(overlay_y + 3, overlay_x, "│" + msg3.center(box_width - 2) + "│", color)
        self._safe_addstr(overlay_y + 4, overlay_x, "└" + "─" * (box_width - 2) + "┘", color)

    def draw(self) -> None:
        """Draw the entire game screen."""
        self.stdscr.clear()

        y = self._draw_header()
        y = self._draw_board(y)
        self._draw_instructions(y)

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
        # Set TERM to support 256 colors if not already set
        if 'TERM' not in os.environ or '256color' not in os.environ.get('TERM', ''):
            os.environ['TERM'] = 'xterm-256color'
        return curses.wrapper(_run_game_wrapper)
    else:
        ui = GameUI(stdscr)
        return ui.run()


def _run_game_wrapper(stdscr) -> int:
    """Wrapper function for curses.wrapper."""
    ui = GameUI(stdscr)
    return ui.run()

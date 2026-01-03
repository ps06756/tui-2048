"""TUI rendering and input handling using curses."""

import curses
from typing import Optional
from .game import Game2048, Direction


# Color pairs for different tile values
TILE_COLORS = {
    0: 1,      # Empty
    2: 2,      # Light
    4: 3,
    8: 4,
    16: 5,
    32: 6,
    64: 7,
    128: 8,
    256: 9,
    512: 10,
    1024: 11,
    2048: 12,  # Gold/Yellow for win!
}


def setup_colors() -> None:
    """Initialize color pairs for the game."""
    curses.start_color()
    curses.use_default_colors()

    # Define color pairs (foreground, background)
    curses.init_pair(1, curses.COLOR_WHITE, -1)       # Empty
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)    # 2
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)     # 4
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_CYAN)     # 8
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_GREEN)    # 16
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_YELLOW)   # 32
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_RED)      # 64
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_MAGENTA)  # 128
    curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLUE)     # 256
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_CYAN)    # 512
    curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_GREEN)   # 1024
    curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # 2048


def get_tile_color(value: int) -> int:
    """Get the color pair for a tile value."""
    if value in TILE_COLORS:
        return curses.color_pair(TILE_COLORS[value])
    # For values > 2048, use the 2048 color
    return curses.color_pair(12) | curses.A_BOLD


class GameUI:
    """Curses-based UI for 2048."""

    CELL_WIDTH = 7
    CELL_HEIGHT = 3

    def __init__(self, stdscr):
        """Initialize the UI.

        Args:
            stdscr: Curses standard screen
        """
        self.stdscr = stdscr
        self.game = Game2048()
        self._setup()

    def _setup(self) -> None:
        """Configure curses settings."""
        curses.curs_set(0)  # Hide cursor
        self.stdscr.keypad(True)  # Enable special keys
        self.stdscr.timeout(-1)  # Blocking input
        setup_colors()

    def _draw_cell(self, row: int, col: int, value: int, start_y: int, start_x: int) -> None:
        """Draw a single cell."""
        y = start_y + row * self.CELL_HEIGHT
        x = start_x + col * self.CELL_WIDTH

        color = get_tile_color(value)

        # Draw the cell background and value
        for dy in range(self.CELL_HEIGHT):
            for dx in range(self.CELL_WIDTH):
                try:
                    self.stdscr.addch(y + dy, x + dx, ' ', color)
                except curses.error:
                    pass

        # Draw the value in the center
        if value > 0:
            value_str = str(value)
            value_x = x + (self.CELL_WIDTH - len(value_str)) // 2
            value_y = y + self.CELL_HEIGHT // 2
            try:
                self.stdscr.addstr(value_y, value_x, value_str, color | curses.A_BOLD)
            except curses.error:
                pass

    def _draw_board(self) -> None:
        """Draw the game board."""
        height, width = self.stdscr.getmaxyx()

        board_width = self.game.size * self.CELL_WIDTH
        board_height = self.game.size * self.CELL_HEIGHT

        start_x = (width - board_width) // 2
        start_y = (height - board_height) // 2 + 2  # Offset for title

        # Draw title
        title = "═══ 2048 ═══"
        try:
            self.stdscr.addstr(start_y - 4, (width - len(title)) // 2, title, curses.A_BOLD)
        except curses.error:
            pass

        # Draw score
        score_str = f"Score: {self.game.score}"
        try:
            self.stdscr.addstr(start_y - 2, (width - len(score_str)) // 2, score_str)
        except curses.error:
            pass

        # Draw cells
        for row in range(self.game.size):
            for col in range(self.game.size):
                value = self.game.board[row][col]
                self._draw_cell(row, col, value, start_y, start_x)

        # Draw grid lines
        for row in range(self.game.size + 1):
            y = start_y + row * self.CELL_HEIGHT
            for x in range(start_x, start_x + board_width):
                try:
                    self.stdscr.addch(y - 1 if row > 0 else y, x, '─')
                except curses.error:
                    pass

        # Draw instructions
        instructions = "Arrow keys: Move | R: Restart | Q: Quit"
        try:
            self.stdscr.addstr(start_y + board_height + 2, (width - len(instructions)) // 2, instructions)
        except curses.error:
            pass

    def _draw_game_over(self) -> None:
        """Draw game over overlay."""
        height, width = self.stdscr.getmaxyx()

        if self.game.won:
            msg = "🎉 YOU WIN! 🎉"
            msg2 = f"Final Score: {self.game.score}"
        else:
            msg = "GAME OVER"
            msg2 = f"Final Score: {self.game.score}"

        msg3 = "Press R to restart or Q to quit"

        center_y = height // 2
        try:
            self.stdscr.addstr(center_y - 1, (width - len(msg)) // 2, msg,
                              curses.A_BOLD | curses.A_REVERSE)
            self.stdscr.addstr(center_y, (width - len(msg2)) // 2, msg2)
            self.stdscr.addstr(center_y + 1, (width - len(msg3)) // 2, msg3)
        except curses.error:
            pass

    def draw(self) -> None:
        """Draw the entire game screen."""
        self.stdscr.clear()
        self._draw_board()

        if self.game.game_over or self.game.won:
            self._draw_game_over()

        self.stdscr.refresh()

    def handle_input(self) -> bool:
        """Handle keyboard input.

        Returns:
            False if the user wants to quit, True otherwise.
        """
        key = self.stdscr.getch()

        # Direction keys
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
        """Run the game loop.

        Returns:
            Final score
        """
        running = True
        while running:
            self.draw()
            running = self.handle_input()

        return self.game.score


def run_game(stdscr=None) -> int:
    """Run the 2048 game.

    Args:
        stdscr: Optional curses screen (if None, will initialize curses)

    Returns:
        Final score
    """
    if stdscr is None:
        return curses.wrapper(_run_game_wrapper)
    else:
        ui = GameUI(stdscr)
        return ui.run()


def _run_game_wrapper(stdscr) -> int:
    """Wrapper function for curses.wrapper."""
    ui = GameUI(stdscr)
    return ui.run()

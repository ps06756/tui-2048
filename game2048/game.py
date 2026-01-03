"""Core 2048 game logic."""

import random
from typing import List, Tuple, Optional
from enum import Enum


class Direction(Enum):
    """Movement directions."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class Game2048:
    """2048 game engine."""

    def __init__(self, size: int = 4, win_tile: int = 2048):
        """Initialize the game.

        Args:
            size: Board size (default 4x4)
            win_tile: Tile value to win (default 2048)
        """
        self.size = size
        self.win_tile = win_tile
        self.board: List[List[int]] = []
        self.score = 0
        self.game_over = False
        self.won = False
        self.reset()

    def reset(self) -> None:
        """Reset the game to initial state."""
        self.board = [[0] * self.size for _ in range(self.size)]
        self.score = 0
        self.game_over = False
        self.won = False
        self._spawn_tile()
        self._spawn_tile()

    def _get_empty_cells(self) -> List[Tuple[int, int]]:
        """Get list of empty cell coordinates."""
        empty = []
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    empty.append((r, c))
        return empty

    def _spawn_tile(self) -> bool:
        """Spawn a new tile (90% chance of 2, 10% chance of 4).

        Returns:
            True if tile was spawned, False if board is full.
        """
        empty = self._get_empty_cells()
        if not empty:
            return False

        r, c = random.choice(empty)
        self.board[r][c] = 2 if random.random() < 0.9 else 4
        return True

    def _slide_row_left(self, row: List[int]) -> Tuple[List[int], int]:
        """Slide and merge a single row to the left.

        Returns:
            Tuple of (new_row, points_earned)
        """
        # Remove zeros
        non_zero = [x for x in row if x != 0]

        # Merge adjacent equal tiles
        merged = []
        points = 0
        skip = False

        for i in range(len(non_zero)):
            if skip:
                skip = False
                continue

            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged_value = non_zero[i] * 2
                merged.append(merged_value)
                points += merged_value
                skip = True
            else:
                merged.append(non_zero[i])

        # Pad with zeros
        result = merged + [0] * (self.size - len(merged))
        return result, points

    def _rotate_board_clockwise(self) -> None:
        """Rotate the board 90 degrees clockwise."""
        self.board = [list(row) for row in zip(*self.board[::-1])]

    def _rotate_board_counter_clockwise(self) -> None:
        """Rotate the board 90 degrees counter-clockwise."""
        self.board = [list(row) for row in zip(*self.board)][::-1]

    def move(self, direction: Direction) -> bool:
        """Execute a move in the given direction.

        Args:
            direction: Direction to move tiles

        Returns:
            True if the move changed the board, False otherwise.
        """
        if self.game_over:
            return False

        # Store original board to check if move changed anything
        original = [row[:] for row in self.board]

        # Rotate board so we can always slide left
        # UP: 3 CW (=1 CCW) so bottom→right, then slide left moves toward top
        # DOWN: 1 CW so top→right, then slide left moves toward bottom
        rotations = {
            Direction.LEFT: 0,
            Direction.UP: 3,
            Direction.RIGHT: 2,
            Direction.DOWN: 1,
        }

        for _ in range(rotations[direction]):
            self._rotate_board_clockwise()

        # Slide all rows left
        total_points = 0
        for i in range(self.size):
            self.board[i], points = self._slide_row_left(self.board[i])
            total_points += points

        # Rotate back
        for _ in range((4 - rotations[direction]) % 4):
            self._rotate_board_clockwise()

        # Check if board changed
        board_changed = self.board != original

        if board_changed:
            self.score += total_points
            self._spawn_tile()
            self._check_game_state()

        return board_changed

    def _check_game_state(self) -> None:
        """Check for win or game over conditions."""
        # Check for win
        for row in self.board:
            for cell in row:
                if cell >= self.win_tile:
                    self.won = True

        # Check for game over (no valid moves)
        if not self._get_empty_cells():
            # Check for possible merges
            can_merge = False
            for r in range(self.size):
                for c in range(self.size):
                    current = self.board[r][c]
                    # Check right neighbor
                    if c + 1 < self.size and self.board[r][c + 1] == current:
                        can_merge = True
                        break
                    # Check bottom neighbor
                    if r + 1 < self.size and self.board[r + 1][c] == current:
                        can_merge = True
                        break
                if can_merge:
                    break

            if not can_merge:
                self.game_over = True

    def can_move(self) -> bool:
        """Check if any move is possible."""
        if self._get_empty_cells():
            return True

        # Check for possible merges
        for r in range(self.size):
            for c in range(self.size):
                current = self.board[r][c]
                if c + 1 < self.size and self.board[r][c + 1] == current:
                    return True
                if r + 1 < self.size and self.board[r + 1][c] == current:
                    return True

        return False

    def get_highest_tile(self) -> int:
        """Get the highest tile value on the board."""
        return max(max(row) for row in self.board)

    def __str__(self) -> str:
        """String representation of the board."""
        max_width = len(str(self.get_highest_tile()))
        lines = []
        for row in self.board:
            cells = [str(cell).center(max_width) if cell else ".".center(max_width)
                     for cell in row]
            lines.append(" | ".join(cells))
        return "\n".join(lines)

"""TUI-based 2048 game."""

__version__ = "1.0.0"
__author__ = "Your Name"

from .game import Game2048
from .tui import run_game

__all__ = ["Game2048", "run_game", "__version__"]

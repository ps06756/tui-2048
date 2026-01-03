#!/usr/bin/env python3
"""Main entry point for the 2048 TUI game."""

from game2048 import run_game


def main():
    """Run the 2048 game."""
    try:
        score = run_game()
        print(f"\nThanks for playing! Final score: {score}")
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")


if __name__ == "__main__":
    main()

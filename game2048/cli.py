"""Command-line interface for 2048 game."""

import argparse
import sys
from . import __version__, run_game


def main():
    """Main entry point for the 2048 CLI."""
    parser = argparse.ArgumentParser(
        prog="tui-2048",
        description="Play 2048 in your terminal!",
        epilog="Use arrow keys or WASD to move tiles. Press Q to quit, R to restart."
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    # Parse args (currently just for --version and --help)
    parser.parse_args()

    try:
        score = run_game()
        print(f"\nThanks for playing! Final score: {score}")
        return 0
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")
        return 1
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

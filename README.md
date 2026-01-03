# 2048 TUI Game

A terminal-based implementation of the classic 2048 puzzle game using Python and curses.

![Python Version](https://img.shields.io/pypi/pyversions/tui-2048)
![License](https://img.shields.io/pypi/l/tui-2048)

## Installation

### From PyPI (recommended)

```bash
pip install tui-2048
```

### From source

```bash
git clone https://github.com/yourusername/tui-2048.git
cd tui-2048
pip install .
```

### Development install

```bash
pip install -e .
```

## Usage

After installation, run the game with:

```bash
tui-2048
```

Or alternatively:

```bash
2048
```

Or run directly with Python:

```bash
python -m game2048.cli
```

## Controls

| Key | Action |
|-----|--------|
| ↑ / W | Move tiles up |
| ↓ / S | Move tiles down |
| ← / A | Move tiles left |
| → / D | Move tiles right |
| R | Restart game |
| Q | Quit game |

## Game Rules

1. Use arrow keys or WASD to slide all tiles in a direction
2. Tiles with the same number merge into one when they collide
3. Each move spawns a new tile (2 or 4) in an empty spot
4. Combine tiles to reach **2048** and win!
5. Game ends when no moves are possible

## Features

- Colorful terminal UI matching the original 2048 style
- 256-color support (with fallback for basic terminals)
- Score and best score tracking
- Works on Linux, macOS, and Windows (with WSL)

## Requirements

- Python 3.7+
- A terminal that supports curses (most Unix terminals, Windows Terminal with WSL)

## Project Structure

```
tui-2048/
├── pyproject.toml       # Package configuration
├── LICENSE              # MIT License
├── README.md            # This file
├── main.py              # Alternative entry point
└── game2048/
    ├── __init__.py      # Package exports & version
    ├── cli.py           # CLI entry point
    ├── game.py          # Core game logic
    └── tui.py           # Terminal UI rendering
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

# 2048 TUI Game

A terminal-based implementation of the classic 2048 puzzle game using Python and curses.

## Requirements

- Python 3.7+
- A terminal that supports curses (Linux/macOS terminals, Windows Terminal with WSL)

## How to Play

```bash
python main.py
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

1. Tiles with the same number merge when they collide
2. Each move spawns a new tile (2 or 4)
3. Combine tiles to reach 2048 and win!
4. Game ends when no moves are possible

## Project Structure

```
tui-2048/
├── main.py              # Entry point
├── game2048/
│   ├── __init__.py      # Package exports
│   ├── game.py          # Core game logic
│   └── tui.py           # Terminal UI rendering
└── README.md
```

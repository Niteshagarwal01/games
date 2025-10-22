# Game Collection Launcher

This repository is a curated collection of Python/Pygame games, all accessible from a graphical launcher (`game_launcher.py`). Each game is self-contained in its own folder, with assets and a README. The launcher auto-discovers games and lets you browse, preview, and launch them easily.

## How It Works

- Run `game_launcher.py` to open a graphical menu of all available games.
- Browse games, view screenshots and descriptions, and launch any game with a click.
- Each game runs in its own process; press <kbd>F10</kbd> in-game to return to the launcher.

## Quick Start (Windows)

1. **Install Python 3.10+** ([Download Python](https://www.python.org/downloads/))
2. **Create and activate a virtual environment** (recommended):
	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	```
3. **Install dependencies:**
	```powershell
	python -m pip install --upgrade pip
	python -m pip install pygame
	```
	For `cosmic-heat-pygame-main`, also run:
	```powershell
	python -m pip install -r cosmic-heat-pygame-main\requirements.txt
	```
4. **Launch the game collection:**
	```powershell
	python game_launcher.py
	```

## Included Games

### Aeroblasters
2D vertical plane shooter. Dodge enemies, shoot, and survive. [Pygame]

### Arc Dash
Endless target-based arcade game. Collect dots, avoid revolving balls. [Pygame]

### Car Racing 2d
Car & obstacle dodging game. Use controls to move and avoid obstacles. [Pygame]

### Connected
Endless arcade game. Collect squares, avoid rectangles, flip direction. [Pygame]

### Cosmic Heat
2D space shooter with bosses and enemies. Keyboard or joystick controls. [Pygame]
**Extra requirements:** See `cosmic-heat-pygame-main/requirements.txt`.

### GhostBusters
Platformer with tile-based physics, scrolling, and parallax. Defeat ghosts, reach the final level. [Pygame]

### HyperTile Dash
Endless arcade game. Reach target tiles, avoid deadly tiles, create new ones. [Pygame]

### Memory Puzzle
Fruit memory puzzle. Match cards, clear the board, info mode for fruit facts. [Pygame]

### Balloon Shooter
Classic balloon shooter game. (See `Balloon-Shooter-Game-Python-main` folder.)

## Controls & Usage

- Most games use keyboard controls; see each game's README for details.
- To launch a game directly (skipping the launcher):
  ```powershell
  python game_launcher.py --launch "GameName"
  ```
  Replace `GameName` with the folder name (e.g., `GhostBusters`).

## Adding Your Own Games

1. Create a new folder in the repo root.
2. Add your game code (`main.py` or `game.py`), assets, and a `README.md` with a short description.
3. Optionally add a preview image (`app.png` or `app.gif`).
4. The launcher will auto-detect your game if it has a main script.

## License

Each game may have its own license. See individual folders for details. If you want to add a license for the whole collection, add a top-level `LICENSE` file.

## Credits

Games by various authors. Launcher by repo maintainer. See each folder for author info.

---
For help running a specific game, open its folder and read the included `README.md`, or ask for step-by-step instructions.

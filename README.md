# Temple Run-Inspired Endless Runner

This repository contains a simple endless runner prototype built with [Pygame](https://www.pygame.org/) to help you explore "vibe coding" while recreating the core mechanics of the classic Temple Run mobile game.

## Features

- Basic endless runner loop with increasing difficulty.
- Player movement (run, jump, slide) using keyboard controls.
- Randomized obstacle generation.
- Simple scoring system based on distance traveled.

> **Note:** This is a desktop prototype meant to capture the feel of an endless runner. Re-creating the full Temple Run game (3D graphics, mobile touch controls, etc.) is far beyond the scope of a quick coding session.

## Requirements

- Python 3.9+
- `pip`
- A virtual environment tool such as `venv` (optional but recommended)

## Getting Started

1. **Clone the repository** (if you have not already):
   ```bash
   git clone https://github.com/<your-username>/sparkspark6969.git
   cd sparkspark6969
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   # On macOS/Linux
   source .venv/bin/activate
   # On Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game:**
   ```bash
   python main.py
   ```

## Controls

- `Space` — Jump
- `Left Shift` — Slide
- `Esc` — Quit game

## Gameplay Notes

- Obstacles appear at random intervals. Time your jumps and slides to avoid them.
- Your score increases the longer you survive. The game gradually becomes faster to increase difficulty.
- Colliding with an obstacle ends the run and shows your final score. Press `Space` to restart.

## Next Steps

Feel free to extend this prototype by adding:

- Animations and sprite art
- Power-ups and collectible coins
- Mobile-friendly controls
- Sound effects and music
- Leaderboards or score saving

Enjoy experimenting and vibe coding!

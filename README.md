# PeaceBreak
> **Rebuild. Survive. Resist.**

A 2D real-time strategy city-building game where players reconstruct a war-torn city 
under periodic missile bombardment. Every building you place is an act of resistance.

**itch.io:** https://amiellee.itch.io/peacebreak

---

## United Nations SDG Alignment

PeaceBreak is a game grounded in three United Nations Sustainable Development Goals:

| SDG | Connection to Gameplay |
|-----|----------------------|
| **SDG 9:** Industry, Innovation & Infrastructure | Players build and upgrade resilient infrastructure. The upgrade system (Brick to Concrete to Gold) models innovation investment. Bombing simulates infrastructure fragility under conflict. |
| **SDG 11:** Sustainable Cities & Communities | Players manage a city with housing, healthcare, education, energy, and transportation. Placement restrictions model responsible urban planning. |
| **SDG 16:** Peace, Justice & Strong Institutions | Bombing events are framed as consequences of conflict and institutional failure. War alert messages reference real humanitarian consequences throughout gameplay. |

---

## Gameplay Overview

- Make your city last 3 minutes in an active war zone
- Place buildings on designated grey paved tiles to grow your city
- Earn income and health bonuses every 10 seconds based on your buildings
- Upgrade buildings through three tiers: **Brick to Concrete to Gold**
- Survive periodic missile strikes that target and degrade your buildings
- Manage your funds, if money or lifeline hits 0, the game ends
- Score is calculated based on buildings placed, upgrades, health, funds, and survival time
- Top scores are saved to a leaderboard backed by a SQLite database

---

## Building Types

| Building | Cost | Income | Lifeline |
|----------|------|-------------|---------------|
| House | $10 | +$5 | - |
| Apartment | $18 | +$10 | - |
| Hospital | $30 | +$5 | +10 |
| School | $24 | +$3 | +5 |
| Power Plant | $28 | +$32 | - |
| Airport | $40 | +$25 | - |

**Upgrade costs:** Brick to Concrete costs $15, Concrete to Gold costs $50

---

## Controls

| Input | Action |
|-------|--------|
| `B` | Open/close build menu |
| `Left Click` (on menu) | Select building type |
| `Left Click` (on grey tile) | Place selected building |
| `Left Click` (on building) | Upgrade building |
| `R` | Return to title screen from leaderboard |
| `ESC` | Go back/quit |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Game Engine | Python 3 + Pygame |
| Tile Map | pytmx |
| Database | SQLite3 |
| Packaging | PyInstaller |
| Deployment | itch.io |

---

## Project Structure
```
PeaceBreak/
├── game/
│   ├── main.py          # Game loop, state machine, event handling
│   ├── settings.py      # Global constants and configuration
│   ├── assets.py        # Asset loading with PyInstaller path resolution
│   ├── buildings.py     # Building data, placement, upgrade, bonus logic
│   ├── bomb.py          # Missile system and building degradation
│   ├── money.py         # Fund tracking and income cap
│   ├── people.py        # Citizen sprites and movement
│   ├── map_renderer.py  # TMX tile map and building rendering
│   ├── ui.py            # All screen and HUD rendering
│   ├── message_box.py   # Animated contextual message boxes
│   ├── leaderboard.py   # Score persistence and leaderboard logic
│   ├── database.py      # SQLite connection and schema management
│   └── effects.py       # Screen shake utility
├── assets/
│   ├── images/          # Sprites, backgrounds, UI panels
│   ├── buildings/       # Building sprites (brick/concrete/gold per type)
│   ├── sounds/          # BOOM.wav, CLANG.wav, background_music.wav
│   └── world.tmx        # Tiled map file
├── data/
│   └── PeaceBreak.db    # SQLite database (auto-created on first launch)
└── README.md
```

---

## Running from Source Code

First, install the following requirements:
```bash
pip install pygame pytmx pyinstaller
```

Then, run the game!
```bash
cd game
python main.py
```

---

## Play Now

**itch.io:** https://amiellee.itch.io/peacebreak

No Python installation is required, just download and run!

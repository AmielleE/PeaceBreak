# Peace Break

Peace Break is a 2D strategy-based city-building game about infrastructure, resilience, and survival during conflict. Instead of focusing on combat, the game challenges players to build and manage a city, protect essential services, and recover from periodic attacks that damage civilian infrastructure.

The goal is to keep the city functioning, maintain population growth, and make smart decisions about construction, rebuilding, and resource use.

## Overview

Players build and manage a small city by placing structures such as housing and other essential infrastructure on a grid-based map. Each building has costs and durability, so every placement affects both city growth and long-term survival.

As the game progresses, attacks damage existing structures. Players must respond by rebuilding, managing resources carefully, and maintaining the city under pressure.

Peace Break is inspired by base-building mechanics, but its focus is on sustainability, resilience, and the human impact of conflict.

## Core Features

- Start a new game session
- View the city map and building grid
- Track player resources and turn number
- Select and place buildings on valid grid tiles
- Prevent invalid placement on occupied tiles
- Prevent placement when resources are insufficient
- Deduct resources after successful building placement
- Advance turns and update city resources
- Trigger raid or bombing events during gameplay
- Apply damage to structures and remove destroyed buildings
- Show feedback messages for important actions and events
- Support saving and loading game data with SQLite

## Gameplay Focus

Peace Break is designed around:
- city planning
- infrastructure durability
- resource management
- recovery after attacks
- strategic decision-making under pressure

The game connects to themes of sustainable infrastructure, resilient communities, and the social consequences of conflict.

## Tech Stack

- **Python**
- **Pygame**
- **PySimpleGUI**
- **SQLite**

## Project Structure

Typical important files and folders include:

- `game/main.py` — main entry point
- `game/` — core game logic modules
- `data/` — game data
- `sounds/` — audio assets
- `buildings/` — building assets
- `world.tmx` — map file
- `title_screen.png` — title screen asset

## Running the Game

Install dependencies first:

```bash
pip install pygame pysimplegui

import json
import os
import pygame
import sys
import sqlite3
from database import update_best_score, get_leaderboard_as_dicts
from buildings import get_unique_buildings

LEADERBOARD_FILE = "leaderboard.json"

def get_leaderboard_path():
    # Save next to the exe, not inside the bundle
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "leaderboard.json")
    return "leaderboard.json"

def load_leaderboard():
    # Load from SQLite, fall back to JSON if DB is empty
    try:
        entries = get_leaderboard_as_dicts()
        if entries:
            return entries
    except Exception as e:
        print(f"[leaderboard] DB load failed: {e}")

    # Fallback to JSON
    path = get_leaderboard_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_leaderboard(leaderboard):
    # Save to JSON as backup.
    path = get_leaderboard_path()
    try:
        with open(path, "w") as f:
            json.dump(leaderboard[:10], f, indent=4)
    except Exception as e:
        print(f"[leaderboard] JSON save failed: {e}")

# Add a new score and keep top 10
def add_score(leaderboard, name, score):
    # Save to database
    try:
        update_best_score(name, score)
    except Exception as e:
        print(f"[leaderboard] DB score update failed: {e}")

    # Update in-memory list and JSON backup
    leaderboard.append({"name": name, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    save_leaderboard(leaderboard[:10])

# Calculate a player's score based on game state
def calculate_score(money_system, player_health, buildings, start_time, game_duration):
    unique = get_unique_buildings(buildings)
    total_buildings = len(unique)

    upgraded_once  = sum(1 for b in unique if b["level"] >= 1)
    upgraded_fully = sum(1 for b in unique if b["level"] == 2)

    # Survival bonus: how long they lasted as a fraction
    elapsed = pygame.time.get_ticks() - start_time
    survival_ratio = min(elapsed / game_duration, 1.0)
    survival_bonus = int(survival_ratio * 300)

    # SDG-weighted building types
    SDG_WEIGHTS = {
        "hospital": 15, # for SDG 11
        "school": 12, # for SDG 11
        "power": 10, # for SDG 9
        "air": 8, # for SDG 9
        "apt": 6, # for SDG 11
        "house": 4, # for SDG 11
    }
    building_score = sum(SDG_WEIGHTS.get(b["type"], 4) for b in unique)

    score = (
        building_score +
        upgraded_once  * 20 +
        upgraded_fully * 40 +
        int(money_system.money * 0.5) +
        player_health  * 2 +
        survival_bonus
    )

    return score, total_buildings, upgraded_fully

def get_top_leaderboard(limit=10):
    # Get top scores directly from database
    try:
        return get_leaderboard_as_dicts(limit)
    except Exception as e:
        print(f"[leaderboard] DB fetch failed: {e}")
        return []
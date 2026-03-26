import json
import os
import pygame
import sys

LEADERBOARD_FILE = "leaderboard.json"

def get_leaderboard_path():
    # Save next to the exe, not inside the bundle
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "leaderboard.json")
    return "leaderboard.json"

# Load leaderboard from file
def load_leaderboard(filename="leaderboard.json"):
    path = get_leaderboard_path()
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

# Save leaderboard to file
def save_leaderboard(leaderboard):
    path = get_leaderboard_path()
    with open(path, "w") as f:
        json.dump(leaderboard[:10], f, indent=4)

# Add a new score and keep top 10
def add_score(leaderboard, name, score):
    leaderboard.append({"name": name, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    save_leaderboard(leaderboard)

# Calculate a player's score based on game state
def calculate_score(money_system, player_health, buildings, start_time, game_duration):
    from buildings import get_unique_buildings

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
        "hospital": 15,  # SDG 3 / SDG 11
        "school":   12,  # SDG 4 / SDG 11
        "power":    10,  # SDG 9
        "air":      8,   # SDG 9
        "apt":      6,   # SDG 11
        "house":    4,   # SDG 11
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

# Get top N leaderboard entries (default 10)
def get_top_leaderboard(leaderboard, top_n=10):
    return leaderboard[:top_n]


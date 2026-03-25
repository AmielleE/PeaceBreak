import json
import os
import pygame

LEADERBOARD_FILE = "leaderboard.json"

# Load leaderboard from file
def load_leaderboard(filename="leaderboard.json"):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return json.load(f)

def draw_leaderboard(screen, leaderboard, x=50, y=50, font_size=30):
    import pygame
    font = pygame.font.SysFont(None, font_size)
    title_text = font.render("Leaderboard", True, (255, 255, 255))
    screen.blit(title_text, (x, y))
    for i, entry in enumerate(leaderboard):
        name = entry.get("name", "Unknown")
        score = entry.get("score", 0)
        entry_text = font.render(f"{i+1}. {name} - {score}", True, (255, 255, 255))
        screen.blit(entry_text, (x, y + (i + 1) * (font_size + 5)))

# Save leaderboard to file
def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard[:10], f, indent=4)

# Add a new score and keep top 10
def add_score(leaderboard, name, score):
    leaderboard.append({"name": name, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    save_leaderboard(leaderboard)

# Calculate a player's score based on game state
def calculate_score(money_system, player_health, buildings):
    # Count unique buildings
    unique_buildings = set(id(b) for b in buildings.values())

    # Count upgraded buildings
    seen = set()
    upgraded = 0
    for b in buildings.values():
        bid = id(b)
        if bid not in seen:
            seen.add(bid)
            if b["level"] > 0:
                upgraded += 1

    score = (
        money_system.money * 2 +
        player_health * 3 +
        len(unique_buildings) * 5 +
        upgraded * 10
    )
    return score, len(unique_buildings), upgraded

# Get top N leaderboard entries (default 10)
def get_top_leaderboard(leaderboard, top_n=10):
    return leaderboard[:top_n]
import json
import os
import pygame

LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard(filename=LEADERBOARD_FILE):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return json.load(f)

def save_leaderboard(leaderboard, filename=LEADERBOARD_FILE):
    with open(filename, "w") as f:
        json.dump(leaderboard[:10], f, indent=4)

def add_score(leaderboard, name, score, filename=LEADERBOARD_FILE):
    leaderboard.append({"name": name, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    save_leaderboard(leaderboard, filename)
    return leaderboard

def draw_leaderboard_list(screen, leaderboard, x=50, y=50, font_size=30):
    font = pygame.font.SysFont(None, font_size)
    title_text = font.render("Leaderboard", True, (255, 255, 255))
    screen.blit(title_text, (x, y))

    for i, entry in enumerate(leaderboard[:10]):
        name = entry.get("name", "Unknown")
        score = entry.get("score", 0)
        entry_text = font.render(f"{i+1}. {name} - {score}", True, (255, 255, 255))
        screen.blit(entry_text, (x, y + (i + 1) * (font_size + 5)))

def calculate_score(money_system, player_health, buildings):
    unique_buildings = set(id(b) for b in buildings.values())

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

def get_top_leaderboard(leaderboard, top_n=10):
    return leaderboard[:top_n]
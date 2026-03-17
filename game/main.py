import pygame
import pytmx
import os
import json
from money import MoneySystem
from bomb import BombingEvent
import random

# Constants
TITLE = "PeaceBreak"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 40, 40)
BRIGHT_RED = (255, 70, 70)
DARK_BLUE = (20, 30, 60)

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Temporary display so pytmx can safely use convert()
screen = pygame.display.set_mode((1, 1))
pygame.display.set_caption(TITLE)

clock = pygame.time.Clock()

# Load map
current_dir = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(current_dir, "..", "assets", "world.tmx")
map_path = os.path.abspath(map_path)
tmx_data = pytmx.util_pygame.load_pygame(map_path)

# Map size
map_pixel_width = tmx_data.width * tmx_data.tilewidth
map_pixel_height = tmx_data.height * tmx_data.tileheight

# Zoom
SCALE = 0.28

scaled_tile_width = int(tmx_data.tilewidth * SCALE)
scaled_tile_height = int(tmx_data.tileheight * SCALE)
scaled_map_width = int(map_pixel_width * SCALE)
scaled_map_height = int(map_pixel_height * SCALE)

# Final window size matches scaled map
SCREEN_WIDTH = scaled_map_width
SCREEN_HEIGHT = scaled_map_height

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)

# Fonts
font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 84)
subtitle_font = pygame.font.SysFont(None, 40)
button_font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 28)

# Title screen image
title_bg = None
title_bg_path = os.path.join(current_dir, "..", "assets", "title_screen.png")
if os.path.exists(title_bg_path):
    title_bg = pygame.image.load(title_bg_path).convert()
    title_bg = pygame.transform.scale(title_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Bomb sound path
sound_path = os.path.join(current_dir, "..", "assets", "sounds", "BOOM.wav")

# Building placement sound
clang_sound_path = os.path.join(current_dir, "..", "assets", "sounds", "CLANG.wav")
if os.path.exists(clang_sound_path):
    clang_sound = pygame.mixer.Sound(clang_sound_path)
else:
    clang_sound = None

# Building images
building_images = {}
types = ["house", "apt", "hospital", "air", "power", "school"]
materials = ["brick", "concrete", "gold"]

for b_type in types:
    building_images[b_type] = []
    for mat in materials:
        path = os.path.join(current_dir, "..", f"assets/buildings/{b_type}_{mat}.png")
        img = pygame.image.load(path).convert_alpha()
        building_images[b_type].append(img)

# Load leaderboard
LEADERBOARD_FILE = "leaderboard.json"
leaderboard = []

if os.path.exists(LEADERBOARD_FILE):
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            content = f.read().strip()
            if content:
                leaderboard = json.loads(content)
    except json.JSONDecodeError:
        print("Leaderboard file is corrupted. Resetting.")
        leaderboard = []

# Game state variables
money_system = None
bombing = None
player_health = 100
game_over = False
message = ""
message_timer = 0
buildings = {}
game_state = "title"
player_name = ""
game_over_reason = ""

GAME_DURATION = 180000  # 3 minutes in ms
start_time = 0

play_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 140, 200, 70)

# Reset game
def reset_game():
    global money_system, bombing, player_health, game_over
    global message, message_timer, buildings
    global start_time

    money_system = MoneySystem(start_amount=50, increment=10, interval=3000)
    bombing = BombingEvent(interval=30000, damage=20, shake_duration=500)
    bombing.load_sound(sound_path)

    player_health = 100
    game_over = False
    message = ""
    message_timer = 0
    buildings = {}
    
    start_time = pygame.time.get_ticks()

def calculate_score():
    # unique buildings by id
    unique_buildings = set(id(b) for b in buildings.values())

    total_buildings = len(unique_buildings)
    upgraded = sum(1 for b in unique_buildings if buildings[list(buildings.keys())[0]]["level"] > 0)  # ❌ old wrong way

    # Better: get unique building dicts
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
        total_buildings * 5 +
        upgraded * 10
    )
    return score, total_buildings, upgraded

def save_score(name, score):
    leaderboard.append({"name": name, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard[:10], f, indent=4)

# Name input with map background
def draw_name_input():
    # Draw map in background
    draw_map_offset()
    
    # Overlay semi-transparent dark layer for readability
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Text
    text = font.render("Enter Name:", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

    name_surface = font.render(player_name, True, WHITE)
    screen.blit(name_surface, (SCREEN_WIDTH // 2 - name_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

# Leaderboard with map background
def draw_leaderboard():
    # Draw map in background
    draw_map_offset()
    
    # Overlay semi-transparent dark layer for readability
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Title
    title = title_font.render("Leaderboard", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width() // 2, 50))

    # Show game over reason if it exists
    if game_over_reason:
        reason_text = font.render(game_over_reason, True, RED)
        screen.blit(reason_text, (SCREEN_WIDTH//2 - reason_text.get_width() // 2, 120))

    # Entries
    start_y = 150 if not game_over_reason else 160
    for i, entry in enumerate(leaderboard[:10]):
        line = font.render(f"{i+1}. {entry['name']} - {entry['score']}", True, WHITE)
        screen.blit(line, (SCREEN_WIDTH//2 - line.get_width() // 2, start_y + i * 40))
    
    # Hint to go back
    hint = small_font.render("Press R to return", True, WHITE)
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 50))

# Tile utility functions
def can_place_building(tile_x, tile_y, width, height):
    for dx in range(width):
        for dy in range(height):
            check_tile = (tile_x + dx, tile_y + dy)

            if check_tile[0] < 0 or check_tile[1] < 0:
                return False
            if check_tile[0] >= tmx_data.width or check_tile[1] >= tmx_data.height:
                return False
            if check_tile in buildings:
                return False
    return True

def place_building(tile_x, tile_y, b_type, width=2, height=2):
    tiles = [(tile_x + dx, tile_y + dy) for dx in range(width) for dy in range(height)]
    building_data = {
        "type": b_type,
        "level": 0,
        "width": width,
        "height": height,
        "tiles": tiles
    }
    for t in tiles:
        buildings[t] = building_data

# Scale helper
def scale_surface(surface, scale):
    w = max(1, int(surface.get_width() * scale))
    h = max(1, int(surface.get_height() * scale))
    return pygame.transform.scale(surface, (w, h))

# Draw map layers
def draw_map_offset(dx=0, dy=0):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if gid == 0:
                    continue

                tile = tmx_data.get_tile_image_by_gid(gid)
                if not tile:
                    continue

                scaled_tile = scale_surface(tile, SCALE)
                img_w = scaled_tile.get_width()
                img_h = scaled_tile.get_height()

                # Bottom-align sprite to tile like Tiled
                draw_x = x * scaled_tile_width + dx
                draw_y = (y + 1) * scaled_tile_height - img_h + dy

                if draw_x > SCREEN_WIDTH or draw_x + img_w < 0:
                    continue
                if draw_y > SCREEN_HEIGHT or draw_y + img_h < 0:
                    continue

                screen.blit(scaled_tile, (draw_x, draw_y))

# Draw buildings
def draw_buildings_offset(dx=0, dy=0):
    drawn = set()

    for b in buildings.values():
        if id(b) in drawn:
            continue
        drawn.add(id(b))

        img = building_images[b["type"]][b["level"]]

        draw_width = int(b["width"] * scaled_tile_width)
        draw_height = int(b["height"] * scaled_tile_height)
        img = pygame.transform.scale(img, (draw_width, draw_height))

        top_left = b["tiles"][0]
        draw_x = top_left[0] * scaled_tile_width + dx
        draw_y = top_left[1] * scaled_tile_height + dy

        screen.blit(img, (draw_x, draw_y))

# Draw game UI
def draw_ui_offset(dx=0, dy=0):
    global message

    money_system.draw(screen, font)

    # Health bar
    bar_x, bar_y = 20 + dx, 60 + dy
    bar_width, bar_height = 200, 20
    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    current_width = int(bar_width * (player_health / 100))
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, current_width, bar_height))
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)

    if message:
        elapsed = pygame.time.get_ticks() - message_timer
        if elapsed < 2000:
            alpha = 255 - int(elapsed / 2000 * 255)
            text_surface = font.render(message, True, WHITE)
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, (20 + dx, SCREEN_HEIGHT - 40 + dy))
        else:
            message = ""

# Draw title screen
def draw_title_screen():
    mouse_pos = pygame.mouse.get_pos()
    hovered = play_button.collidepoint(mouse_pos)

    if title_bg:
        screen.blit(title_bg, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 35))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill(DARK_BLUE)

        title_text = title_font.render("PeaceBreak", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        screen.blit(title_text, title_rect)

        subtitle_text = subtitle_font.render("Rebuild. Survive. Resist.", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 55))
        screen.blit(subtitle_text, subtitle_rect)

    button_color = BRIGHT_RED if hovered else RED
    pygame.draw.rect(screen, button_color, play_button, border_radius=12)
    pygame.draw.rect(screen, WHITE, play_button, width=3, border_radius=12)

    play_text = button_font.render("PLAY", True, WHITE)
    play_rect = play_text.get_rect(center=play_button.center)
    screen.blit(play_text, play_rect)

# Initial reset
reset_game()

# Main loop
running = True
shake_offset = (0, 0)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif game_state == "title":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button.collidepoint(event.pos):
                    player_name = ""
                    game_state = "name_input"

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    reset_game()
                    game_state = "name_input"
                    player_name = ""

        # name input
        elif game_state == "name_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    reset_game()
                    game_state = "game"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 10:
                        player_name += event.unicode

        elif game_state == "game":
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    game_state = "title"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    tile_x = int(mouse_x / scaled_tile_width)
                    tile_y = int(mouse_y / scaled_tile_height)
                    clicked_tile = (tile_x, tile_y)

                    if 0 <= tile_x < tmx_data.width and 0 <= tile_y < tmx_data.height:
                        if clicked_tile in buildings:
                            building = buildings[clicked_tile]
                            if building["level"] < 2:
                                building["level"] += 1
                                message = f"{building['type'].capitalize()} upgraded!"
                                money_system.change_money(-15, (mouse_x, mouse_y))
                            else:
                                message = f"{building['type'].capitalize()} fully upgraded!"
                        else:
                            b_type = random.choice(types)
                            width, height = 2, 2
                            if can_place_building(tile_x, tile_y, width, height):
                                place_building(tile_x, tile_y, b_type, width, height)
                                message = f"New {b_type} added!"
                                money_system.change_money(-5, (mouse_x, mouse_y))
                                if clang_sound:
                                    clang_sound.play()
                            else:
                                message = "Cannot place building here!"

                        message_timer = pygame.time.get_ticks()

    if game_state == "title":
        draw_title_screen()
    
    elif game_state == "name_input":
        draw_name_input()

    elif game_state == "game":
        current_time = pygame.time.get_ticks()
        # time end
        if current_time - start_time >= GAME_DURATION:
            score, total, upgraded = calculate_score()
            save_score(player_name, score)
            game_state = "leaderboard"

        # game over condition
        if player_health <= 0 or money_system.money <= 0:
            score, total, upgraded = calculate_score()
            save_score(player_name, score)
            
            # Set the reason for losing
            if player_health <= 0 and money_system.money <= 0:
                game_over_reason = "Game Over! Health and Money have fallen below 0"
            elif player_health <= 0:
                game_over_reason = "Game Over! Health has fallen below 0"
            else:
                game_over_reason = "Game Over! Money has fallen below 0"

            game_state = "leaderboard"
        
        building_count = len(set(id(b) for b in buildings.values()))
        bombing.interval = max(5000, 30000 - building_count * 400)

        # Only increment money if at least one building exists
        if len(buildings) > 0:
            money_system.update()

        player_health, shake_offset = bombing.update(player_health)

        screen.fill(BLACK)
        shake_x, shake_y = shake_offset
        draw_map_offset(shake_x, shake_y)
        draw_buildings_offset(shake_x, shake_y)
        draw_ui_offset(shake_x, shake_y)
    
    elif game_state == "leaderboard":
        draw_leaderboard()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_state = "title"

    pygame.display.update()
    clock.tick(60)

pygame.quit()
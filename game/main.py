import pygame
import pytmx
import os
import json
from money import MoneySystem
from bomb import BombingEvent

# Constants
TITLE = "PeaceBreak"

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 40, 40)
BRIGHT_RED = (255, 70, 70)
DARK_BLUE = (20, 30, 60)
GOLD = (255, 215, 0)
LIGHT_WOOD = (156, 104, 64)
DARK_WOOD = (92, 55, 30)
PANEL_BROWN = (70, 40, 20)
HIGHLIGHT = (255, 230, 120)

# -------------------------
# Building data
# -------------------------
BUILDING_DATA = {
    "house": {
        "label": "House",
        "cost": 10,
        "income": 1,
        "health": 0
    },
    "apt": {
        "label": "Apartment",
        "cost": 18,
        "income": 2,
        "health": 0
    },
    "hospital": {
        "label": "Hospital",
        "cost": 30,
        "income": 0,
        "health": 4
    },
    "school": {
        "label": "School",
        "cost": 24,
        "income": 0,
        "health": 2
    },
    "power": {
        "label": "Power Plant",
        "cost": 28,
        "income": 5,
        "health": 0
    },
    "air": {
        "label": "Airport",
        "cost": 40,
        "income": 8,
        "health": 0
    }
}

MENU_ORDER = ["house", "apt", "hospital", "school", "power", "air"]

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
SCALE = 0.27

scaled_tile_width = int(tmx_data.tilewidth * SCALE)
scaled_tile_height = int(tmx_data.tileheight * SCALE)
scaled_map_width = int(map_pixel_width * SCALE)
scaled_map_height = int(map_pixel_height * SCALE)

SCREEN_WIDTH = scaled_map_width
SCREEN_HEIGHT = scaled_map_height

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)

# Fonts
font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 84)
subtitle_font = pygame.font.SysFont(None, 40)
button_font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 24)
tiny_font = pygame.font.SysFont(None, 20)
menu_title_font = pygame.font.SysFont(None, 30)

# Title screen image
title_bg = None
title_bg_path = os.path.join(current_dir, "..", "assets", "images", "title_screen.png")
if os.path.exists(title_bg_path):
    title_bg = pygame.image.load(title_bg_path).convert()
    title_bg = pygame.transform.scale(title_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# -------------------------
# Optional build menu image
# -------------------------
menu_panel = None
menu_panel_path = os.path.join(current_dir, "..", "assets", "build_menu_panel.png")
if os.path.exists(menu_panel_path):
    menu_panel = pygame.image.load(menu_panel_path).convert_alpha()

# -------------------------
# Sound path
# -------------------------
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
menu_icons = {}

types = ["house", "apt", "hospital", "air", "power", "school"]
materials = ["brick", "concrete", "gold"]

for b_type in types:
    building_images[b_type] = []
    for mat in materials:
        path = os.path.join(current_dir, "..", f"assets/buildings/{b_type}_{mat}.png")
        img = pygame.image.load(path).convert_alpha()
        building_images[b_type].append(img)

    # brick version used as menu icon
    menu_icons[b_type] = building_images[b_type][0]

# -------------------------
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

# -------------------------
# Title button
# -------------------------
play_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 110, 200, 70)

# -------------------------
# Build menu state
# -------------------------
MENU_WIDTH = 240
MENU_X_CLOSED = SCREEN_WIDTH
MENU_X_OPEN = SCREEN_WIDTH - MENU_WIDTH
menu_x = MENU_X_CLOSED
menu_open = False
menu_speed = 24
selected_building = "house"

slot_rects = []

# -------------------------
# Bonus timing
# -------------------------
BONUS_INTERVAL = 5000
last_bonus_tick = 0

# Reset game
def reset_game():
    global money_system, bombing, player_health, game_over
    global message, message_timer, buildings
    global menu_open, menu_x, selected_building, last_bonus_tick
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

    menu_open = False
    menu_x = MENU_X_CLOSED
    selected_building = "house"
    last_bonus_tick = pygame.time.get_ticks()

# -------------------------
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

def get_unique_buildings():
    unique = []
    seen = set()
    for b in buildings.values():
        if id(b) not in seen:
            seen.add(id(b))
            unique.append(b)
    return unique

def apply_building_bonuses():
    global player_health, last_bonus_tick

    current_time = pygame.time.get_ticks()
    if current_time - last_bonus_tick < BONUS_INTERVAL:
        return

    last_bonus_tick = current_time

    total_income = 0
    total_health = 0

    for b in get_unique_buildings():
        b_type = b["type"]
        level_multiplier = b["level"] + 1
        data = BUILDING_DATA[b_type]
        total_income += data["income"] * level_multiplier
        total_health += data["health"] * level_multiplier

    if total_income > 0:
        money_system.change_money(total_income, (20, 20))

    if total_health > 0:
        player_health = min(100, player_health + total_health)

# -------------------------
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

    selected_label = BUILDING_DATA[selected_building]["label"] if selected_building else "None"
    help_text = small_font.render(f"B: Build Menu   Selected: {selected_label}", True, WHITE)
    screen.blit(help_text, (20, 90))

    if message:
        elapsed = pygame.time.get_ticks() - message_timer
        if elapsed < 2200:
            alpha = 255 - int(elapsed / 2200 * 255)
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

# -------------------------
# Menu slide animation
# -------------------------
def update_menu_animation():
    global menu_x

    if menu_open:
        if menu_x > MENU_X_OPEN:
            menu_x -= menu_speed
            if menu_x < MENU_X_OPEN:
                menu_x = MENU_X_OPEN
    else:
        if menu_x < MENU_X_CLOSED:
            menu_x += menu_speed
            if menu_x > MENU_X_CLOSED:
                menu_x = MENU_X_CLOSED

# -------------------------
# Draw build menu
# -------------------------
def draw_build_menu():
    global slot_rects

    if menu_x >= SCREEN_WIDTH:
        slot_rects = []
        return

    slot_rects = []

    panel_rect = pygame.Rect(menu_x, 0, MENU_WIDTH, SCREEN_HEIGHT)

    # draw panel image if available, else fallback panel
    if menu_panel:
        panel_scaled = pygame.transform.scale(menu_panel, (MENU_WIDTH, SCREEN_HEIGHT))
        screen.blit(panel_scaled, (menu_x, 0))
    else:
        pygame.draw.rect(screen, LIGHT_WOOD, panel_rect)
        pygame.draw.rect(screen, DARK_WOOD, panel_rect, 6)
        title_text = menu_title_font.render("Build Menu", True, WHITE)
        screen.blit(title_text, (menu_x + 48, 18))

    # slot layout
    slot_w = 188
    slot_h = 68
    slot_gap = 10
    start_y = 88

    mouse_pos = pygame.mouse.get_pos()
    hovered_type = None

    for i, b_type in enumerate(MENU_ORDER):
        slot_x = menu_x + 26
        slot_y = start_y + i * (slot_h + slot_gap)
        rect = pygame.Rect(slot_x, slot_y, slot_w, slot_h)
        slot_rects.append((rect, b_type))

        is_selected = (selected_building == b_type)
        is_hovered = rect.collidepoint(mouse_pos)

        if is_hovered:
            hovered_type = b_type

        # subtle backing
        pygame.draw.rect(screen, PANEL_BROWN, rect, border_radius=8)

        border_color = HIGHLIGHT if is_selected else WHITE
        border_width = 4 if is_selected else 2
        pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)

        # icon
        icon = menu_icons[b_type]
        icon_scaled = pygame.transform.scale(icon, (48, 48))
        screen.blit(icon_scaled, (rect.x + 8, rect.y + 10))

        # labels
        label = BUILDING_DATA[b_type]["label"]
        cost = BUILDING_DATA[b_type]["cost"]

        text1 = tiny_font.render(label, True, WHITE)
        text2 = tiny_font.render(f"${cost}", True, GOLD)

        screen.blit(text1, (rect.x + 64, rect.y + 12))
        screen.blit(text2, (rect.x + 64, rect.y + 36))

    # hover info box
    info_type = hovered_type if hovered_type else selected_building
    if info_type:
        draw_menu_info_box(info_type)

def draw_menu_info_box(b_type):
    data = BUILDING_DATA[b_type]

    box_w = 190
    box_h = 112
    box_x = max(10, menu_x - box_w - 10)
    box_y = SCREEN_HEIGHT - box_h - 18

    info_rect = pygame.Rect(box_x, box_y, box_w, box_h)
    pygame.draw.rect(screen, (35, 25, 18), info_rect, border_radius=10)
    pygame.draw.rect(screen, HIGHLIGHT, info_rect, 2, border_radius=10)

    lines = [
        data["label"],
        f"Cost: ${data['cost']}",
        f"Income: +{data['income']} / bonus tick",
        f"Health: +{data['health']} / bonus tick"
    ]

    for i, line in enumerate(lines):
        txt = tiny_font.render(line, True, WHITE)
        screen.blit(txt, (box_x + 12, box_y + 12 + i * 22))

# -------------------------
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
            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_r:
                    game_state = "title"

                elif not game_over and event.key == pygame.K_b:
                    menu_open = not menu_open

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not game_over:
                    click_handled = False

                    # menu clicks first
                    if menu_x < SCREEN_WIDTH:
                        for rect, b_type in slot_rects:
                            if rect.collidepoint(event.pos):
                                selected_building = b_type
                                message = f"{BUILDING_DATA[b_type]['label']} selected"
                                message_timer = pygame.time.get_ticks()
                                click_handled = True
                                break

                    if click_handled:
                        continue

                    # prevent map placement if clicking on visible menu area
                    if event.pos[0] >= menu_x and menu_x < SCREEN_WIDTH:
                        continue

                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    tile_x = int(mouse_x / scaled_tile_width)
                    tile_y = int(mouse_y / scaled_tile_height)
                    clicked_tile = (tile_x, tile_y)

                    if 0 <= tile_x < tmx_data.width and 0 <= tile_y < tmx_data.height:
                        if clicked_tile in buildings:
                            building = buildings[clicked_tile]
                            upgrade_cost = max(8, BUILDING_DATA[building["type"]]["cost"] // 2)

                            if building["level"] < 2:
                                if money_system.money >= upgrade_cost:
                                    building["level"] += 1
                                    message = f"{BUILDING_DATA[building['type']]['label']} upgraded!"
                                    money_system.change_money(-upgrade_cost, (mouse_x, mouse_y))
                                else:
                                    message = "Not enough money to upgrade!"
                            else:
                                message = f"{BUILDING_DATA[building['type']]['label']} fully upgraded!"
                        else:
                            b_type = selected_building
                            cost = BUILDING_DATA[b_type]["cost"]


                            b_type = random.choice(types)
                            width, height = 2, 2
                            if can_place_building(tile_x, tile_y, width, height):
                                place_building(tile_x, tile_y, b_type, width, height)
                                message = f"New {b_type} added!"
                                money_system.change_money(-5, (mouse_x, mouse_y))
                                if clang_sound:
                                    clang_sound.play()
                            else:
                                width, height = 2, 2
                                if can_place_building(tile_x, tile_y, width, height):
                                    place_building(tile_x, tile_y, b_type, width, height)
                                    message = f"Placed {BUILDING_DATA[b_type]['label']}!"
                                    money_system.change_money(-cost, (mouse_x, mouse_y))
                                else:
                                    message = "Cannot place building here!"

                        message_timer = pygame.time.get_ticks()

    if game_state == "title":
        draw_title_screen()
    
    elif game_state == "name_input":
        draw_name_input()

    elif game_state == "game":
        update_menu_animation()

        if not game_over:
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
            apply_building_bonuses()

        player_health, shake_offset = bombing.update(player_health)

        screen.fill(BLACK)
        shake_x, shake_y = shake_offset
        draw_map_offset(shake_x, shake_y)
        draw_buildings_offset(shake_x, shake_y)
        draw_ui_offset(shake_x, shake_y)
        draw_build_menu()
    
    elif game_state == "leaderboard":
        draw_leaderboard()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_state = "title"

    pygame.display.update()
    clock.tick(60)

pygame.quit()
from database import create_tables
create_tables()

import pygame
import pytmx
import os
import json
import random
import math
import glob
import sys

from settings import *
from assets import load_images, load_sounds, load_buildings
from ui import draw_title_screen, draw_name_input, draw_ui_offset, draw_build_menu, draw_menu_info_box, draw_leaderboard, draw_instructions_screen
from map_renderer import draw_map_offset, draw_buildings_offset, scale_surface, get_buildable_gids, draw_craters, get_tile_gid
from leaderboard import load_leaderboard, add_score, calculate_score
from effects import draw_bomb_animation, apply_screen_shake
from buildings import (
    BUILDING_DATA, MENU_ORDER, TYPES,
    can_place_building, place_building, get_unique_buildings,
    count_buildings, count_upgraded, apply_building_bonuses,
    try_upgrade_building
)
from money import MoneySystem
from bomb import BombingEvent
from people import load_people_sprites, update_people, draw_people
from message_box import MessageBox

# --- Pygame init ---
pygame.init()
pygame.mixer.init()

# Temporary display for pytmx
screen = pygame.display.set_mode((1, 1))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# --- Map loading ---
current_dir = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.abspath(os.path.join(current_dir, ".."))

map_path = os.path.join(base_path, "assets", "world.tmx")
tmx_data = pytmx.util_pygame.load_pygame(map_path)

map_pixel_width = tmx_data.width * tmx_data.tilewidth
map_pixel_height = tmx_data.height * tmx_data.tileheight

# Use rounded tile scaling and derive screen size from tile grid
scaled_tile_width = max(1, round(tmx_data.tilewidth * SCALE))
scaled_tile_height = max(1, round(tmx_data.tileheight * SCALE))
scaled_map_width = tmx_data.width * scaled_tile_width
scaled_map_height = tmx_data.height * scaled_tile_height

SCREEN_WIDTH = scaled_map_width
SCREEN_HEIGHT = scaled_map_height
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)

# --- Fonts ---
font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 84)
subtitle_font = pygame.font.SysFont(None, 40)
button_font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 28)
tiny_font = pygame.font.SysFont(None, 20)
menu_title_font = pygame.font.SysFont(None, 30)

# --- Load assets ---
images = load_images(current_dir, SCREEN_WIDTH, SCREEN_HEIGHT)
sounds = load_sounds(current_dir)
building_images, menu_icons, types = load_buildings(current_dir)

title_bg = images.get("title_bg")
menu_panel = images.get("menu_panel")
bomb_img = images.get("bomb")
crater_img = images.get("crater")
clang_sound = sounds.get("clang")
bomb_sound_path = sounds.get("bomb_path")
bgm_path = sounds.get("bgm_path")

#play music
def play_bgm():
    if bgm_path:
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(bgm_path)
                pygame.mixer.music.set_volume(0.13)  # adjust if too loud
                pygame.mixer.music.play(-1)  # loop forever
        except pygame.error as e:
            print(f"[music] Failed to play BGM: {e}")

def stop_bgm():
    pygame.mixer.music.stop()

# Load people sprites
load_people_sprites()

def get_buildable_tiles(tmx_data, buildings, buildable_gids, craters):
    crater_set = set(craters)
    tiles = []
    for y in range(tmx_data.height):
        for x in range(tmx_data.width):
            if (x, y) in buildings:
                continue
            if (x, y) in crater_set:
                continue
            gid = get_tile_gid(tmx_data, x, y)
            if gid in buildable_gids:
                tiles.append((x, y))
    return tiles

# --- Leaderboard ---
leaderboard = load_leaderboard() or []

# --- Game state ---
money_system = None
bombing = None
player_health = 100
game_over = False
buildings = {}
game_state = "title"
player_name = ""
game_over_reason = ""
people = []
last_person_spawn = 0
play_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 110, 200, 70)
quit_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 195, 200, 70)
instructions_continue_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 80, 170, 50)
instructions_back_button = pygame.Rect(SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT - 80, 170, 50)
leaderboard_back_button = pygame.Rect(SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT - 80, 180, 50)
leaderboard_quit_button = pygame.Rect(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT - 80, 180, 50)
menu_x = MENU_X_CLOSED = SCREEN_WIDTH
MENU_X_OPEN = SCREEN_WIDTH - MENU_WIDTH
menu_open = False
menu_speed = 24
selected_building = "house"
slot_rects = []
last_bonus_tick = 0
last_tip_time = 0
start_time = 0
corner_msg_box = MessageBox()
bottom_tip_box = MessageBox()
blocked_build_warning_tile = None
blocked_build_warning_time = 0
tip_sprite_images = []
current_tip_sprite = None
last_tip_box_timer = -1

WAR_MESSAGES = [
    ("Airstrike detected nearby.", "Civilian infrastructure is the first casualty of war.", "war"),
    ("Supply lines have been cut.", "Food and medicine shortages are spreading.", "war"),
    ("Hospitals are overwhelmed.", "SDG 3: Good Health depends on stability.", "war"),
    ("Power grid damaged.", "Without energy, cities cannot function.", "war"),
    ("Displacement camps forming.", "SDG 11: Safe cities require peace.", "war"),
    ("Bridges destroyed.", "SDG 9: Infrastructure enables recovery.", "war"),
    ("Schools closed due to conflict.", "An entire generation loses access to education.", "war"),
    ("International aid blocked.", "Corruption undermines SDG 16: Strong Institutions.", "war"),
    ("Refugee population rising.", "SDG 11 calls for inclusive, safe settlements.", "war"),
    ("Clean water access lost.", "Conflict destroys decades of development overnight.", "war"),
]

SDG_TIPS = [
    ("SDG 9: Build resilient infrastructure.", "Upgrade buildings to withstand future attacks.", "tip"),
    ("SDG 11: Sustainable cities need hospitals & schools.", "Invest in social infrastructure, not just housing.", "tip"),
    ("SDG 16: Peace enables development.", "Every bombing sets your city back years.", "tip"),
    ("Tip: Power plants multiply your income.", "Energy is the foundation of industrialization.", "tip"),
    ("Tip: Hospitals restore city health over time.", "Healthcare infrastructure saves lives.", "tip"),
    ("Tip: Upgrading buildings increases resilience.", "SDG 9 calls for innovation in infrastructure.", "tip"),
    ("Tip: Airports connect your city to the world.", "SDG 9: Foster innovation through connectivity.", "tip"),
    ("Tip: Balance growth with sustainability.", "More buildings = more bombing frequency.", "tip"),
    ("SDG 9: Over 1 billion people lack reliable electricity.", "Power plants are not a luxury — they are essential.", "tip"),
    ("SDG 11: 1 in 4 people live in informal settlements.", "Safe housing is a human right, not a privilege.", "tip"),
    ("SDG 16: Corruption costs $2.6 trillion annually.", "Strong institutions protect your city from within.", "tip"),
    ("Tip: Schools build long-term city resilience.", "Educated populations recover from conflict faster.", "tip"),
    ("SDG 9: Infrastructure investment drives GDP growth.", "Every dollar spent on infrastructure returns four.", "tip"),
    ("SDG 11: Green cities reduce disaster risk.", "Sustainable planning saves lives before crisis hits.", "tip"),
    ("Tip: Diversify your buildings.", "Cities that rely on one industry are fragile.", "tip"),
    ("SDG 16: 2 billion people live in conflict-affected areas.", "Peace is not guaranteed — it must be built.", "tip"),
    ("SDG 9: Innovation closes the development gap.", "Technology and infrastructure lift communities out of poverty.", "tip"),
    ("Tip: Upgrade hospitals early.", "Health infrastructure is your city's lifeline in war.", "tip"),
    ("SDG 11: Disaster-resilient cities save more lives.", "Build smart — not just fast.", "tip"),
    ("SDG 16: Access to justice protects the vulnerable.", "Without law, the powerful take from the powerless.", "tip"),
    ("Tip: Apartments house more people per tile.", "Dense housing is key to sustainable urban growth.", "tip"),
    ("SDG 9: 2.7 billion people lack internet access.", "Connectivity is modern infrastructure — build toward it.", "tip"),
    ("SDG 11: Public services define a city's character.", "Schools and hospitals matter more than monuments.", "tip"),
    ("Tip: A bombed city can be rebuilt.", "Resilience means starting over without giving up.", "tip"),
]

get_buildable_gids(tmx_data)


# --- Game functions ---
def reset_game():
    global money_system, bombing, player_health, game_over
    global buildings, corner_msg_box, bottom_tip_box
    global menu_open, menu_x, selected_building, last_bonus_tick
    global start_time, game_over_reason, last_tip_time
    global people, last_person_spawn, leaderboard
    global blocked_build_warning_tile, blocked_build_warning_time
    global current_tip_sprite, last_tip_box_timer

    money_system = MoneySystem(start_amount=50, increment=0, interval=3000)
    bombing = BombingEvent(interval=30000, damage=20, shake_duration=500, missile_speed=7)
    bombing.load_sound(bomb_sound_path)
    
    if clang_sound:
        clang_sound.set_volume(0.14)

    if bombing.sound:
        bombing.sound.set_volume(0.82)

    player_health = 100
    #msg_box = MessageBox()
    game_over = False
    buildings.clear()
    
    people.clear()
    last_person_spawn = pygame.time.get_ticks()
    
    game_over_reason = ""

    start_time = pygame.time.get_ticks()
    menu_x = MENU_X_CLOSED
    menu_open = False
    selected_building = "house"
    last_bonus_tick = pygame.time.get_ticks()
    last_tip_time = pygame.time.get_ticks()
    blocked_build_warning_tile = None
    blocked_build_warning_time = 0
    current_tip_sprite = None
    last_tip_box_timer = -1 
    
    corner_msg_box = MessageBox()
    bottom_tip_box = MessageBox()
    
    if bombing:
        bombing.craters.clear()
        bombing.crater_patches.clear()
    #bombing.craters.clear() if bombing else None

def draw_map_wrapper():
    draw_map_offset(screen, tmx_data, scaled_tile_width, scaled_tile_height, 0, 0)

def get_random_bomb_target():
    unique_buildings = list(get_unique_buildings(buildings))

    if unique_buildings:
        b = random.choice(unique_buildings)

        center_tile_x = b["tiles"][0][0] + b["width"] // 2
        center_tile_y = b["tiles"][0][1] + b["height"] // 2

        center_x = int((center_tile_x + 0.5) * scaled_tile_width)
        center_y = int((center_tile_y + 0.5) * scaled_tile_height)

        return (center_x, center_y), (center_tile_x, center_tile_y)

    min_x = int(SCREEN_WIDTH * 0.25)
    max_x = int(SCREEN_WIDTH * 0.75)
    min_y = int(SCREEN_HEIGHT * 0.18)
    max_y = int(SCREEN_HEIGHT * 0.82)

    rand_x = random.randint(min_x, max_x)
    rand_y = random.randint(min_y, max_y)

    tile_x = max(0, min(tmx_data.width - 1, rand_x // scaled_tile_width))
    tile_y = max(0, min(tmx_data.height - 1, rand_y // scaled_tile_height))

    return (rand_x, rand_y), (tile_x, tile_y)
# build warning

def draw_blocked_build_warning(screen, warning_tile, warning_time, current_time):
    if warning_tile is None:
        return

    if current_time - warning_time > 1200:
        return

    tile_x, tile_y = warning_tile

    bob_offset = int(math.sin((current_time - warning_time) * 0.01) * 6)

    center_x = tile_x * scaled_tile_width + scaled_tile_width // 2
    draw_y = tile_y * scaled_tile_height - 18 + bob_offset

    warning_font = pygame.font.SysFont(None, 34)
    text = warning_font.render("!", True, (255, 60, 60))
    outline = warning_font.render("!", True, (255, 255, 255))

    text_rect = text.get_rect(center=(center_x, draw_y))

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        screen.blit(outline, text_rect.move(dx, dy))

    screen.blit(text, text_rect)
    
def draw_game_over_overlay(screen, SCREEN_WIDTH, SCREEN_HEIGHT, title_font, font, small_font, game_over_reason):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    screen.blit(overlay, (0, 0))

    shadow_text = title_font.render("GAME OVER", True, (40, 0, 0))
    shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT // 2 - 87))
    screen.blit(shadow_text, shadow_rect)

    title_text = title_font.render("GAME OVER", True, (210, 30, 30))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90))
    screen.blit(title_text, title_rect)

    # Subtitle based on failure reason
    if game_over_reason == "money":
        line1 = "You didn't use your resources wisely."
        line2 = "Sustainable cities need responsible planning — SDG 11."
    elif game_over_reason == "health":
        line1 = "You failed to defend your city."
        line2 = "Peace, justice, and resilience matter — SDG 16."
    elif game_over_reason == "time":
        line1 = "Your city was not rebuilt in time."
        line2 = "Innovation and resilience require action — SDG 9."
    else:
        line1 = "Your city could not endure the conflict."
        line2 = "Recovery demands planning, resilience, and peace."

    subtitle_text = font.render(line1, True, (240, 240, 240))
    subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
    screen.blit(subtitle_text, subtitle_rect)

    sdg_text = small_font.render(line2, True, (220, 200, 120))
    sdg_rect = sdg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(sdg_text, sdg_rect)

    restart_text = small_font.render("Press Enter to continue", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
    screen.blit(restart_text, restart_rect)

def load_tip_sprites():
    global tip_sprite_images

    tip_sprite_images = []

    citizens_folder = os.path.join(base_path, "assets", "images", "citizens")
    if not os.path.exists(citizens_folder):
        print(f"[tip sprites] Folder not found: {citizens_folder}")
        return

    for file_path in glob.glob(os.path.join(citizens_folder, "*.png")):
        try:
            sprite = pygame.image.load(file_path).convert_alpha()

            target_h = 105
            scale = target_h / sprite.get_height()
            target_w = max(1, int(sprite.get_width() * scale))
            sprite = pygame.transform.scale(sprite, (target_w, target_h))

            tip_sprite_images.append(sprite)
            print(f"[tip sprites] Loaded: {os.path.basename(file_path)}")
        except pygame.error as e:
            print(f"[tip sprites] Failed to load {file_path}: {e}")


def update_tip_sprite_for_message():
    global current_tip_sprite, last_tip_box_timer

    if bottom_tip_box.active and bottom_tip_box.box_type == "game_tip":
        if bottom_tip_box.timer != last_tip_box_timer:
            last_tip_box_timer = bottom_tip_box.timer
            if tip_sprite_images:
                current_tip_sprite = random.choice(tip_sprite_images)
    else:
        current_tip_sprite = None
        last_tip_box_timer = -1


def draw_tip_sprite(screen):
    if not current_tip_sprite:
        return

    box_w = 480
    box_h = 110
    box_x = SCREEN_WIDTH // 2 - box_w // 2
    box_y = SCREEN_HEIGHT - box_h - 30

    gap = 2
    x = box_x - current_tip_sprite.get_width() - gap
    y = box_y + box_h - current_tip_sprite.get_height() - 2

    panel_w = current_tip_sprite.get_width() + 10
    panel_h = current_tip_sprite.get_height() + 10

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, 70), (0, 0, panel_w, panel_h), border_radius=8)

    screen.blit(panel, (x - 5, y - 5))
    screen.blit(current_tip_sprite, (x, y))


def draw_game_timer(screen, current_time, start_time):
    elapsed_ms = current_time - start_time
    remaining_ms = max(0, GAME_DURATION - elapsed_ms)
    remaining_seconds = remaining_ms // 1000

    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    timer_text = f"Time Left: {minutes:02}:{seconds:02}"

    timer_font = pygame.font.SysFont(None, 26)
    text_surf = timer_font.render(timer_text, True, (255, 255, 255))

    pad_x = 12
    pad_y = 6
    box_w = text_surf.get_width() + pad_x * 2
    box_h = text_surf.get_height() + pad_y * 2

    box_x = SCREEN_WIDTH // 2 - box_w // 2
    box_y = 10

    panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, 105), (0, 0, box_w, box_h), border_radius=10)
    pygame.draw.rect(panel, (220, 220, 220, 170), (0, 0, box_w, box_h), 2, border_radius=10)

    screen.blit(panel, (box_x, box_y))
    screen.blit(text_surf, (box_x + pad_x, box_y + pad_y))

def draw_building_preview(screen, mouse_pos):
    # only show preview during gameplay
    if game_state != "game" or game_over:
        return

    # don't show preview if mouse is over the right-side menu
    if mouse_pos[0] >= menu_x and menu_x < SCREEN_WIDTH:
        return

    tile_x = int(mouse_pos[0] / scaled_tile_width)
    tile_y = int(mouse_pos[1] / scaled_tile_height)

    width, height = 3, 3

    # stay inside map bounds
    if not (0 <= tile_x < tmx_data.width and 0 <= tile_y < tmx_data.height):
        return

    if (tile_x, tile_y) in buildings:
        return
    valid = can_place_building(
        buildings,
        tile_x,
        tile_y,
        width,
        height,
        tmx_data.width,
        tmx_data.height,
        tmx_data,
        BUILDABLE_GIDS,
        bombing.craters 
    )

    # choose preview color
    if valid:
        fill_color = (60, 220, 90, 70)
        border_color = (80, 255, 120)
    else:
        fill_color = (220, 60, 60, 70)
        border_color = (255, 90, 90)

    # draw each tile in the footprint
    for dx in range(width):
        for dy in range(height):
            preview_x = (tile_x + dx) * scaled_tile_width
            preview_y = (tile_y + dy) * scaled_tile_height

            # skip tiles outside visible map just in case
            if preview_x < 0 or preview_y < 0:
                continue

            tile_surface = pygame.Surface((scaled_tile_width, scaled_tile_height), pygame.SRCALPHA)
            tile_surface.fill(fill_color)
            screen.blit(tile_surface, (preview_x, preview_y))

            pygame.draw.rect(
                screen,
                border_color,
                (preview_x, preview_y, scaled_tile_width, scaled_tile_height),
                2
            )

load_tip_sprites()

# --- Initial reset ---
reset_game()

# --- Main loop ---
running = True
shake_offset = (0, 0)

while running:
    current_time = pygame.time.get_ticks()
    update_tip_sprite_for_message() 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- Title screen input ---
        elif game_state == "title":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button.collidepoint(event.pos):
                    player_name = ""
                    game_state = "name_input"
                elif quit_button.collidepoint(event.pos):
                    running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    player_name = ""
                    game_state = "name_input"
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # --- Name input ---
        elif game_state == "name_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name.strip():
                    game_state = "instructions"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    game_state = "title"
                else:
                    if len(player_name) < 10 and event.unicode.isprintable():
                        player_name += event.unicode
                        
        elif game_state == "instructions":
             if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if instructions_continue_button.collidepoint(event.pos):
                    reset_game()
                    play_bgm()
                    game_state = "game"
                elif instructions_back_button.collidepoint(event.pos):
                    game_state = "name_input"
             elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    play_bgm()
                    game_state = "game"
                elif event.key == pygame.K_ESCAPE:
                    game_state = "name_input"

        # --- Game input ---
        elif game_state == "game":
            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_RETURN:
                    game_state = "leaderboard"
                elif not game_over and event.key == pygame.K_b:
                    menu_open = not menu_open

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                click_handled = False
                
                # Menu clicks
                if menu_x < SCREEN_WIDTH:
                    for rect, b_type in slot_rects:
                        if rect.collidepoint(event.pos):
                            selected_building = b_type
                            corner_msg_box.show(f"{BUILDING_DATA[b_type]['label']} selected", "Click a tile to place it.", box_type="tip", position="corner")
                            click_handled = True
                            break

                if click_handled:
                    continue

                # Prevent clicks on menu area
                if event.pos[0] >= menu_x and menu_x < SCREEN_WIDTH:
                    continue

                mouse_x, mouse_y = event.pos
                tile_x = int(mouse_x / scaled_tile_width)
                tile_y = int(mouse_y / scaled_tile_height)
                clicked_tile = (tile_x, tile_y)

                if 0 <= tile_x < tmx_data.width and 0 <= tile_y < tmx_data.height:
                    if clicked_tile in buildings:
                        building = buildings[clicked_tile]
                        result = try_upgrade_building(building, money_system, event.pos)
                        corner_msg_box.show(result, box_type="tip", position="corner")
                    else:
                        b_type = selected_building
                        width, height = 3, 3

                        footprint_tiles = []
                        for dx in range(width):
                            for dy in range(height):
                                footprint_tiles.append((tile_x + dx, tile_y + dy))

                        crater_set = set(bombing.craters)

                        if any(t in crater_set for t in footprint_tiles):
                            blocked_build_warning_tile = (tile_x + width // 2, tile_y)
                            blocked_build_warning_time = pygame.time.get_ticks()
                            corner_msg_box.show("Cannot build here!", "Repair the crater first.", box_type="event", position="corner")

                        elif can_place_building(buildings, tile_x, tile_y, width, height, tmx_data.width, tmx_data.height, tmx_data, BUILDABLE_GIDS, bombing.craters):
                            place_building(buildings, tile_x, tile_y, selected_building, width, height)
                            corner_msg_box.show(f"{BUILDING_DATA[selected_building]['label']} placed!", "Your city grows.", box_type="tip", position ="corner")
                            money_system.change_money(-BUILDING_DATA[selected_building]['cost'], (mouse_x, mouse_y))
                            if clang_sound:
                                clang_sound.play()
                        else:
                            corner_msg_box.show("Cannot place here!", "Build only on paved grey areas.", box_type="event", position="corner")

        # --- Leaderboard input ---
        elif game_state == "leaderboard":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if leaderboard_back_button.collidepoint(event.pos):
                    stop_bgm()
                    game_state = "title"
                elif leaderboard_quit_button.collidepoint(event.pos):
                    running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_state = "title"
                elif event.key == pygame.K_ESCAPE:
                    running = False
    # --- Game logic ---
    if game_state == "title":
        draw_title_screen(
            screen, title_bg, SCREEN_WIDTH, SCREEN_HEIGHT,
            play_button, quit_button,
            title_font, subtitle_font, button_font
        )
    
    elif game_state == "name_input":
        draw_name_input(screen, draw_map_wrapper, SCREEN_WIDTH, SCREEN_HEIGHT, font, player_name)
    
    elif game_state == "instructions":
        draw_map_wrapper()
        draw_instructions_screen(screen,SCREEN_WIDTH,SCREEN_HEIGHT,title_font,font,small_font,instructions_continue_button,instructions_back_button)
    
    elif game_state == "game":
        # Menu animation
        if menu_open and menu_x > MENU_X_OPEN:
            menu_x -= menu_speed
        elif not menu_open and menu_x < MENU_X_CLOSED:
            menu_x += menu_speed
        menu_x = max(MENU_X_OPEN, min(menu_x, MENU_X_CLOSED))

        # Tips
        if current_time - last_tip_time > TIP_INTERVAL:
            last_tip_time = current_time

            if random.random() < 0.45:
                msg, sub, _ = random.choice(WAR_MESSAGES)
                bottom_tip_box.show(msg, sub, duration=7000, box_type="war", position="bottom")
            else:
                msg, sub, _ = random.choice(SDG_TIPS)
                bottom_tip_box.show(msg, sub, duration=7000, box_type="game_tip", position="bottom")

        # End game conditions
        if not game_over and (current_time - start_time >= GAME_DURATION or player_health <= 0 or money_system.money <= 0):
            if player_health <= 0:
                game_over_reason = "health"
            elif money_system.money <= 0:
                game_over_reason = "money"
            else:
                game_over_reason = "time"

            score, total, upgraded = calculate_score(
                money_system,
                player_health,
                buildings,
                start_time,
                GAME_DURATION
            )
            add_score(leaderboard, player_name, score)
            leaderboard = load_leaderboard()

            stop_bgm()
            game_over = True

        if not game_over:
            # Bombing interval scales with city size
            building_count = len(get_unique_buildings(buildings))
            base_interval = max(5000, 30000 - building_count * 400)

            elapsed = current_time - start_time
            if elapsed > GAME_DURATION // 2:
                base_interval = int(base_interval * 0.3)  # adjust speed

            bombing.interval = max(3500, base_interval)

            # Money and bonuses
            money_system.update()
            if buildings:
                player_health, last_bonus_tick = apply_building_bonuses(
                    buildings,
                    money_system,
                    player_health,
                    last_bonus_tick,
                    current_time,
                    BONUS_INTERVAL
                )

            # Low money warning
            if money_system.money < 50 and not corner_msg_box.active:
                corner_msg_box.show(
                    "Funds critically low!",
                    "If your money hits $0, you lose the game.",
                    duration=3000,
                    box_type="war",
                    position="corner"
                )

            if blocked_build_warning_tile is not None:
                if current_time - blocked_build_warning_time > 1200:
                    blocked_build_warning_tile = None

            # Bombing update
            buildable_tiles = get_buildable_tiles(tmx_data, buildings, BUILDABLE_GIDS, bombing.craters)

            bomb_target_pos, bomb_target_tile = get_random_bomb_target()
            player_health, shake_offset, bombed = bombing.update(
                player_health,
                buildable_tiles,
                buildings,
                bomb_target_pos,
                bomb_target_tile
            )

            if bombed:
                corner_msg_box.show(
                    "Your city was bombed!",
                    "Rebuild and stay resilient — SDG 9.",
                    box_type="war",
                    position="corner"
                )

            # people update
            last_person_spawn = update_people(
                people,
                buildings,
                scaled_tile_width,
                scaled_tile_height,
                last_person_spawn,
                current_time
            )       

        # --- Drawing ---
        screen.fill(BLACK)
        if game_over:
            shake_x, shake_y = 0, 0
        else:
            shake_x, shake_y = shake_offset

        draw_map_offset(screen, tmx_data, scaled_tile_width, scaled_tile_height, shake_x, shake_y)
        draw_craters(screen, bombing.crater_patches, crater_img, scaled_tile_width, scaled_tile_height, shake_x, shake_y)        
        draw_buildings_offset(screen, buildings, building_images, scaled_tile_width, scaled_tile_height, shake_x, shake_y)
        draw_building_preview(screen, pygame.mouse.get_pos())
        bombing.draw(screen, shake_x, shake_y)
        draw_people(screen, people)
        
        draw_blocked_build_warning(screen, blocked_build_warning_tile, blocked_build_warning_time, current_time)
        draw_ui_offset(screen, money_system, font, small_font, player_health, selected_building, BUILDING_DATA, SCREEN_HEIGHT)
        draw_game_timer(screen, current_time, start_time)
        
        bottom_tip_box.draw(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        draw_tip_sprite(screen)
        corner_msg_box.draw(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        slot_rects, hovered_type = draw_build_menu(screen, menu_x, SCREEN_WIDTH, MENU_WIDTH, menu_panel, menu_icons, BUILDING_DATA, selected_building, tiny_font, menu_title_font, SCREEN_HEIGHT)
        if game_over:
            draw_game_over_overlay(
                screen,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                title_font,
                font,
                small_font,
                game_over_reason
            )

    elif game_state == "leaderboard":
        draw_leaderboard(
            screen, draw_map_wrapper, SCREEN_WIDTH, SCREEN_HEIGHT,
            leaderboard, title_font, font, small_font, game_over_reason,
            leaderboard_back_button, leaderboard_quit_button
        )
       
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_state = "title"

    pygame.display.update()
    clock.tick(60)

pygame.quit()
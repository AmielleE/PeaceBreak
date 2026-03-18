import pygame
import pytmx
import os
import json
import random

from settings import *
from assets import load_images, load_sounds, load_buildings
from ui import draw_title_screen, draw_name_input, draw_ui_offset, draw_build_menu, draw_menu_info_box
from map_renderer import draw_map_offset, draw_buildings_offset, scale_surface
from leaderboard import load_leaderboard, add_score, draw_leaderboard
from effects import draw_bomb_animation, apply_screen_shake
from buildings import (
    BUILDING_DATA, MENU_ORDER, TYPES,
    can_place_building, place_building, get_unique_buildings,
    count_buildings, count_upgraded, apply_building_bonuses,
    try_upgrade_building
)
from money import MoneySystem
from bomb import BombingEvent

# --- Pygame init ---
pygame.init()
pygame.mixer.init()

# Temporary display for pytmx
screen = pygame.display.set_mode((1, 1))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# --- Map loading ---
current_dir = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.abspath(os.path.join(current_dir, "..", "assets", "world.tmx"))
tmx_data = pytmx.util_pygame.load_pygame(map_path)

map_pixel_width = tmx_data.width * tmx_data.tilewidth
map_pixel_height = tmx_data.height * tmx_data.tileheight

scaled_tile_width = int(tmx_data.tilewidth * SCALE)
scaled_tile_height = int(tmx_data.tileheight * SCALE)
scaled_map_width = int(map_pixel_width * SCALE)
scaled_map_height = int(map_pixel_height * SCALE)

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
clang_sound = sounds.get("clang")
bomb_sound_path = sounds.get("bomb_path")

# --- Leaderboard ---
leaderboard = load_leaderboard()

# --- Game state ---
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
bomb_anim_active = False
bomb_anim_start = 0
play_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 140, 200, 70)
menu_x = MENU_X_CLOSED = SCREEN_WIDTH
MENU_X_OPEN = SCREEN_WIDTH - MENU_WIDTH
menu_open = False
menu_speed = 24
selected_building = "house"
slot_rects = []
last_bonus_tick = 0
last_tip_time = 0
start_time = 0

# --- Game functions ---
def reset_game():
    global money_system, bombing, player_health, game_over
    global message, message_timer, buildings
    global menu_open, menu_x, selected_building, last_bonus_tick
    global start_time

    money_system = MoneySystem(start_amount=50, increment=10, interval=3000)
    bombing = BombingEvent(interval=30000, damage=20, shake_duration=500)
    bombing.load_sound(bomb_sound_path)

    player_health = 100
    game_over = False
    message = ""
    message_timer = 0
    buildings.clear()
    
    start_time = pygame.time.get_ticks()
    menu_x = MENU_X_CLOSED
    menu_open = False
    selected_building = "house"
    last_bonus_tick = pygame.time.get_ticks()

def draw_map_wrapper():
    draw_map_offset(screen, tmx_data, scaled_tile_width, scaled_tile_height, 0, 0)

# --- Initial reset ---
reset_game()

# --- Main loop ---
running = True
shake_offset = (0, 0)

while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- Title screen input ---
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

        # --- Name input ---
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

        # --- Game input ---
        elif game_state == "game":
            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_r:
                    game_state = "title"
                elif not game_over and event.key == pygame.K_b:
                    menu_open = not menu_open

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                click_handled = False
                # Menu clicks
                if menu_x < SCREEN_WIDTH:
                    for rect, b_type in slot_rects:
                        if rect.collidepoint(event.pos):
                            selected_building = b_type
                            message = f"{BUILDING_DATA[b_type]['label']} selected"
                            message_timer = current_time
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
                        message = try_upgrade_building(building, money_system, event.pos)
                    else:
                        b_type = random.choice(types)
                        width, height = 2, 2
                        if can_place_building(buildings, tile_x, tile_y, width, height, tmx_data.width, tmx_data.height):
                            place_building(buildings, tile_x, tile_y, b_type, width, height)
                            message = f"New {b_type} added!"
                            money_system.change_money(-5, (mouse_x, mouse_y))
                            if clang_sound:
                                clang_sound.play()
                        else:
                            message = "Cannot place building here!"
                    message_timer = current_time

    # --- Game logic ---
    if game_state == "title":
        draw_title_screen(screen, title_bg, SCREEN_WIDTH, SCREEN_HEIGHT, play_button, title_font, subtitle_font, button_font)
    
    elif game_state == "name_input":
        draw_name_input(screen, draw_map_wrapper, SCREEN_WIDTH, SCREEN_HEIGHT, font, player_name)
    
    elif game_state == "game":
        # Menu animation
        if menu_open and menu_x > MENU_X_OPEN:
            menu_x -= menu_speed
        elif not menu_open and menu_x < MENU_X_CLOSED:
            menu_x += menu_speed
        menu_x = max(MENU_X_OPEN, min(menu_x, MENU_X_CLOSED))

        # Tips
        if current_time - last_tip_time > TIP_INTERVAL and len(buildings) > 0:
            message = random.choice([
                "Tip: Build power plants or airports to earn more income.",
                "Tip: Hospitals and schools increase your score more when upgraded.",
                "Tip: Upgrading buildings increases your score.",
                "War never waits. Be prepared.",
                "Infrastructure is the backbone of survival.",
                "No one is safe, but some are safer than others.",
                "Cities grow, but so do threats.",
                "City management is a delicate balance of growth and defense.",
                "Balance growth and survival carefully.",
                "Every decision has a cost.",
                "Tip: Don't let your money hit zero!",
                "Tip: Don't let your health hit zero!",
                "Cities grow, but so do threats.",
                "Rebuild faster than destruction strikes."
            ])
            message_timer = current_time
            last_tip_time = current_time

        # End game conditions
        if current_time - start_time >= GAME_DURATION or player_health <= 0 or money_system.money <= 0:
            score, total, upgraded = count_buildings(buildings), count_buildings(buildings), count_upgraded(buildings)
            add_score(player_name, score, leaderboard)
            game_state = "leaderboard"

        # Bombing interval
        building_count = len(get_unique_buildings(buildings))
        bombing.interval = max(5000, 30000 - building_count * 400)

        # Money and bonuses
        if buildings:
            money_system.update()
            player_health, last_bonus_tick = apply_building_bonuses(buildings, money_system, player_health, last_bonus_tick, current_time, BONUS_INTERVAL)

        # Bombing update
        prev_health = player_health
        player_health, shake_offset = bombing.update(player_health)
        if player_health < prev_health:
            bomb_anim_active = True
            bomb_anim_start = current_time

        # --- Drawing ---
        screen.fill(BLACK)
        shake_x, shake_y = shake_offset
        draw_map_offset(screen, tmx_data, scaled_tile_width, scaled_tile_height, shake_x, shake_y)
        draw_buildings_offset(screen, buildings, building_images, scaled_tile_width, scaled_tile_height, shake_x, shake_y)
        draw_ui_offset(screen, money_system, font, small_font, player_health, selected_building, BUILDING_DATA, message, message_timer, SCREEN_HEIGHT)
        bomb_anim_active = draw_bomb_animation(screen, bomb_img, bomb_anim_active, bomb_anim_start, 600, SCREEN_WIDTH, SCREEN_HEIGHT)
        slot_rects, hovered_type = draw_build_menu(screen, menu_x, SCREEN_WIDTH, MENU_WIDTH, menu_panel, menu_icons, BUILDING_DATA, selected_building, tiny_font, menu_title_font, SCREEN_HEIGHT)

    elif game_state == "leaderboard":
        draw_leaderboard(screen, draw_map_wrapper, SCREEN_WIDTH, SCREEN_HEIGHT, leaderboard, title_font, font, small_font, game_over_reason)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            game_state = "title"

    pygame.display.update()
    clock.tick(60)

pygame.quit()
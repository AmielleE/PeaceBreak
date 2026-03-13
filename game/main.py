import pygame
import pytmx
import os
from money import MoneySystem
from bomb import BombingEvent
import random

# -------------------------
# Constants
# -------------------------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650

# -------------------------
# Initialize pygame
# -------------------------
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PeaceBreak Prototype")

# -------------------------
# Load map
# -------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
map_path = os.path.join(current_dir, "..", "assets", "world.tmx")
map_path = os.path.abspath(map_path)
tmx_data = pytmx.util_pygame.load_pygame(map_path)

# -------------------------
# Map scaling
# -------------------------
map_pixel_width = tmx_data.width * tmx_data.tilewidth
map_pixel_height = tmx_data.height * tmx_data.tileheight
scale_x = SCREEN_WIDTH / map_pixel_width
scale_y = SCREEN_HEIGHT / map_pixel_height
SCALE = min(scale_x, scale_y)
offset_x = (SCREEN_WIDTH - map_pixel_width * SCALE) / 2
offset_y = (SCREEN_HEIGHT - map_pixel_height * SCALE) / 2

# -------------------------
# Font
# -------------------------
font = pygame.font.SysFont(None, 36)

# -------------------------
# Money system
# -------------------------
money_system = MoneySystem(start_amount=50, increment=10, interval=3000)

# -------------------------
# Bombing system
# -------------------------
bombing = BombingEvent(interval=30000, damage=20, shake_duration=500)
sound_path = os.path.join(current_dir, "..", "assets", "sounds", "explosion.wav")
bombing.load_sound(sound_path)

# -------------------------
# Player
# -------------------------
player_health = 100
game_over = False

# -------------------------
# Messages
# -------------------------
message = ""
message_timer = 0

# -------------------------
# Buildings
# -------------------------
buildings = {}  # key=(tile_x,tile_y) value={"type":..., "level":0-2}

# -------------------------
# Load building images
# -------------------------
building_images = {}
types = ["house", "apt", "hospital", "school", "air", "power"]
materials = ["brick", "concrete", "gold"]  # index 0,1,2

for b_type in types:
    building_images[b_type] = []
    for mat in materials:
        path = os.path.join(current_dir, "..", f"assets/buildings/{b_type}_{mat}.png")
        img = pygame.image.load(path)
        img = pygame.transform.scale(
            img,
            (int(tmx_data.tilewidth * SCALE), int(tmx_data.tileheight * SCALE))
        )
        building_images[b_type].append(img)

# -------------------------
# Draw tile layers
# -------------------------
def draw_map_offset(dx=0, dy=0):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    tile = pygame.transform.scale(
                        tile,
                        (int(tmx_data.tilewidth*SCALE), int(tmx_data.tileheight*SCALE))
                    )
                    screen.blit(
                        tile,
                        (offset_x + x*tmx_data.tilewidth*SCALE + dx,
                         offset_y + y*tmx_data.tileheight*SCALE + dy)
                    )

# -------------------------
# Draw buildings
# -------------------------
def draw_buildings_offset(dx=0, dy=0):
    for (tile_x, tile_y), data in buildings.items():
        b_type = data["type"]
        level = data["level"]
        img = building_images[b_type][level]
        screen.blit(
            img,
            (offset_x + tile_x * tmx_data.tilewidth * SCALE + dx,
             offset_y + tile_y * tmx_data.tileheight * SCALE + dy)
        )

# -------------------------
# Draw UI
# -------------------------
def draw_ui_offset(dx=0, dy=0):
    # Money
    money_system.draw(screen, font)
    
    # Health bar
    bar_x, bar_y = 20 + dx, 60 + dy
    bar_width, bar_height = 200, 20
    pygame.draw.rect(screen, (255,0,0), (bar_x, bar_y, bar_width, bar_height))
    current_width = int(bar_width * (player_health / 100))
    pygame.draw.rect(screen, (0,255,0), (bar_x, bar_y, current_width, bar_height))
    pygame.draw.rect(screen, (0,0,0), (bar_x, bar_y, bar_width, bar_height), 2)

    # Messages
    global message
    if message:
        elapsed = pygame.time.get_ticks() - message_timer
        if elapsed < 2000:
            alpha = 255 - int(elapsed / 2000 * 255)
            text_surface = font.render(message, True, (255,255,255))
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, (20 + dx, SCREEN_HEIGHT-40 + dy))
        else:
            message = ""

    # Game Over
    if game_over:
        go_text = font.render("GAME OVER!", True, (255, 0, 0))
        go_rect = go_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(go_text, go_rect)

# -------------------------
# Main loop
# -------------------------
running = True
shake_offset = (0,0)

while running:
    current_time = pygame.time.get_ticks()

    # Update money system
    if not game_over:
        money_system.update()

    # Update bombing system
    if not game_over:
        player_health, shake_offset = bombing.update(player_health)
        if player_health <= 0:
            player_health = 0
            game_over = True
            message = "GAME OVER!"
            message_timer = pygame.time.get_ticks()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not game_over:
                mouse_pos = pygame.mouse.get_pos()
                tile_x = int((mouse_pos[0] - offset_x) / (tmx_data.tilewidth * SCALE))
                tile_y = int((mouse_pos[1] - offset_y) / (tmx_data.tileheight * SCALE))
                key = (tile_x, tile_y)

                # Choose building type for now (could be selectable later)
                building_type = random.choice(types)

                if key not in buildings:
                    buildings[key] = {"type": building_type, "level": 0}
                    message = f"New {building_type} added!"
                    money_system.change_money(-5, mouse_pos)
                elif buildings[key]["level"] < 2:
                    buildings[key]["level"] += 1
                    message = f"{building_type.capitalize()} upgraded!"
                    money_system.change_money(-15, mouse_pos)
                else:
                    message = f"{building_type.capitalize()} fully upgraded!"

                message_timer = pygame.time.get_ticks()

    # Draw everything with shake
    screen.fill((0,0,0))
    shake_x, shake_y = shake_offset
    draw_map_offset(shake_x, shake_y)
    draw_buildings_offset(shake_x, shake_y)
    draw_ui_offset(shake_x, shake_y)
    pygame.display.update()

pygame.quit()
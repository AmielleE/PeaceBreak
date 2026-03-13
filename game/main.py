# import pygame, sys
# from pytmx.util_pygame import load_pygame

# pygame.init()
# screen = pygame.display.set_mode((1280, 720))
# tmx_data = load_pygame('../assets/world.tmx')

# while True:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             sys.exit()

#     screen.fill(('black'))
#     pygame.display.update()

import pygame
import pytmx
import os

# -------------------------
# Constants
# -------------------------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCALE = 0.7  # scale tiles down by 50%

# -------------------------
# Initialize Pygame
# -------------------------
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("PeaceBreak Prototype")

# -------------------------
# Load Tiled Map
# -------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))  # folder with main.py
map_path = os.path.join(current_dir, "..", "assets", "world.tmx")
map_path = os.path.abspath(map_path)
print("Loading map from:", map_path)

tmx_data = pytmx.util_pygame.load_pygame(map_path)

# -------------------------
# Font for messages
# -------------------------
font = pygame.font.SysFont(None, 36)
message = ""

# -------------------------
# Game Loop
# -------------------------
running = True
while running:
    screen.fill((0, 0, 0))  # clear screen

    # Draw Tiled map
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

    # Display message if any
    if message:
        text_surface = font.render(message, True, (255, 255, 255))
        screen.blit(text_surface, (10, SCREEN_HEIGHT - 50))

    pygame.display.flip()

    # -------------------------
    # Event Handling
    # -------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            print(f"Clicked at {mouse_pos}")  # console output
            message = "Added new building!"   # display on screen

pygame.quit()
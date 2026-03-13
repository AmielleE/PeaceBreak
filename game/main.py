import pygame
import pytmx
import os
from money import MoneySystem

# -------------------------
# Constants
# -------------------------
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650

# -------------------------
# Initialize pygame
# -------------------------
pygame.init()
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
# Calculate map scaling
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
# Message system
# -------------------------
message = ""
message_timer = 0

# -------------------------
# Building states
# -------------------------
buildings = {}  # key=(tile_x,tile_y) value=state 0=empty,1=added,2=upgraded

# -------------------------
# Player health
# -------------------------
player_health = 100  # out of 100

# -------------------------
# Draw tile layers
# -------------------------
def draw_map():
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    tile = pygame.transform.scale(
                        tile,
                        (
                            int(tmx_data.tilewidth * SCALE),
                            int(tmx_data.tileheight * SCALE)
                        )
                    )
                    screen.blit(tile, (offset_x + x*tmx_data.tilewidth*SCALE,
                                       offset_y + y*tmx_data.tileheight*SCALE))

# -------------------------
# Draw UI elements
# -------------------------
def draw_ui():
    # Money system
    money_system.draw(screen, font)

    # Health bar
    bar_x, bar_y = 20, 60
    bar_width, bar_height = 200, 20
    pygame.draw.rect(screen, (255,0,0), (bar_x, bar_y, bar_width, bar_height))  # red background
    current_width = int(bar_width * (player_health / 100))
    pygame.draw.rect(screen, (0,255,0), (bar_x, bar_y, current_width, bar_height))  # green current health
    pygame.draw.rect(screen, (0,0,0), (bar_x, bar_y, bar_width, bar_height), 2)  # border

    # Messages
    global message
    if message:
        elapsed = pygame.time.get_ticks() - message_timer
        if elapsed < 2000:  # fade after 2s
            alpha = 255 - int(elapsed / 2000 * 255)
            text_surface = font.render(message, True, (255,255,255))
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, (20, SCREEN_HEIGHT-40))
        else:
            message = ""

# -------------------------
# Main loop
# -------------------------
running = True
while running:
    current_time = pygame.time.get_ticks()

    # Update money
    money_system.update()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            tile_x = int((mouse_pos[0] - offset_x) / (tmx_data.tilewidth * SCALE))
            tile_y = int((mouse_pos[1] - offset_y) / (tmx_data.tileheight * SCALE))
            key = (tile_x, tile_y)
            state = buildings.get(key, 0)

            if state == 0:
                cost = -5
                message = "New building added!"
                buildings[key] = 1
            elif state == 1:
                cost = -15
                message = "Building upgraded!"
                buildings[key] = 2
            else:
                cost = 0
                message = "Building fully upgraded!"

            if cost != 0:
                money_system.change_money(cost, mouse_pos)

            message_timer = pygame.time.get_ticks()

    # Draw
    screen.fill((0,0,0))
    draw_map()
    draw_ui()
    pygame.display.update()

pygame.quit()
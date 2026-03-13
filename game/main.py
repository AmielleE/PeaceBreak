import pygame
import pytmx
import os

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

print("Loading map from:", map_path)

tmx_data = pytmx.util_pygame.load_pygame(map_path)

# -------------------------
# Calculate map scaling
# -------------------------
map_pixel_width = tmx_data.width * tmx_data.tilewidth
map_pixel_height = tmx_data.height * tmx_data.tileheight

scale_x = SCREEN_WIDTH / map_pixel_width
scale_y = SCREEN_HEIGHT / map_pixel_height

SCALE = min(scale_x, scale_y)

# Center the map
offset_x = (SCREEN_WIDTH - map_pixel_width * SCALE) / 2
offset_y = (SCREEN_HEIGHT - map_pixel_height * SCALE) / 2

print("Map scale:", SCALE)

# -------------------------
# Font for messages
# -------------------------
font = pygame.font.SysFont(None, 36)
message = ""

# -------------------------
# Draw tile layers (Ground + Nature)
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

                    screen.blit(
                        tile,
                        (
                            offset_x + x * tmx_data.tilewidth * SCALE,
                            offset_y + y * tmx_data.tileheight * SCALE
                        )
                    )

# -------------------------
# Game loop
# -------------------------
running = True

while running:

    screen.fill((0, 0, 0))

    # Draw map (all tile layers)
    draw_map()

    # Show message if player clicked
    if message:
        text_surface = font.render(message, True, (255, 255, 255))
        screen.blit(text_surface, (20, SCREEN_HEIGHT - 40))

    pygame.display.update()

    # -------------------------
    # Events
    # -------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = pygame.mouse.get_pos()
            print("Clicked at:", mouse_pos)

            message = "Added new building!"

pygame.quit()
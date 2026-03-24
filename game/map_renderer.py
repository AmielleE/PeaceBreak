import pygame
import pytmx
from settings import SCALE

# Scale helper
def scale_surface(surface, scale):
    w = max(1, int(surface.get_width() * scale))
    h = max(1, int(surface.get_height() * scale))
    return pygame.transform.scale(surface, (w, h))

# Draw map layers
def draw_map_offset(screen, tmx_data, scaled_tile_width, scaled_tile_height, dx=0, dy=0):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if gid == 0:
                    continue

                tile = tmx_data.get_tile_image_by_gid(gid)
                if not tile:
                    continue

                # Scale using global SCALE
                scaled_tile = scale_surface(tile, SCALE)

                draw_x = x * scaled_tile_width + dx
                draw_y = y * scaled_tile_height + dy

                screen.blit(scaled_tile, (draw_x, draw_y))

# Draw buildings
def draw_buildings_offset(screen, buildings, building_images, scaled_tile_width, scaled_tile_height, dx=0, dy=0):
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
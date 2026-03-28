import pygame
import pytmx
from settings import SCALE

# Helper function to load and scale tile images
def scale_surface(surface, scale):
    w = max(1, int(surface.get_width() * scale))
    h = max(1, int(surface.get_height() * scale))
    return pygame.transform.scale(surface, (w, h))

# Draw the map with screen shake and bomb animation
def draw_map_offset(screen, tmx_data, scaled_tile_width, scaled_tile_height, dx=0, dy=0):
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if gid == 0:
                    continue

                tile = tmx_data.get_tile_image_by_gid(gid)
                if not tile:
                    continue

                scaled_tile = scale_surface(tile, SCALE)
                img_h = scaled_tile.get_height()

                draw_x = x * scaled_tile_width + dx
                draw_y = (y + 1) * scaled_tile_height - img_h + dy

                screen.blit(scaled_tile, (draw_x, draw_y))

# helper function for building placement
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

# for identifying tile GIDs and buildable areas
def get_tile_gid(tmx_data, tile_x, tile_y):
    gid = 0
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            tile_gid = layer.data[tile_y][tile_x]
            if tile_gid != 0:
                gid = tile_gid  # keep overwriting so we get the top layer
    return gid

# prints all unique GIDs on the map so we can identify which ones are the grey tiles (to place buidlings)
def get_buildable_gids(tmx_data):
    gids = set()
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if gid != 0:
                    gids.add(gid)
    return gids

def draw_craters(screen, crater_patches, crater_img, scaled_tile_width, scaled_tile_height, dx=0, dy=0):
    if not crater_img or not crater_patches:
        return

    for (min_x, min_y, max_x, max_y) in crater_patches:
        padding = 2  # extra tiles of padding on each side
        patch_w = (max_x - min_x + 1 + padding * 2) * scaled_tile_width
        patch_h = (max_y - min_y + 1 + padding * 2) * scaled_tile_height
        crater_scaled = pygame.transform.scale(crater_img, (int(patch_w), int(patch_h)))
        draw_x = (min_x - padding) * scaled_tile_width + dx
        draw_y = (min_y - padding) * scaled_tile_height + dy
        screen.blit(crater_scaled, (draw_x, draw_y))
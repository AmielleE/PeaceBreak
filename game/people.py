import random
import math
import os
import pygame

SPRITE_FOLDER = os.path.join("..", "assets", "images", "citizens")
PEOPLE_SPRITES = []

def load_people_sprites():
    global PEOPLE_SPRITES
    PEOPLE_SPRITES = []

    current_dir = os.path.dirname(os.path.abspath(__file__))
    sprite_folder_path = os.path.abspath(os.path.join(current_dir, SPRITE_FOLDER))

    if not os.path.exists(sprite_folder_path):
        print(f"[people.py] Sprite folder not found: {sprite_folder_path}")
        return

    for filename in os.listdir(sprite_folder_path):
        if filename.lower().endswith(".png"):
            full_path = os.path.join(sprite_folder_path, filename)
            try:
                sprite = pygame.image.load(full_path).convert_alpha()
                PEOPLE_SPRITES.append(sprite)
                print(f"[people.py] Loaded sprite: {filename}")
            except pygame.error as e:
                print(f"[people.py] Failed to load {filename}: {e}")

    if not PEOPLE_SPRITES:
        print("[people.py] No citizen sprites found, rectangles will be used.")


def _get_unique_buildings(buildings):
    unique = []
    seen = set()

    for building in buildings.values():
        building_id = id(building)
        if building_id not in seen:
            seen.add(building_id)
            unique.append(building)

    return unique

def _building_point(building, scaled_tile_width, scaled_tile_height):
    top_left_tile = building["tiles"][0]
    tile_x, tile_y = top_left_tile

    x = int((tile_x + building["width"] / 2) * scaled_tile_width)
    y = int((tile_y + building["height"]) * scaled_tile_height - 4)

    return x, y

def _role_weight(building_type, role):
    if role == "origin":
        if building_type == "house":
            return 5
        if building_type == "apt":
            return 6
        if building_type == "school":
            return 2
        if building_type == "hospital":
            return 1
        if building_type == "power":
            return 1
        if building_type == "air":
            return 2

    if role == "destination":
        if building_type == "house":
            return 2
        if building_type == "apt":
            return 2
        if building_type == "school":
            return 5
        if building_type == "hospital":
            return 6
        if building_type == "power":
            return 3
        if building_type == "air":
            return 4

    return 1

def _weighted_pick(building_list, role):
    weights = [_role_weight(b["type"], role) for b in building_list]
    return random.choices(building_list, weights=weights, k=1)[0]

def _max_people_for_count(building_count):
    if building_count < 3:
        return 0
    if building_count < 6:
        return 3
    if building_count < 10:
        return 5
    return 8

def spawn_person(people, buildings, scaled_tile_width, scaled_tile_height):
    unique_buildings = _get_unique_buildings(buildings)

    if len(unique_buildings) < 3:
        return

    origin = _weighted_pick(unique_buildings, "origin")
    destination = _weighted_pick(unique_buildings, "destination")

    tries = 0
    while destination is origin and tries < 10:
        destination = _weighted_pick(unique_buildings, "destination")
        tries += 1

    if destination is origin:
        return

    start_x, start_y = _building_point(origin, scaled_tile_width, scaled_tile_height)
    target_x, target_y = _building_point(destination, scaled_tile_width, scaled_tile_height)

    dx = target_x - start_x
    dy = target_y - start_y
    distance = math.hypot(dx, dy)

    if distance < 8:
        return

    speed = random.uniform(0.6, 1.2)

    sprite = random.choice(PEOPLE_SPRITES) if PEOPLE_SPRITES else None

    # tweak these if the sprite looks too big/small in game
    sprite_scale = 0.13

    if sprite:
        sprite_width = max(1, int(sprite.get_width() * sprite_scale))
        sprite_height = max(1, int(sprite.get_height() * sprite_scale))
    else:
        sprite_width = 4
        sprite_height = 7

    person = {
        "x": float(start_x),
        "y": float(start_y),
        "target_x": float(target_x),
        "target_y": float(target_y),
        "speed": speed,
        "width": sprite_width,
        "height": sprite_height,
        "color": random.choice([
            (30, 30, 30),
            (60, 70, 130),
            (120, 40, 40),
            (90, 110, 60),
            (140, 120, 80)
        ]),
        "sprite": sprite,
        "sprite_scale": sprite_scale
    }

    people.append(person)

def update_people(people, buildings, scaled_tile_width, scaled_tile_height, last_spawn_time, current_time):
    unique_buildings = _get_unique_buildings(buildings)
    building_count = len(unique_buildings)
    max_people = _max_people_for_count(building_count)

    if building_count < 3:
        spawn_interval = 999999
    elif building_count < 6:
        spawn_interval = 2200
    elif building_count < 10:
        spawn_interval = 1600
    else:
        spawn_interval = 1200

    if len(people) < max_people and current_time - last_spawn_time >= spawn_interval:
        spawn_person(people, buildings, scaled_tile_width, scaled_tile_height)
        last_spawn_time = current_time

    remaining = []

    for person in people:
        dx = person["target_x"] - person["x"]
        dy = person["target_y"] - person["y"]
        distance = math.hypot(dx, dy)

        if distance <= person["speed"] or distance < 2:
            continue

        if distance != 0:
            person["x"] += (dx / distance) * person["speed"]
            person["y"] += (dy / distance) * person["speed"]

        remaining.append(person)

    people[:] = remaining
    return last_spawn_time

def draw_people(screen, people):
    for person in people:
        x = int(person["x"])
        y = int(person["y"])

        if person["sprite"]:
            scaled_sprite = pygame.transform.scale(
                person["sprite"],
                (
                    max(1, int(person["sprite"].get_width() * person["sprite_scale"])),
                    max(1, int(person["sprite"].get_height() * person["sprite_scale"]))
                )
            )

            draw_x = x - scaled_sprite.get_width() // 2
            draw_y = y - scaled_sprite.get_height() + 2
            screen.blit(scaled_sprite, (draw_x, draw_y))
        else:
            shadow_rect = pygame.Rect(
                x - 1,
                y + person["height"] - 1,
                person["width"] + 2,
                2
            )
            pygame.draw.rect(screen, (20, 20, 20), shadow_rect)

            body_rect = pygame.Rect(x, y, person["width"], person["height"])
            pygame.draw.rect(screen, person["color"], body_rect, border_radius=1)
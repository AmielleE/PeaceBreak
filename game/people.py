import random
import math
import pygame


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
    """
    Returns a point near the bottom-center of a building footprint.
    This makes walkers look like they are moving between buildings
    instead of snapping to top-left corners.
    """
    top_left_tile = building["tiles"][0]
    tile_x, tile_y = top_left_tile

    x = int((tile_x + building["width"] / 2) * scaled_tile_width)
    y = int((tile_y + building["height"]) * scaled_tile_height - 4)

    return x, y


def _role_weight(building_type, role):
    """
    Biases where people come from and where they go.
    Houses/apartments are more likely origins.
    Hospitals/schools are more likely destinations.
    """
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

    # Tiny rectangle people for now
    person = {
        "x": float(start_x),
        "y": float(start_y),
        "target_x": float(target_x),
        "target_y": float(target_y),
        "speed": speed,
        "width": 4,
        "height": 7,
        "color": random.choice([
            (30, 30, 30),
            (60, 70, 130),
            (120, 40, 40),
            (90, 110, 60),
            (140, 120, 80)
        ])
    }

    people.append(person)


def update_people(people, buildings, scaled_tile_width, scaled_tile_height, last_spawn_time, current_time):
    """
    Returns updated last_spawn_time.
    """
    unique_buildings = _get_unique_buildings(buildings)
    building_count = len(unique_buildings)
    max_people = _max_people_for_count(building_count)

    # Spawn interval gets slightly faster as city grows
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

        # tiny shadow
        shadow_rect = pygame.Rect(x - 1, y + person["height"] - 1, person["width"] + 2, 2)
        pygame.draw.rect(screen, (20, 20, 20), shadow_rect)

        body_rect = pygame.Rect(x, y, person["width"], person["height"])
        pygame.draw.rect(screen, person["color"], body_rect, border_radius=1)
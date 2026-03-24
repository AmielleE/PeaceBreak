BUILDING_DATA = {
    "house": {
        "label": "House",
        "cost": 10,
        "income": 1,
        "health": 0
    },
    "apt": {
        "label": "Apartment",
        "cost": 18,
        "income": 2,
        "health": 0
    },
    "hospital": {
        "label": "Hospital",
        "cost": 30,
        "income": 0,
        "health": 4
    },
    "school": {
        "label": "School",
        "cost": 24,
        "income": 0,
        "health": 2
    },
    "power": {
        "label": "Power Plant",
        "cost": 28,
        "income": 5,
        "health": 0
    },
    "air": {
        "label": "Airport",
        "cost": 40,
        "income": 8,
        "health": 0
    }
}

MENU_ORDER = ["house", "apt", "hospital", "school", "power", "air"]
TYPES = ["house", "apt", "hospital", "air", "power", "school"]

# building placement
def can_place_building(buildings, tile_x, tile_y, width, height, map_w, map_h):
    for dx in range(width):
        for dy in range(height):
            check_tile = (tile_x + dx, tile_y + dy)

            if check_tile[0] < 0 or check_tile[1] < 0:
                return False
            if check_tile[0] >= map_w or check_tile[1] >= map_h:
                return False
            if check_tile in buildings:
                return False

    return True

def place_building(buildings, tile_x, tile_y, b_type, width=2, height=2):
    tiles = [(tile_x + dx, tile_y + dy) for dx in range(width) for dy in range(height)]

    building_data = {
        "type": b_type,
        "level": 0,
        "width": width,
        "height": height,
        "tiles": tiles
    }

    for t in tiles:
        buildings[t] = building_data

# building helper functions
def get_unique_buildings(buildings):
    unique = []
    seen = set()

    for b in buildings.values():
        if id(b) not in seen:
            seen.add(id(b))
            unique.append(b)

    return unique

def count_buildings(buildings):
    return len(set(id(b) for b in buildings.values()))

def count_upgraded(buildings):
    seen = set()
    upgraded = 0

    for b in buildings.values():
        bid = id(b)
        if bid not in seen:
            seen.add(bid)
            if b["level"] > 0:
                upgraded += 1

    return upgraded

# bonus system
def apply_building_bonuses(buildings, money_system, player_health, last_bonus_tick, current_time, bonus_interval):
    if current_time - last_bonus_tick < bonus_interval:
        return player_health, last_bonus_tick

    last_bonus_tick = current_time

    total_income = 0
    total_health = 0

    for b in get_unique_buildings(buildings):
        b_type = b["type"]
        level_multiplier = b["level"] + 1
        data = BUILDING_DATA[b_type]

        total_income += data["income"] * level_multiplier
        total_health += data["health"] * level_multiplier

    if total_income > 0:
        money_system.change_money(total_income, (20, 20))

    if total_health > 0:
        player_health = min(100, player_health + total_health)

    return player_health, last_bonus_tick

# upgrade logic
def try_upgrade_building(building, money_system, mouse_pos):
    if building["level"] < 2:
        building["level"] += 1
        money_system.change_money(-15, mouse_pos)
        return f"{building['type'].capitalize()} upgraded!"
    else:
        return f"{building['type'].capitalize()} fully upgraded!"
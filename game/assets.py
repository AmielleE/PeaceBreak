import pygame
import os

def get_asset_path(current_dir, *paths):
    return os.path.abspath(os.path.join(current_dir, "..", *paths))

def load_images(current_dir, SCREEN_WIDTH, SCREEN_HEIGHT):
    images = {}

    # Title screen
    title_bg_path = get_asset_path(current_dir, "assets", "images", "title_screen.png")
    if os.path.exists(title_bg_path):
        title_bg = pygame.image.load(title_bg_path).convert()
        title_bg = pygame.transform.scale(title_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        images["title_bg"] = title_bg
    else:
        images["title_bg"] = None

    # Build menu panel 
    panel_path = get_asset_path(current_dir, "assets", "images", "build_menu_panel.png")
    images["menu_panel"] = pygame.image.load(panel_path).convert_alpha() if os.path.exists(panel_path) else None

    # Bomb image
    bomb_path = get_asset_path(current_dir, "assets", "images", "bomb.png")
    images["bomb"] = pygame.image.load(bomb_path).convert_alpha() if os.path.exists(bomb_path) else None

    # Crater image
    crater_path = get_asset_path(current_dir, "assets", "images", "crater.png")
    images["crater"] = pygame.image.load(crater_path).convert_alpha() if os.path.exists(crater_path) else None

    return images

def load_sounds(current_dir):
    sounds = {}
    bomb_sound_path = get_asset_path(current_dir, "assets", "sounds", "BOOM.wav")
    sounds["bomb_path"] = bomb_sound_path

    clang_path = get_asset_path(current_dir, "assets", "sounds", "CLANG.wav")
    sounds["clang"] = pygame.mixer.Sound(clang_path) if os.path.exists(clang_path) else None

    return sounds

def load_buildings(current_dir):
    building_images = {}
    menu_icons = {}

    types = ["house", "apt", "hospital", "air", "power", "school"]
    materials = ["brick", "concrete", "gold"]

    for b_type in types:
        building_images[b_type] = []
        for mat in materials:
            path = get_asset_path(current_dir, "assets", "buildings", f"{b_type}_{mat}.png")
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing building asset: {path}")
            img = pygame.image.load(path).convert_alpha()
            building_images[b_type].append(img)
        menu_icons[b_type] = building_images[b_type][0]

    return building_images, menu_icons, types
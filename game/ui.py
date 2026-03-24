import pygame
from buildings import MENU_ORDER

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 40, 40)
BRIGHT_RED = (255, 70, 70)
DARK_BLUE = (20, 30, 60)
GOLD = (255, 215, 0)
LIGHT_WOOD = (156, 104, 64)
DARK_WOOD = (92, 55, 30)
PANEL_BROWN = (70, 40, 20)
HIGHLIGHT = (255, 230, 120)

# title screen
def draw_title_screen(screen, title_bg, SCREEN_WIDTH, SCREEN_HEIGHT, play_button, title_font, subtitle_font, button_font):
    mouse_pos = pygame.mouse.get_pos()
    hovered = play_button.collidepoint(mouse_pos)

    if title_bg:
        screen.blit(title_bg, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 35))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill(DARK_BLUE)

        title_text = title_font.render("PeaceBreak", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        screen.blit(title_text, title_rect)

        subtitle_text = subtitle_font.render("Rebuild. Survive. Resist.", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 55))
        screen.blit(subtitle_text, subtitle_rect)

    button_color = BRIGHT_RED if hovered else RED
    pygame.draw.rect(screen, button_color, play_button, border_radius=12)
    pygame.draw.rect(screen, WHITE, play_button, width=3, border_radius=12)

    play_text = button_font.render("PLAY", True, WHITE)
    play_rect = play_text.get_rect(center=play_button.center)
    screen.blit(play_text, play_rect)

# name input
def draw_name_input(screen, draw_map_func, SCREEN_WIDTH, SCREEN_HEIGHT, font, player_name):
    draw_map_func()

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    text = font.render("Enter Name:", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

    name_surface = font.render(player_name, True, WHITE)
    screen.blit(name_surface, (SCREEN_WIDTH // 2 - name_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

# leaderboard
def draw_leaderboard(screen, draw_map_func, SCREEN_WIDTH, SCREEN_HEIGHT, leaderboard, title_font, font, small_font, game_over_reason):
    draw_map_func()

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    title = title_font.render("Leaderboard", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width() // 2, 50))

    if game_over_reason:
        reason_text = font.render(game_over_reason, True, RED)
        screen.blit(reason_text, (SCREEN_WIDTH//2 - reason_text.get_width() // 2, 120))

    start_y = 150 if not game_over_reason else 160

    for i, entry in enumerate(leaderboard[:10]):
        line = font.render(f"{i+1}. {entry['name']} - {entry['score']}", True, WHITE)
        screen.blit(line, (SCREEN_WIDTH//2 - line.get_width() // 2, start_y + i * 40))

    hint = small_font.render("Press R to return", True, WHITE)
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 50))

# game UI
def draw_ui_offset(screen, money_system, font, small_font, player_health, selected_building, BUILDING_DATA, message, message_timer, SCREEN_HEIGHT): 
    money_system.draw(screen, font)

    # Health bar
    bar_x, bar_y = 20, 60
    bar_width, bar_height = 200, 20

    pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
    current_width = int(bar_width * (player_health / 100))
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, current_width, bar_height))
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)

    selected_label = BUILDING_DATA[selected_building]["label"] if selected_building else "None"

    help_text = small_font.render(f"B: Build Menu   Selected: {selected_label}", True, WHITE)
    screen.blit(help_text, (20, 90))

    # Message fade
    if message:
        elapsed = pygame.time.get_ticks() - message_timer
        if elapsed < 2200:
            alpha = 255 - int(elapsed / 2200 * 255)
            text_surface = font.render(message, True, WHITE)
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, (20, SCREEN_HEIGHT - 40))

# build menu
def draw_build_menu(screen, menu_x, SCREEN_WIDTH, MENU_WIDTH, menu_panel, menu_icons, BUILDING_DATA, selected_building, tiny_font, menu_title_font, SCREEN_HEIGHT):
    if menu_x >= SCREEN_WIDTH:
        return [], None

    slot_rects = []

    # Shift panel image slightly left/up
    panel_offset_x = -12
    panel_offset_y = -15
    panel_rect = pygame.Rect(menu_x + panel_offset_x, panel_offset_y, MENU_WIDTH, SCREEN_HEIGHT)

    if menu_panel:
        # scale panel image to fit menu width & height
        panel_scaled = pygame.transform.scale(menu_panel, (MENU_WIDTH, SCREEN_HEIGHT))
        screen.blit(panel_scaled, (menu_x + panel_offset_x, panel_offset_y))
    else:
        pygame.draw.rect(screen, LIGHT_WOOD, panel_rect)
        pygame.draw.rect(screen, DARK_WOOD, panel_rect, 6)

    # Title
    title_text = menu_title_font.render("Build Menu", True, WHITE)
    screen.blit(title_text, (menu_x + 26, 18))

    # Slots (start a little lower for proper panel frame)
    slot_w, slot_h = 188, 68
    slot_gap = 10
    start_y = 100  # moved down slightly

    mouse_pos = pygame.mouse.get_pos()
    hovered_type = None

    for i, b_type in enumerate(MENU_ORDER):
        slot_x = menu_x + 20
        slot_y = start_y + i * (slot_h + slot_gap)

        rect = pygame.Rect(slot_x, slot_y, slot_w, slot_h)
        slot_rects.append((rect, b_type))

        is_selected = selected_building == b_type
        is_hovered = rect.collidepoint(mouse_pos)

        if is_hovered:
            hovered_type = b_type

        pygame.draw.rect(screen, PANEL_BROWN, rect, border_radius=8)
        border_color = HIGHLIGHT if is_selected else WHITE
        border_width = 4 if is_selected else 2
        pygame.draw.rect(screen, border_color, rect, border_width, border_radius=8)

        # Draw icon
        icon = menu_icons[b_type]
        icon_scaled = pygame.transform.scale(icon, (48, 48))
        screen.blit(icon_scaled, (rect.x + 8, rect.y + 10))

        # Draw label & cost
        label = BUILDING_DATA[b_type]["label"]
        cost = BUILDING_DATA[b_type]["cost"]
        text1 = tiny_font.render(label, True, WHITE)
        text2 = tiny_font.render(f"${cost}", True, GOLD)
        screen.blit(text1, (rect.x + 64, rect.y + 12))
        screen.blit(text2, (rect.x + 64, rect.y + 36))

    # Draw info box for hovered/selected type
    info_type = hovered_type if hovered_type else selected_building
    if info_type:
        draw_menu_info_box(screen, info_type, BUILDING_DATA, menu_x, SCREEN_HEIGHT)

    return slot_rects, hovered_type

# menu info box
def draw_menu_info_box(screen, b_type, BUILDING_DATA, menu_x, SCREEN_HEIGHT):
    
    data = BUILDING_DATA[b_type]

    box_w, box_h = 190, 112
    box_x = max(10, menu_x - box_w - 10)
    box_y = SCREEN_HEIGHT - box_h - 18

    info_rect = pygame.Rect(box_x, box_y, box_w, box_h)

    pygame.draw.rect(screen, (35, 25, 18), info_rect, border_radius=10)
    pygame.draw.rect(screen, HIGHLIGHT, info_rect, 2, border_radius=10)

    lines = [
        data["label"],
        f"Cost: ${data['cost']}",
        f"Income: +{data['income']} / bonus tick",
        f"Health: +{data['health']} / bonus tick"
    ]

    font = pygame.font.SysFont(None, 20)

    for i, line in enumerate(lines):
        txt = font.render(line, True, WHITE)
        screen.blit(txt, (box_x + 12, box_y + 12 + i * 22))

# menu animation from the side
def update_menu_animation(menu_open, menu_x, MENU_X_OPEN, MENU_X_CLOSED, menu_speed):
    
    if menu_open:
        if menu_x > MENU_X_OPEN:
            menu_x -= menu_speed
            if menu_x < MENU_X_OPEN:
                menu_x = MENU_X_OPEN
    else:
        if menu_x < MENU_X_CLOSED:
            menu_x += menu_speed
            if menu_x > MENU_X_CLOSED:
                menu_x = MENU_X_CLOSED

    return menu_x

# bomb animation
def draw_bomb_animation(screen, bomb_img, bomb_anim_active,
                         bomb_anim_start, BOMB_ANIM_DURATION,
                         SCREEN_WIDTH, SCREEN_HEIGHT):
    
    if not bomb_anim_active or not bomb_img:
        return False

    elapsed = pygame.time.get_ticks() - bomb_anim_start
    progress = elapsed / BOMB_ANIM_DURATION

    if progress >= 1:
        return False

    start_y = -200
    end_y = SCREEN_HEIGHT // 2

    y = start_y + (end_y - start_y) * progress
    scale = 0.3 + (2.5 * progress)

    img = pygame.transform.rotozoom(bomb_img, 0, scale)
    rect = img.get_rect(center=(SCREEN_WIDTH // 2, int(y)))

    screen.blit(img, rect)

    return True
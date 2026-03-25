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

    # Dark overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    screen.blit(overlay, (0, 0))

    # Center panel
    panel_w, panel_h = 460, 280
    panel_x = SCREEN_WIDTH  // 2 - panel_w // 2
    panel_y = SCREEN_HEIGHT // 2 - panel_h // 2

    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (12, 14, 35, 240), (0, 0, panel_w, panel_h), border_radius=16)
    pygame.draw.rect(panel_surf, (60, 160, 80, 220), (0, 0, panel_w, panel_h), 3, border_radius=16)
    screen.blit(panel_surf, (panel_x, panel_y))

    # Title
    title_font = pygame.font.SysFont(None, 52)
    title_surf = title_font.render("ENTER YOUR NAME", True, (255, 215, 0))
    screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, panel_y + 28))

    # Divider
    pygame.draw.line(screen, (60, 160, 80), (panel_x + 30, panel_y + 80), (panel_x + panel_w - 30, panel_y + 80), 2)
 
    # Subtitle
    sub_font = pygame.font.SysFont(None, 26)
    sub_surf = sub_font.render("Your name will appear on the leaderboard.", True, (160, 160, 160))
    screen.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, panel_y + 94))

    # Name input box
    input_w, input_h = 360, 52
    input_x = SCREEN_WIDTH // 2 - input_w // 2
    input_y = panel_y + 138

    input_surf = pygame.Surface((input_w, input_h), pygame.SRCALPHA)
    pygame.draw.rect(input_surf, (25, 30, 55, 230), (0, 0, input_w, input_h), border_radius=10)
    pygame.draw.rect(input_surf, (100, 220, 120, 200), (0, 0, input_w, input_h), 2, border_radius=10)
    screen.blit(input_surf, (input_x, input_y))

    # Typed name with blinking cursor
    name_font = pygame.font.SysFont(None, 38)
    cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
    name_surf = name_font.render(player_name + cursor, True, (255, 255, 255))
    screen.blit(name_surf, (SCREEN_WIDTH // 2 - name_surf.get_width() // 2, input_y + 12))

    # Hint
    hint_font = pygame.font.SysFont(None, 24)
    hint_surf = hint_font.render("Press  ENTER  to start", True, (100, 160, 100))
    screen.blit(hint_surf, (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, panel_y + 222))

# leaderboard
def draw_leaderboard(screen, draw_map_func, SCREEN_WIDTH, SCREEN_HEIGHT, leaderboard, title_font, font, small_font, game_over_reason):
    draw_map_func()

    # Dark overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    screen.blit(overlay, (0, 0))

    # Center panel
    panel_w, panel_h = 520, 580
    panel_x = SCREEN_WIDTH // 2 - panel_w // 2
    panel_y = SCREEN_HEIGHT // 2 - panel_h // 2

    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (12, 14, 35, 240), (0, 0, panel_w, panel_h), border_radius=16)
    pygame.draw.rect(panel_surf, (60, 160, 80, 220), (0, 0, panel_w, panel_h), 3, border_radius=16)
    screen.blit(panel_surf, (panel_x, panel_y))

    # Title
    title_font2 = pygame.font.SysFont(None, 62)
    title_surf = title_font2.render("LEADERBOARD", True, (255, 215, 0))
    screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, panel_y + 22))

    # Divider
    pygame.draw.line(screen, (80, 100, 200), (panel_x + 30, panel_y + 80), (panel_x + panel_w - 30, panel_y + 80), 2)

    # Game over reason
    start_y = panel_y + 95
    if game_over_reason:
        reason_font = pygame.font.SysFont(None, 28)
        reason_surf = reason_font.render(game_over_reason, True, (220, 80, 80))
        screen.blit(reason_surf, (SCREEN_WIDTH // 2 - reason_surf.get_width() // 2, start_y))
        start_y += 34

    # Column headers
    header_font = pygame.font.SysFont(None, 24)
    rank_h = header_font.render("RANK", True, (120, 180, 120))
    name_h = header_font.render("PLAYER", True, (120, 180, 120))
    score_h = header_font.render("SCORE", True, (120, 180, 120))
    screen.blit(rank_h, (panel_x + 30,  start_y))
    screen.blit(name_h, (panel_x + 110, start_y))
    screen.blit(score_h, (panel_x + 390, start_y))
    start_y += 26

    pygame.draw.line(screen, (60, 160, 80), (panel_x + 30, start_y), (panel_x + panel_w - 30, start_y), 1)
    start_y += 8

    # Entries
    entry_font = pygame.font.SysFont(None, 28)
    medal_colors = [(255, 215, 0), (192, 192, 192), (180, 100, 40)]

    for i, entry in enumerate(leaderboard[:10]):
        row_y = start_y + i * 36

        # Highlight top 3
        if i < 3:
            row_surf = pygame.Surface((panel_w - 40, 30), pygame.SRCALPHA)
            pygame.draw.rect(row_surf, (255, 215, 0, 18 - i * 5), (0, 0, panel_w - 40, 30), border_radius=6)
            screen.blit(row_surf, (panel_x + 20, row_y - 2))

        rank_color = medal_colors[i] if i < 3 else (180, 180, 180)
        rank_surf  = entry_font.render(f"#{i+1}", True, rank_color)
        name_surf  = entry_font.render(entry.get("name", "Unknown"), True, (220, 220, 220))
        score_surf = entry_font.render(str(entry.get("score", 0)), True, (100, 220, 140))

        screen.blit(rank_surf,  (panel_x + 30,  row_y))
        screen.blit(name_surf,  (panel_x + 110, row_y))
        screen.blit(score_surf, (panel_x + 390, row_y))

    # Return hint
    hint_font = pygame.font.SysFont(None, 26)
    hint_surf = hint_font.render("Press  R  to return to menu", True, (100, 160, 100))
    screen.blit(hint_surf, (SCREEN_WIDTH // 2 - hint_surf.get_width() // 2, panel_y + panel_h - 36))
    
# game UI
def draw_ui_offset(screen, money_system, font, small_font, player_health, selected_building, BUILDING_DATA, SCREEN_HEIGHT):

    panel_w, panel_h = 270, 125
    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (15, 15, 35, 200), (0, 0, panel_w, panel_h), border_radius=10)
    pygame.draw.rect(panel_surf, (60, 80, 140, 160), (0, 0, panel_w, panel_h), 2, border_radius=10)
    screen.blit(panel_surf, (10, 10))

    hud_font = pygame.font.SysFont(None, 22)
    val_font = pygame.font.SysFont(None, 26)
    tiny = pygame.font.SysFont(None, 18)

    # Funds label + value
    screen.blit(hud_font.render("FUNDS", True, (140, 140, 200)), (20, 18))
    money_color = (255, 80, 80) if money_system.money < 50 else (100, 255, 140)
    screen.blit(val_font.render(f"${money_system.money}", True, money_color), (20, 34))

    # Lifeline label
    screen.blit(hud_font.render("LIFELINE", True, (140, 140, 200)), (20, 58))

    # Health bar
    bar_x, bar_y, bar_w, bar_h = 20, 76, 235, 11
    pygame.draw.rect(screen, (60, 20, 20), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
    fill_w = int(bar_w * (player_health / 100))

    if player_health > 60:
        bar_color = (60, 200, 80)
    elif player_health > 30:
        bar_color = (220, 180, 0)
    else:
        bar_color = (220, 50, 50)

    pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_w, bar_h), border_radius=5)
    pygame.draw.rect(screen, (180, 180, 180), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=5)
    screen.blit(tiny.render(f"{player_health}%", True, (200, 200, 200)), (bar_x + bar_w + 4, bar_y))

    # Selected building
    selected_label = BUILDING_DATA[selected_building]["label"] if selected_building else "None"
    screen.blit(tiny.render(f"[B]  {selected_label} | Click tile to place", True, (200, 200, 140)), (20, 96))
    screen.blit(tiny.render("Click building to upgrade",True, (100, 100, 100)), (20, 112))

    money_system.draw(screen, val_font)

# build menu
def draw_build_menu(screen, menu_x, SCREEN_WIDTH, MENU_WIDTH, menu_panel,
                    menu_icons, BUILDING_DATA, selected_building,
                    tiny_font, menu_title_font, SCREEN_HEIGHT):

    if menu_x >= SCREEN_WIDTH:
        return [], None

    slot_rects = []
    
    # Everything is anchored to the right edge of the screen
    panel_w = 260
    panel_x = SCREEN_WIDTH - panel_w  # always flush to right edge

    # Draw panel image scaled exactly to panel_w
    if menu_panel:
        panel_scaled = pygame.transform.scale(menu_panel, (panel_w, SCREEN_HEIGHT))
        screen.blit(panel_scaled, (panel_x, 0))
    else:
        panel_surf = pygame.Surface((panel_w, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (12, 14, 30, 230), (0, 0, panel_w, SCREEN_HEIGHT))
        screen.blit(panel_surf, (panel_x, 0))

    # Slots sized to fit strictly within the panel
    slot_w  = 220
    slot_h  = 95
    slot_gap = 6
    start_y  = 90
    slot_x   = panel_x + (panel_w - slot_w) // 2  # centered inside panel

    mouse_pos    = pygame.mouse.get_pos()
    hovered_type = None

    label_font = pygame.font.SysFont(None, 22)
    stat_font  = pygame.font.SysFont(None, 19)
    GOLD      = (255, 215, 0)
    GREEN     = (100, 220, 120)
    BLUE      = (100, 190, 255)
    WHITE     = (255, 255, 255)
    RED_COL   = (220, 100, 100)
    HIGHLIGHT = (255, 230, 120)

    for i, b_type in enumerate(MENU_ORDER):
        slot_y = start_y + i * (slot_h + slot_gap)
        rect   = pygame.Rect(slot_x, slot_y, slot_w, slot_h)
        slot_rects.append((rect, b_type))

        is_selected = selected_building == b_type
        is_hovered  = rect.collidepoint(mouse_pos)
        if is_hovered:
            hovered_type = b_type

        # Slot background
        slot_surf = pygame.Surface((slot_w, slot_h), pygame.SRCALPHA)
        bg_color  = (60, 45, 20, 210) if is_selected else (30, 20, 10, 180)
        pygame.draw.rect(slot_surf, bg_color, (0, 0, slot_w, slot_h), border_radius=10)
        border_color = (*HIGHLIGHT, 255) if is_selected else (120, 80, 30, 200)
        border_w = 3 if is_selected else 1
        pygame.draw.rect(slot_surf, border_color, (0, 0, slot_w, slot_h), border_w, border_radius=10)
        screen.blit(slot_surf, (slot_x, slot_y))

        # Icon
        icon = menu_icons[b_type]
        icon_scaled = pygame.transform.scale(icon, (44, 44))
        screen.blit(icon_scaled, (slot_x + 6, slot_y + 24))

        data = BUILDING_DATA[b_type]

        # Name
        name_surf = label_font.render(data["label"], True, WHITE)
        screen.blit(name_surf, (slot_x + 58, slot_y + 8))

        # Cost
        cost_surf = stat_font.render(f"Cost: ${data['cost']}", True, RED_COL)
        screen.blit(cost_surf, (slot_x + 58, slot_y + 30))

        # Income and health on separate lines
        stat_y = slot_y + 50
        if data["income"] > 0:
            inc_surf = stat_font.render(f"+${data['income']}/tick", True, GREEN)
            screen.blit(inc_surf, (slot_x + 58, stat_y))
            stat_y += 18

        if data["health"] > 0:
            hp_surf = stat_font.render(f"+{data['health']} lifeline/tick", True, BLUE)
            screen.blit(hp_surf, (slot_x + 58, stat_y))

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
def draw_bomb_animation(screen, bomb_img, bomb_anim_active, bomb_anim_start, BOMB_ANIM_DURATION, SCREEN_WIDTH, SCREEN_HEIGHT):
    
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
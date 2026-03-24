import pygame
import random

# Bomb animation
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

# Screen shake effect
def apply_screen_shake(shake_strength):
    return (random.randint(-shake_strength, shake_strength), random.randint(-shake_strength, shake_strength))
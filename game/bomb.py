import pygame
import random


class BombingEvent:
    def __init__(self, interval=30000, damage=20, shake_duration=500, missile_speed=7):
        self.interval = interval
        self.damage = damage
        self.shake_duration = shake_duration
        self.missile_speed = missile_speed

        self.last_bomb = pygame.time.get_ticks()
        self.shaking = False
        self.shake_start_time = 0
        self.sound = None

        self.missile_active = False
        self.missile_pos = pygame.Vector2(0, 0)
        self.target_pos = pygame.Vector2(0, 0)
        self.flash_until = 0

    def load_sound(self, path):
        self.sound = pygame.mixer.Sound(path)

    def start_missile(self, target_pos):
        self.target_pos = pygame.Vector2(target_pos)

        # Start above the screen, roughly near the target
        start_x = self.target_pos.x + random.randint(-120, 120)
        start_y = -80

        self.missile_pos = pygame.Vector2(start_x, start_y)
        self.missile_active = True

    def update(self, player_health, target_pos=None):
        current_time = pygame.time.get_ticks()
        shake_offset = (0, 0)

        # Launch a new bomb when interval passes
        if not self.missile_active and current_time - self.last_bomb >= self.interval:
            self.last_bomb = current_time
            if target_pos is not None:
                self.start_missile(target_pos)

        # Move the bomb toward the target
        if self.missile_active:
            direction = self.target_pos - self.missile_pos
            distance = direction.length()

            if distance <= self.missile_speed:
                self.missile_pos = self.target_pos
                self.missile_active = False
                self.shaking = True
                self.shake_start_time = current_time
                self.flash_until = current_time + 220
                player_health -= self.damage

                if self.sound:
                    self.sound.play()
            else:
                direction = direction.normalize()
                self.missile_pos += direction * self.missile_speed

        # Screen shake after impact
        if self.shaking:
            elapsed = current_time - self.shake_start_time
            if elapsed < self.shake_duration:
                shake_offset = (random.randint(-6, 6), random.randint(-6, 6))
            else:
                self.shaking = False

        return player_health, shake_offset

    def draw(self, surface, dx=0, dy=0):
        current_time = pygame.time.get_ticks()

        # Draw falling bomb
        if self.missile_active:
            missile_x = int(self.missile_pos.x + dx)
            missile_y = int(self.missile_pos.y + dy)

            # Flame trail
            pygame.draw.line(
                surface,
                (255, 170, 60),
                (missile_x, missile_y - 28),
                (missile_x, missile_y + 14),
                6
            )

            # Bomb body
            pygame.draw.circle(surface, (210, 210, 210), (missile_x, missile_y), 11)
            pygame.draw.circle(surface, (80, 80, 80), (missile_x, missile_y), 11, 2)

        # Impact flash
        if current_time < self.flash_until:
            flash = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(flash, (255, 170, 60, 170), (60, 60), 38)
            pygame.draw.circle(flash, (255, 235, 180, 220), (60, 60), 18)

            surface.blit(
                flash,
                (int(self.target_pos.x - 60 + dx), int(self.target_pos.y - 60 + dy))
            )
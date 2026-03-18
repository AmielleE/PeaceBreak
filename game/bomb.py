import pygame
import random

class BombingEvent:
    def __init__(self, interval=30000, damage=20, shake_duration=500):
        self.interval = interval # milliseconds between bombings
        self.damage = damage # health lost per bombing
        self.shake_duration = shake_duration # duration of screen shake in ms
        self.last_bomb = pygame.time.get_ticks()
        self.shaking = False
        self.shake_start_time = 0
        self.sound = None

    def load_sound(self, path):
        self.sound = pygame.mixer.Sound(path)

    def update(self, player_health):
        # Returns updated health and shake offset
        current_time = pygame.time.get_ticks()
        shake_offset = (0,0)

        # Trigger bomb if interval passed
        if current_time - self.last_bomb >= self.interval:
            self.last_bomb = current_time
            self.shaking = True
            self.shake_start_time = current_time
            player_health -= self.damage
            if self.sound:
                self.sound.play()

        # Handle screen shake
        if self.shaking:
            elapsed = current_time - self.shake_start_time
            if elapsed < self.shake_duration:
                shake_offset = (random.randint(-5,5), random.randint(-5,5))
            else:
                self.shaking = False

        return player_health, shake_offset
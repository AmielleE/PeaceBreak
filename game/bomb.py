import pygame
import random
import os

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
        self.craters = []
        self.crater_patches = []
        self.missile_active = False
        self.missile_pos = pygame.Vector2(0, 0)
        self.target_pos = pygame.Vector2(0, 0)
        self.flash_until = 0
        self.pending_target_tile = None

    def load_sound(self, path):
        if path and os.path.exists(path):
            self.sound = pygame.mixer.Sound(path)

    def start_missile(self, target_pixel_pos):
        self.target_pos = pygame.Vector2(target_pixel_pos)
        start_x = self.target_pos.x + random.randint(-120, 120)
        start_y = -80
        self.missile_pos = pygame.Vector2(start_x, start_y)
        self.missile_active = True

    def get_connected_patch(self, origin, buildable_tiles):
        buildable_set = set(buildable_tiles)
        visited = set()
        stack = [origin]
        patch = []

        while stack:
            tile = stack.pop()
            if tile in visited:
                continue
            if tile not in buildable_set:
                continue
            visited.add(tile)
            patch.append(tile)
            tx, ty = tile
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbour = (tx + dx, ty + dy)
                if neighbour not in visited:
                    stack.append(neighbour)

        return patch

    def apply_crater(self, buildings, buildable_tiles):
        if self.pending_target_tile is None:
            return

        origin = self.pending_target_tile

        # Small local crater patch instead of flood-filling the whole connected road
        patch = [
            origin,
            (origin[0] - 1, origin[1]),
            (origin[0] + 1, origin[1]),
            (origin[0], origin[1] - 1),
            (origin[0], origin[1] + 1),
        ]

        valid_patch = []
        for tile in patch:
            x, y = tile
            if x < 0 or y < 0:
                continue
            valid_patch.append(tile)

        for tile in valid_patch:
            if tile not in self.craters:
                self.craters.append(tile)

        # draw crater image centered on impact tile
        ox, oy = origin
        self.crater_patches.append((ox, oy, ox, oy))

        # Damage buildings touching crater
        damaged = set()
        for tile, building in list(buildings.items()):
            if id(building) in damaged:
                continue

            if any(b_tile in valid_patch for b_tile in building["tiles"]):
                damaged.add(id(building))

                if building["level"] > 0:
                    building["level"] -= 1
                else:
                    for t in building["tiles"]:
                        if t in buildings:
                            del buildings[t]

        self.pending_target_tile = None

    def update(self, player_health, buildable_tiles, buildings, target_pos=None, target_tile=None):
        current_time = pygame.time.get_ticks()
        shake_offset = (0, 0)
        bombed = False

        # Launch missile when interval passes
        if not self.missile_active and current_time - self.last_bomb >= self.interval:
            self.last_bomb = current_time
            if target_pos is not None:
                self.start_missile(target_pos)
                self.pending_target_tile = target_tile

        # Move missile
        if self.missile_active:
            direction = self.target_pos - self.missile_pos
            distance  = direction.length()

            if distance <= self.missile_speed:
                self.missile_pos    = self.target_pos
                self.missile_active = False
                self.shaking        = True
                self.shake_start_time = current_time
                self.flash_until    = current_time + 220
                player_health      -= self.damage
                bombed              = True

                if self.sound:
                    self.sound.play()

                self.apply_crater(buildings, buildable_tiles)
            else:
                self.missile_pos += direction.normalize() * self.missile_speed

        # Screen shake
        if self.shaking:
            elapsed = current_time - self.shake_start_time
            if elapsed < self.shake_duration:
                shake_offset = (random.randint(-6, 6), random.randint(-6, 6))
            else:
                self.shaking = False

        return player_health, shake_offset, bombed

    def draw(self, surface, dx=0, dy=0):
        current_time = pygame.time.get_ticks()

        if self.missile_active:
            missile_x = int(self.missile_pos.x + dx)
            missile_y = int(self.missile_pos.y + dy)
            pygame.draw.line(surface, (255, 170, 60),
                             (missile_x, missile_y - 28),
                             (missile_x, missile_y + 14), 6)
            pygame.draw.circle(surface, (210, 210, 210), (missile_x, missile_y), 11)
            pygame.draw.circle(surface, (80, 80, 80),    (missile_x, missile_y), 11, 2)

        if current_time < self.flash_until:
            flash = pygame.Surface((120, 120), pygame.SRCALPHA)
            pygame.draw.circle(flash, (255, 170, 60, 170),  (60, 60), 38)
            pygame.draw.circle(flash, (255, 235, 180, 220), (60, 60), 18)
            surface.blit(flash, (int(self.target_pos.x - 60 + dx),
                                 int(self.target_pos.y - 60 + dy)))
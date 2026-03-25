import pygame
import random
import os

class BombingEvent:
    def __init__(self, interval=30000, damage=20, shake_duration=500):
        self.interval = interval
        self.damage = damage
        self.shake_duration = shake_duration
        self.last_bomb = pygame.time.get_ticks()
        self.shaking = False
        self.shake_start_time = 0
        self.sound = None
        self.craters = [] # list of individual (tile_x, tile_y) tiles that are cratered
        self.crater_patches = [] # list of patch origins for drawing one crater image per patch

    def load_sound(self, path):
        if path and os.path.exists(path):
            self.sound = pygame.mixer.Sound(path)

    def get_connected_patch(self, origin, buildable_tiles):
        """Flood fill from origin to find all connected grey tiles in the same patch."""
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
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                neighbour = (tx + dx, ty + dy)
                if neighbour not in visited:
                    stack.append(neighbour)

        return patch

    def trigger_bomb(self, player_health, buildable_tiles, buildings):
        if buildable_tiles:
            origin = random.choice(buildable_tiles)
            patch  = self.get_connected_patch(origin, buildable_tiles)

            # add all patch tiles to craters FIRST
            for tile in patch:
                if tile not in self.craters:
                    self.craters.append(tile)

            # store patch bounds for drawing
            if patch:
                min_x = min(t[0] for t in patch)
                min_y = min(t[1] for t in patch)
                max_x = max(t[0] for t in patch)
                max_y = max(t[1] for t in patch)
                self.crater_patches.append((min_x, min_y, max_x, max_y))

            # destroy buildings AFTER crater_set is fully built
            crater_set = set(self.craters)
            to_remove = set()
            for tile, building in list(buildings.items()):
                for b_tile in building["tiles"]:
                    if b_tile in crater_set:
                        for t in building["tiles"]:
                            to_remove.add(t)
                        break

            for t in to_remove:
                if t in buildings:
                    del buildings[t]

        player_health -= self.damage
        if self.sound:
            self.sound.play()
        return player_health

    def update(self, player_health, buildable_tiles, buildings):
        current_time = pygame.time.get_ticks()
        shake_offset = (0, 0)
        bombed = False

        if current_time - self.last_bomb >= self.interval:
            self.last_bomb = current_time
            self.shaking = True
            self.shake_start_time = current_time
            player_health = self.trigger_bomb(player_health, buildable_tiles, buildings)
            bombed = True

        if self.shaking:
            elapsed = current_time - self.shake_start_time
            if elapsed < self.shake_duration:
                shake_offset = (random.randint(-5, 5), random.randint(-5, 5))
            else:
                self.shaking = False

        return player_health, shake_offset, bombed
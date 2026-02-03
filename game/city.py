from building import *

class City:
    def __init__(self):
        self.gold = 120
        self.materials = 60
        self.turn = 1
        self.grid = [[None for _ in range(6)] for _ in range(6)]

    def place_building(self, r, c, building):
        if self.grid[r][c] is None and self.materials >= building.cost:
            self.grid[r][c] = building
            self.materials -= building.cost

    def next_turn(self):
        self.turn += 1
        self.gold += 25
        self.materials += 15

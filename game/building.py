class Building:
    def __init__(self, name, cost, max_hp, defense):
        self.name = name
        self.cost = cost
        self.hp = max_hp
        self.max_hp = max_hp
        self.defense = defense

    def take_damage(self, damage):
        reduced = max(0, damage - self.defense)
        self.hp -= reduced
        return reduced

    def is_destroyed(self):
        return self.hp <= 0

WOOD_WALL = Building("Wood Wall", 10, 30, 1)
STEEL_WALL = Building("Steel Wall", 25, 80, 4)
TOWER = Building("Defense Tower", 40, 60, 6)

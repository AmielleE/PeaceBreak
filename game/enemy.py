import random

class EnemyRaid:
    def __init__(self):
        self.damage = random.randint(10, 30)

    def attack(self, city):
        targets = [
            (r, c)
            for r in range(6)
            for c in range(6)
            if city.grid[r][c]
        ]

        if not targets:
            return "No buildings to attack"

        r, c = random.choice(targets)
        building = city.grid[r][c]
        damage_done = building.take_damage(self.damage)

        if building.is_destroyed():
            city.grid[r][c] = None
            return f"{building.name} destroyed!"

        return f"{building.name} took {damage_done} damage"

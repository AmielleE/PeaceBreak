import pygame

class MoneySystem:
    def __init__(self, start_amount=50, increment=0, interval=3000, cap=9999):
        self.money = start_amount
        self.increment = increment
        self.interval = interval
        self.cap = cap 
        self.last_update = pygame.time.get_ticks()
        self.animations = []  # floating money animations

    def update(self):
        current_time = pygame.time.get_ticks()
        # Passive income over time
        if current_time - self.last_update >= self.interval:
            self.last_update = current_time

        # Update floating animations
        for anim in self.animations[:]:
            anim['pos'][1] -= 1 # float up
            anim['alpha'] -= 5 # fade
            if anim['alpha'] <= 0:
                self.animations.remove(anim)

    def change_money(self, amount, pos):
        if amount > 0:
            amount = min(amount, self.cap - self.money) # cap positive changes too
        self.money = max(0, self.money + amount)
        self.animations.append({'amount': amount, 'pos': list(pos), 'alpha': 255})

    def draw(self, surface, font, position=(20, 20)):
    # Only draw floating animations, HUD draws the static money value
        for anim in self.animations:
            text = f"+${anim['amount']}" if anim['amount'] > 0 else f"${anim['amount']}"
            main_color = (100, 255, 140) if anim['amount'] > 0 else (255, 80, 80)

            base = font.render(text, True, main_color)
            outline = font.render(text, True, (0, 0, 0))

            x, y = anim['pos']
            base.set_alpha(anim['alpha'])
            outline.set_alpha(anim['alpha'])

            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        surface.blit(outline, (x + dx, y + dy))
            surface.blit(base, (x, y))
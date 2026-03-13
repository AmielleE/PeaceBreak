import pygame

class MoneySystem:
    def __init__(self, start_amount=0, increment=10, interval=3000):
        self.money = start_amount
        self.increment = increment
        self.interval = interval
        self.last_update = pygame.time.get_ticks()
        self.animations = []  # floating money animations

    def update(self):
        current_time = pygame.time.get_ticks()
        # Automatic income
        if current_time - self.last_update >= self.interval:
            self.money += self.increment
            self.last_update = current_time
            # floating coin animation at fixed position
            self.animations.append({'amount': self.increment, 'pos':[20, 20], 'alpha':255})

        # Update floating animations
        for anim in self.animations[:]:
            anim['pos'][1] -= 1       # float up
            anim['alpha'] -= 5        # fade
            if anim['alpha'] <= 0:
                self.animations.remove(anim)

    def change_money(self, amount, pos):
        """Animate money change at given position."""
        self.money += amount
        self.animations.append({'amount': amount, 'pos': list(pos), 'alpha': 255})

    def draw(self, surface, font, position=(20, 20)):
        # Draw main money
        money_surface = font.render(f"Money: ${self.money}", True, (255, 215, 0))  # gold
        surface.blit(money_surface, position)

        # Draw floating animations
        for anim in self.animations:
            color = (0, 255, 0) if anim['amount'] > 0 else (255, 0, 0)
            text = f"+${anim['amount']}" if anim['amount'] > 0 else f"${anim['amount']}"
            text_surface = font.render(text, True, color)
            text_surface.set_alpha(anim['alpha'])
            surface.blit(text_surface, anim['pos'])
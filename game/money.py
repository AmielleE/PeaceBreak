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
            anim['pos'][1] -= 1 # float up
            anim['alpha'] -= 5 # fade
            if anim['alpha'] <= 0:
                self.animations.remove(anim)

    def change_money(self, amount, pos):
        """Animate money change at given position."""
        self.money += amount
        self.animations.append({'amount': amount, 'pos': list(pos), 'alpha': 255})

    def draw(self, surface, font, position=(20, 20)):
        def draw_text_with_outline(text, pos, main_color, outline_color=(0, 0, 0)):
            # Render base text
            base = font.render(text, True, main_color)
            outline = font.render(text, True, outline_color)

            x, y = pos

            # Draw outline (8 directions)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        surface.blit(outline, (x + dx, y + dy))

            # Draw main text on top
            surface.blit(base, (x, y))

        # Draw main money (white with black outline)
        draw_text_with_outline(f"Money: ${self.money}", position, (255, 255, 255))

        # Draw floating animations
        for anim in self.animations:
            text = f"+${anim['amount']}" if anim['amount'] > 0 else f"${anim['amount']}"

            # Color logic
            main_color = (255, 255, 255) if anim['amount'] > 0 else (255, 0, 0)

            base = font.render(text, True, main_color)
            outline = font.render(text, True, (0, 0, 0))

            x, y = anim['pos']

            # Apply alpha to both
            base.set_alpha(anim['alpha'])
            outline.set_alpha(anim['alpha'])

            # Draw outline
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        surface.blit(outline, (x + dx, y + dy))

            # Draw main text
            surface.blit(base, (x, y))
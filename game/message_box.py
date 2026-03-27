import pygame

class MessageBox:
    def __init__(self):
        self.message = ""
        self.submessage = ""
        self.timer = 0
        self.duration = 3500
        self.active = False
        self.box_type = "tip"  # "tip", "war", "score", "event"
        self.position = "bottom"  # "bottom" or "corner"

    def show(self, message, submessage="", duration=6000, box_type="tip", position="bottom"):
        self.message = message
        self.submessage = submessage
        self.timer = pygame.time.get_ticks()
        self.duration = duration
        self.active = True
        self.position = position
        self.box_type = box_type

    def draw(self, screen, SCREEN_WIDTH, SCREEN_HEIGHT):
        if not self.active:
            return

        elapsed = pygame.time.get_ticks() - self.timer
        if elapsed >= self.duration:
            self.active = False
            return

        # Fade in/out
        fade_time = 300
        if elapsed < fade_time:
            alpha = int(255 * (elapsed / fade_time))
        elif elapsed > self.duration - fade_time:
            alpha = int(255 * (1 - (elapsed - (self.duration - fade_time)) / fade_time))
        else:
            alpha = 255

        # Box style per type
        type_styles = {
            "tip":   {"border": (80, 160, 80),  "bg": (20, 50, 20),  "icon": "TIP"},
            "game_tip": {"border": (80, 160, 80),  "bg": (20, 50, 20),  "icon": "TIP"},
            "war":   {"border": (200, 40, 40),   "bg": (60, 10, 10),  "icon": "CONFLICT ALERT"},
            "score": {"border": (200, 170, 0),   "bg": (50, 40, 0),   "icon": "MILESTONE"},
            "event": {"border": (60, 120, 200),  "bg": (10, 25, 60),  "icon": "EVENT"},
        }
        style = type_styles.get(self.box_type, type_styles["tip"])

        if self.position == "corner":
            box_w, box_h = 230, 68
            box_x = 15
            box_y = 148 # sits just below the HUD panel
        else:
            box_w, box_h = 480, 110
            box_x = SCREEN_WIDTH // 2 - box_w // 2
            box_y = SCREEN_HEIGHT - box_h - 30

        # Draw box
        surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg = (*style["bg"], min(alpha, 220))
        border = (*style["border"], alpha)

        pygame.draw.rect(surf, bg, (0, 0, box_w, box_h), border_radius=12)
        pygame.draw.rect(surf, border, (0, 0, box_w, box_h), 3, border_radius=12)

        # Icon/label bar
        label_font = pygame.font.SysFont(None, 18)   # was 20
        msg_font = pygame.font.SysFont(None, 20 if self.position == "corner" else 26)
        sub_font = pygame.font.SysFont(None, 17 if self.position == "corner" else 21)

        label_surf = label_font.render(style["icon"], True, style["border"])
        label_surf.set_alpha(alpha)
        surf.blit(label_surf, (14, 10))

        msg_surf = msg_font.render(self.message, True, (255, 255, 255))
        msg_surf.set_alpha(alpha)
        surf.blit(msg_surf, (14, 34))

        if self.submessage:
            sub_surf = sub_font.render(self.submessage, True, (180, 180, 180))
            sub_surf.set_alpha(alpha)
            surf.blit(sub_surf, (14, 64))

        screen.blit(surf, (box_x, box_y))
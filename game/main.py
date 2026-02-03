import pygame
from config import *
from city import City
from ui import Button

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("City Defense (SDG Game)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)

city = City()
build_mode = False

build_button = Button(600, 120, 200, 40, "Build Wall (10)")
turn_button = Button(600, 180, 200, 40, "End Turn")

running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)

    # HUD
    screen.blit(font.render(f"Gold: {city.gold}", True, BLACK), (50, 20))
    screen.blit(font.render(f"Materials: {city.materials}", True, BLACK), (200, 20))
    screen.blit(font.render(f"Turn: {city.turn}", True, BLACK), (400, 20))

    # Grid
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(
                GRID_OFFSET_X + col * CELL_SIZE,
                GRID_OFFSET_Y + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(screen, GRAY, rect, 1)

            if city.grid[row][col]:
                pygame.draw.rect(screen, GREEN, rect.inflate(-10, -10))

    # Buttons
    build_button.draw(screen)
    turn_button.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if build_button.clicked(event):
            build_mode = True

        if turn_button.clicked(event):
            city.next_turn()

        if build_mode and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    rect = pygame.Rect(
                        GRID_OFFSET_X + c * CELL_SIZE,
                        GRID_OFFSET_Y + r * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    if rect.collidepoint(mx, my):
                        city.build(r, c)
                        build_mode = False

    pygame.display.flip()

pygame.quit()
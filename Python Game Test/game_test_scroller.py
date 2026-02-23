import pygame, random

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

player = pygame.Rect(380, 520, 40, 40)
falling = []
score = 0
running = True

while running:
    # 1) handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  player.x -= 6
    if keys[pygame.K_RIGHT]: player.x += 6

    # 2) update game state
    if random.random() < 0.03:
        falling.append(pygame.Rect(random.randint(0, 760), 0, 40, 40))

    for obj in falling:
        obj.y += 6
        if obj.colliderect(player):
            running = False

    score += 1

    # 3) draw everything
    screen.fill((20, 20, 20))
    pygame.draw.rect(screen, (200, 200, 255), player)
    for obj in falling:
        pygame.draw.rect(screen, (255, 120, 120), obj)

    pygame.display.flip()
    clock.tick(60)

print("Game over! Score:", score)
pygame.quit()
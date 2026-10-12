import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
DARK_GRAY = (47, 67, 65)
LIGHT_GRAY = (226, 243, 242)
GROUND_COLOR = (235, 229, 199)
GRASS_COLOR = (87, 145, 112)
CACTUS_COLOR = (75, 133, 103)

# Setup Display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chrome Dino Game Clone")
clock = pygame.time.Clock()

class Dinosaur:
    def __init__(self):
        self.width = 40
        self.height = 50
        self.x = 50
        self.y = SCREEN_HEIGHT - self.height - 50
        self.color = DARK_GRAY
        
        # Physics variables
        self.velocity_y = 0
        self.gravity = 0.6
        self.jump_strength = -12
        self.is_jumping = False
        self.ground_y = self.y

    def handle_event(self, event):
        # Jump if Spacebar or Up Arrow is pressed
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not self.is_jumping:
                self.velocity_y = self.jump_strength
                self.is_jumping = True

    def update(self):
        # Apply gravity
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # Prevent falling through the ground
        if self.y >= self.ground_y:
            self.y = self.ground_y
            self.velocity_y = 0
            self.is_jumping = False

    def draw(self, surface):
        pixel = 5
        # Keep the silhouette blocky while leaving the collision box unchanged.
        pygame.draw.rect(surface, self.color, (self.x + 5, self.y + 20, 25, 22))
        pygame.draw.rect(surface, self.color, (self.x + 20, self.y + 5, 20, 23))
        pygame.draw.rect(surface, self.color, (self.x + 30, self.y + 15, 10, 10))
        pygame.draw.rect(surface, self.color, (self.x, self.y + 28, 10, 7))
        pygame.draw.rect(surface, self.color, (self.x + 15, self.y + 37, 6, 6))
        pygame.draw.rect(surface, LIGHT_GRAY, (self.x + 31, self.y + 10, pixel, pixel))
        pygame.draw.rect(surface, self.color, (self.x + 37, self.y + 19, 3, 3))

        leg_y = self.y + 41
        if not self.is_jumping:
            step = (pygame.time.get_ticks() // 110) % 2
            pygame.draw.rect(surface, self.color, (self.x + 10, leg_y, 7, 9 if step else 5))
            pygame.draw.rect(surface, self.color, (self.x + 24, leg_y, 7, 5 if step else 9))
        else:
            pygame.draw.rect(surface, self.color, (self.x + 10, leg_y, 7, 7))
            pygame.draw.rect(surface, self.color, (self.x + 24, leg_y, 7, 7))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Cactus:
    def __init__(self):
        # Select a random width variation for obstacles
        self.width = random.choice([20, 30, 40]) 
        self.height = random.randint(40, 70)
        self.x = SCREEN_WIDTH + random.randint(0, 200)
        self.y = SCREEN_HEIGHT - self.height - 50
        self.speed = 7
        self.color = DARK_GRAY

    def update(self):
        self.x -= self.speed

    def draw(self, surface):
        stem_width = max(8, self.width // 3)
        stem_x = self.x + (self.width - stem_width) // 2
        pygame.draw.rect(surface, self.color, (stem_x, self.y, stem_width, self.height))
        pygame.draw.rect(surface, self.color, (self.x, self.y + self.height // 2, stem_x - self.x + 3, 8))
        pygame.draw.rect(surface, self.color, (self.x, self.y + self.height // 2 - 10, 8, 18))
        arm_x = stem_x + stem_width - 3
        pygame.draw.rect(surface, self.color, (arm_x, self.y + self.height // 3, self.x + self.width - arm_x, 8))
        pygame.draw.rect(surface, self.color, (self.x + self.width - 8, self.y + self.height // 3 - 9, 8, 17))
        pygame.draw.line(surface, (133, 181, 132), (stem_x + 2, self.y + 7),
                         (stem_x + 2, self.y + self.height - 5), 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


def main():
    dino = Dinosaur()
    obstacles = []
    score = 0
    game_over = False
    spawn_timer = 0

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(LIGHT_GRAY)

        # Distant hills and clouds give the playfield depth without hiding hazards.
        pygame.draw.circle(screen, (255, 203, 113), (690, 78), 27)
        pygame.draw.ellipse(screen, (193, 222, 211), (330, 205, 300, 95))
        pygame.draw.ellipse(screen, (193, 222, 211), (520, 188, 350, 112))
        for cloud_x, cloud_y in ((90, 75), (385, 112), (565, 57)):
            pygame.draw.circle(screen, (250, 253, 245), (cloud_x, cloud_y), 15)
            pygame.draw.circle(screen, (250, 253, 245), (cloud_x + 18, cloud_y - 5), 19)
            pygame.draw.circle(screen, (250, 253, 245), (cloud_x + 39, cloud_y), 14)
            pygame.draw.rect(screen, (250, 253, 245), (cloud_x, cloud_y, 39, 14))

        ground_y = SCREEN_HEIGHT - 50
        pygame.draw.rect(screen, GROUND_COLOR, (0, ground_y, SCREEN_WIDTH, 50))
        pygame.draw.line(screen, GRASS_COLOR, (0, ground_y), (SCREEN_WIDTH, ground_y), 3)
        for mark_x in range(-20, SCREEN_WIDTH, 47):
            offset = (pygame.time.get_ticks() // 7) % 47
            pygame.draw.rect(screen, (191, 181, 143), (mark_x - offset, ground_y + 16, 9, 2))
            pygame.draw.rect(screen, (191, 181, 143), (mark_x - offset + 19, ground_y + 32, 4, 2))

        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            if not game_over:
                dino.handle_event(event)
            else:
                # Restart game if R key is pressed
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    main() 

        if not game_over:
            # 2. Update Game Entities
            dino.update()
            
            # Manage obstacle spawning
            spawn_timer += 1
            if spawn_timer > random.randint(60, 120): 
                obstacles.append(Cactus())
                spawn_timer = 0

            # Update obstacles
            for obstacle in obstacles[:]:
                obstacle.update()
                if obstacle.x + obstacle.width < 0:
                    obstacles.remove(obstacle)
                    score += 1 

                # Collision Detection
                if dino.get_rect().colliderect(obstacle.get_rect()):
                    game_over = True

        # 3. Render / Draw Entities
        dino.draw(screen)
        for obstacle in obstacles:
            obstacle.draw(screen)

        # 4. Draw Score
        font = pygame.font.SysFont("Courier", 20, bold=True)
        score_text = font.render(f"SCORE: {score}", True, DARK_GRAY)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 20))

        # 5. Draw Game Over Screen
        if game_over:
            game_over_text = font.render("G A M E   O V E R", True, DARK_GRAY)
            restart_text = font.render("Press 'R' to Restart", True, DARK_GRAY)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 10))

        pygame.display.update()

if __name__ == "__main__":
    main()

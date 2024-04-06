import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH = 600
HEIGHT = 800
FPS = 60
GRAVITY = 0.25
FLAP_STRENGTH = -6  # Increased flap strength
PIPE_GAP_HEIGHT = 300  # Height of the gap between pipes
PIPE_SPEED = 3
SCORE_INCREMENT = 25  # Score increment for passing through a pipe
GAME_DURATION = 30  # Game duration in seconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 250)
GREEN = (34, 139, 34)

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flying Pig")

# Load images
pig_img = pygame.image.load("pig.png").convert_alpha()
pipe_img = pygame.image.load("pipe.png").convert_alpha()

# Scale images
pig_img = pygame.transform.scale(pig_img, (60, 45))
pipe_img = pygame.transform.scale(pipe_img, (100, 800))

# Pig class
class Pig(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pig_img
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 3 + 50)  # Adjusted starting position
        self.vel_y = 0
        self.clicked = False

    def update(self):
        if self.clicked:
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y
            self.rect.y = min(max(0, self.rect.y), HEIGHT - self.rect.height)

    def flap_up(self):
        if self.clicked:
            self.vel_y = FLAP_STRENGTH

    def flap_down(self):
        if self.clicked:
            self.vel_y = FLAP_STRENGTH * 2

    def start_game(self):
        self.clicked = True

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 3 + 50)  # Adjusted starting position
        self.vel_y = 0
        self.clicked = False

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pipe_img
        self.rect = self.image.get_rect()
        self.gap_y = random.randint(50, HEIGHT - PIPE_GAP_HEIGHT - 50)  # Adjusted gap position
        self.upper_pipe_height = self.gap_y
        self.lower_pipe_height = HEIGHT - self.gap_y - PIPE_GAP_HEIGHT
        self.upper_pipe_image = pygame.transform.scale(pipe_img, (self.rect.width, self.upper_pipe_height))
        self.lower_pipe_image = pygame.transform.scale(pipe_img, (self.rect.width, self.lower_pipe_height))
        self.rect_upper = self.upper_pipe_image.get_rect(topleft=(x, 0))
        self.rect_lower = self.lower_pipe_image.get_rect(topleft=(x, self.gap_y + PIPE_GAP_HEIGHT))

# Group for all sprites
all_sprites = pygame.sprite.Group()
pipes = pygame.sprite.Group()

# Create pig
pig = Pig()
all_sprites.add(pig)

# Font
font = pygame.font.SysFont(None, 40)
timer_font = pygame.font.SysFont(None, 30)

# Function to display text on the screen
def display_text(text, center, font, color=WHITE):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center)
    screen.blit(text_surface, text_rect)

# Background
background = pygame.Surface(screen.get_size())
background.fill(BLUE)  # Sky
pygame.draw.rect(background, GREEN, (0, HEIGHT - 100, WIDTH, 100))  # Grass

# Main game loop
clock = pygame.time.Clock()
game_start_time = pygame.time.get_ticks()  # Initialize game start time
score = 0
running = True

while running and (pygame.time.get_ticks() - game_start_time) < GAME_DURATION * 1000:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not pig.clicked:
                pig.start_game()  # Start the game when any key is pressed
            if event.key == pygame.K_u:
                pig.flap_up()  # Make the pig flap up
            elif event.key == pygame.K_d:
                pig.flap_down()  # Make the pig flap down

    # Update pig position
    pig.update()

    # Spawn pipes
    if pig.clicked and len(pipes) < 4:
        pipe = Pipe(WIDTH)
        pipes.add(pipe)
        all_sprites.add(pipe)

    # Update pipe positions
    for pipe in pipes:
        pipe.rect_upper.x -= PIPE_SPEED
        pipe.rect_lower.x -= PIPE_SPEED

    # Check for collisions
    hits = pygame.sprite.spritecollide(pig, pipes, False)
    if hits or pig.rect.bottom >= HEIGHT:
        running = False

    # Remove off-screen pipes
    for pipe in pipes:
        if pipe.rect_upper.right < 0:
            pipe.kill()

    # Check for passing through pipes and update score
    for pipe in pipes:
        if pipe.rect_upper.right < pig.rect.left and not hasattr(pipe, "passed"):
            score += SCORE_INCREMENT
            pipe.passed = True

    # Draw background
    screen.blit(background, (0, 0))

    # Draw pipes
    for pipe in pipes:
        screen.blit(pipe.upper_pipe_image, pipe.rect_upper)
        screen.blit(pipe.lower_pipe_image, pipe.rect_lower)

    # Draw pig
    screen.blit(pig.image, pig.rect)

    # Draw score
    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))

    # Timer
    time_remaining = max(0, GAME_DURATION - (pygame.time.get_ticks() - game_start_time) // 1000)
    timer_text = timer_font.render("Time: " + str(time_remaining) + "s", True, WHITE)
    screen.blit(timer_text, (WIDTH - timer_text.get_width() - 10, HEIGHT - timer_text.get_height() - 10))

    # Display instructions at the beginning
    if not pig.clicked:
        display_text("Ready player one?", (WIDTH // 2, HEIGHT // 3), font)  # Adjusted
        display_text("Press any key to start", (WIDTH // 2, HEIGHT // 2), font)
        display_text("Press U to move up, D to move down", (WIDTH // 2, HEIGHT * 3 // 4), font)

    pygame.display.flip()

# Display "GAME OVER!" text
display_text("GAME OVER!", (WIDTH // 2, HEIGHT // 3), font)
pygame.display.flip()

# Wait for a key press to restart the game
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            waiting = False
        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

pygame.quit()
sys.exit()

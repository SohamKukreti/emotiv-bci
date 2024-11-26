import pygame
import random
from multiprocessing import shared_memory
import struct

shm = shared_memory.SharedMemory(name="command_buffer")

def check_for_push():
    command_value = struct.unpack('I', shm.buf[:4])[0]
    if command_value == 1:  # 1 represents "push"
        shm.buf[:4] = struct.pack('I', 0)  # Reset to "no command"
        return "right"
    elif command_value == 2:
        shm.buf[:4] = struct.pack('I', 0)
        return "left"
    else:
        return "none"

# Initialize Pygame
pygame.init()
pygame.mixer.music.load("assets/countriestheme.ogg")
pygame.mixer.music.play(-1)
background = pygame.image.load("assets/ballbg.png")
# background = pygame.transform.scale(background, (background.get_width() * 0.7, background.get_height() * 0.7))


# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BALL_RADIUS = 15
FLOOR_HEIGHT = 20
HOLE_WIDTH = 80
BALL_SPEED = 0.5
MAX_SPEED = 12
FLOOR_GAP = 100
ACCELERATION = 0.4
DECELERATION = 0.1
IMPULSE_STRENGTH = 2.0
COIN_SIZE = 20  # Size of collectable squares

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Set up display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Ball Drop Game")
clock = pygame.time.Clock()

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, COIN_SIZE, COIN_SIZE)
        self.collected = False
    
    def draw(self, screen):
        if not self.collected:
            pygame.draw.rect(screen, YELLOW, (self.x, self.y, COIN_SIZE, COIN_SIZE))

    def check_collision(self, ball):
        if not self.collected:
            ball_rect = pygame.Rect(ball.x - BALL_RADIUS, ball.y - BALL_RADIUS, 
                                  BALL_RADIUS * 2, BALL_RADIUS * 2)
            if ball_rect.colliderect(self.rect):
                self.collected = True
                return True
        return False

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_y = 0
        self.velocity_x = 0
        self.falling = True
    
    def apply_impulse(self, direction):
        self.velocity_x += direction * IMPULSE_STRENGTH
        self.velocity_x = max(min(self.velocity_x, MAX_SPEED), -MAX_SPEED)
    
    def move(self, direction):
        if direction != 0:
            self.velocity_x += direction * ACCELERATION
            self.velocity_x = max(min(self.velocity_x, MAX_SPEED), -MAX_SPEED)
        else:
            if self.velocity_x > 0:
                self.velocity_x = max(0, self.velocity_x - DECELERATION)
            elif self.velocity_x < 0:
                self.velocity_x = min(0, self.velocity_x + DECELERATION)
        
        self.x += self.velocity_x
        
        if self.x < BALL_RADIUS:
            self.x = BALL_RADIUS
            self.velocity_x = -self.velocity_x * 0.5
        elif self.x > WINDOW_WIDTH - BALL_RADIUS:
            self.x = WINDOW_WIDTH - BALL_RADIUS
            self.velocity_x = -self.velocity_x * 0.5
    
    def update(self):
        if self.falling:
            self.velocity_y += 0.5
            self.y += self.velocity_y
    
    def draw(self, screen):
        pygame.draw.circle(screen, GREEN, (int(self.x), int(self.y)), BALL_RADIUS)

class Floor:
    def __init__(self, y):
        self.y = y
        self.hole_x = random.randint(HOLE_WIDTH, WINDOW_WIDTH - HOLE_WIDTH)
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (0, self.y, self.hole_x - HOLE_WIDTH//2, FLOOR_HEIGHT))
        pygame.draw.rect(screen, BLUE, (self.hole_x + HOLE_WIDTH//2, self.y, 
                                      WINDOW_WIDTH - (self.hole_x + HOLE_WIDTH//2), FLOOR_HEIGHT))
    
    def check_collision(self, ball):
        if ball.y + BALL_RADIUS >= self.y and ball.y - BALL_RADIUS <= self.y + FLOOR_HEIGHT:
            if ball.x < self.hole_x - HOLE_WIDTH//2 or ball.x > self.hole_x + HOLE_WIDTH//2:
                ball.y = self.y - BALL_RADIUS
                ball.velocity_y = 0
                ball.falling = False
                ball.velocity_x *= 0.95
                return True
        return False

class Game:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        self.ball = Ball(WINDOW_WIDTH // 2, 50)
        self.floors = []
        self.coins = []
        self.score = 0
        
        # Create floors
        for i in range(5):
            floor_y = 200 + i * FLOOR_GAP
            self.floors.append(Floor(floor_y))
            
            # Add coins above each floor
            for _ in range(random.randint(1,2)):  # 3 coins per floor
                coin_x = random.randint(COIN_SIZE, WINDOW_WIDTH - COIN_SIZE)
                coin_y = floor_y - 30  # Random height above floor
                self.coins.append(Coin(coin_x, coin_y))
        
        self.game_over = False
        self.won = False
    
    def update(self):
        self.ball.update()
        
        # Check floor collisions
        ball_on_floor = False
        for floor in self.floors:
            if floor.check_collision(self.ball):
                ball_on_floor = True
                break
        
        if not ball_on_floor:
            self.ball.falling = True
        
        # Check coin collisions
        for coin in self.coins:
            if coin.check_collision(self.ball):
                self.score += 10  # Increase score by 10 for each coin
        
        # Check if ball reached bottom
        if self.ball.y > WINDOW_HEIGHT:
            self.won = True
        
        # Check if ball went off screen
        if self.ball.y < 0:
            self.game_over = True
    
    def draw(self, screen):
        screen.fill(WHITE)
        #screen.blit(background, (0, 0))
        
        # Draw floors
        for floor in self.floors:
            floor.draw(screen)
        
        # Draw coins
        for coin in self.coins:
            coin.draw(screen)
        
        # Draw ball
        self.ball.draw(screen)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        
        # Draw game over or win message
        # if self.game_over or self.won:
        #     font = pygame.font.Font(None, 74)
        #     text = font.render(f"{'You Won!' if self.won else 'Game Over!'} Score: {self.score}", True, BLACK)
        #     text_rect = text.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        #     screen.blit(text, text_rect)

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game.game_over or game.won:
            game.reset_game()

        if not game.game_over and not game.won:
            keys = pygame.key.get_pressed()
            direction = 0
            if keys[pygame.K_LEFT]:
                direction -= 1
            if keys[pygame.K_RIGHT]:
                direction += 1
            
            var = check_for_push()
            if var == "left":
                game.ball.apply_impulse(-1)
            elif var == "right":
                game.ball.apply_impulse(1)
            
            game.ball.move(direction)
            game.update()

        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
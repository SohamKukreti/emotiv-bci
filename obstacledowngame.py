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

import pygame
import sys
import random

# Initialize Pygame
pygame.init()
pygame.mixer.music.load('assets/energy.mp3')
pygame.mixer.music.play(-1)
# Screen setup
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dodge the Obstacles")

# Colors
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)

# Game Variables
player_width = 50
player_height = 50
left_wall_x = 50  # Left wall position (x-coordinate)
right_wall_x = screen_width - 50 - player_width  # Right wall position (x-coordinate)
player_y = screen_height - player_height - 10
player_x = 0  # Start at the left wall
background_image = pygame.image.load("assets/background-black.png")
background_image = pygame.transform.scale(background_image, (800, 600))
player_speed = 5  # Initial speed
obstacle_speed = 2  # Initial speed of obstacles
obstacles = []  # List to hold the obstacles
slime_image = pygame.image.load("assets/slime.png")
player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
player_lives = 5

enemy_image = pygame.image.load("assets/enemy.png")

MIN_OBSTACLE_GAP = 400

score = 0
font = pygame.font.Font(None, 36)

# Initialize player direction variable
player_direction = 0  # 0 means no movement, -1 means move left, 1 means move right
player_x_speed = 0
# Function to display the score
def display_score():
    score_text = font.render(f"Score: {score}", True, green)
    live_text = font.render(f"Lives: {player_lives} ", True, (228, 77, 77))
    screen.blit(live_text, (700, 10))
    screen.blit(score_text, (10, 10))

def display_end():
    end_text = font.render(f"Game Over!", True, (255, 255, 255))
    screen.blit(end_text, (screen_width // 2, screen_height // 2))

# Function to generate obstacles
def generate_obstacles():
    global obstacles
    
    # If there are existing obstacles, check their position
    if obstacles:
        # Check for obstacles from the opposite side
        existing_obstacles = [obs for obs in obstacles if obs.x == 0 or obs.x == screen_width - 50]
        
        # Determine which side to generate an obstacle
        if not existing_obstacles:
            side = random.choice(['left', 'right'])
        else:
            # Find the maximum y position of existing obstacles
            max_y = max(obs.y for obs in existing_obstacles)
            
            # Only generate a new obstacle if there's enough vertical gap
            if max_y > MIN_OBSTACLE_GAP:
                side = 'left' if existing_obstacles[0].x == screen_width - 50 else 'right'
            else:
                return  # Skip obstacle generation if gap is insufficient
    else:
        side = random.choice(['left', 'right'])
    
    # Generate the obstacle
    x_pos = 0 if side == 'left' else screen_width - 50
    y_pos = -50
    obstacle_rect = pygame.Rect(x_pos, y_pos, 50, 50)
    obstacles.append(obstacle_rect)

# Function to move player
def move_player():
    global player_x
    global player_x_speed
    global slime_image
    if player_x <= 0:
        player_x = 0
        player_x_speed = 0
        if player_direction == 1:       
            player_x_speed = 20
            slime_image = pygame.transform.flip(slime_image, True, False)
            #player_x = right_wall_x + player_width  # Move to the right wall
    elif player_x >= right_wall_x + player_width:
        player_x = right_wall_x + player_width
        player_x_speed = 0
        if player_direction == -1:
            slime_image = pygame.transform.flip(slime_image, True, False)
            player_x_speed = -20
            #player_x = 0  # Move to the left wall

# Main game loop
def game_loop():
    
    global player_x, player_y, score, player_direction, obstacle_speed, obstacles
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(black)
        screen.blit(background_image, (0, 0))
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player_direction = -1  # Move left
                elif event.key == pygame.K_RIGHT:
                    player_direction = 1  # Move right
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player_direction = 0  # Stop moving

        # Generate new obstacles
        if random.randint(1, 100) <= 2:  # Roughly 2% chance per frame to generate an obstacle
            generate_obstacles()

        # Move obstacles
        for obstacle in obstacles[:]:
            obstacle.y += obstacle_speed
            if obstacle.y > screen_height:
                obstacles.remove(obstacle)
                score += 1  # Player scores when an obstacle is avoided

            # Check for collisions
            player_rect.x = player_x
            player_rect.y = player_y
            if player_rect.colliderect(obstacle):
                global player_lives
                 # Wait for a second after collision
                player_lives -= 1
                obstacles = []
                if player_lives == 0:
                    display_end()
                    pygame.display.flip()
                    pygame.time.wait(5000)
                    return  # End the game if there is a collision

            # Draw obstacles
            screen.blit(enemy_image, obstacle)
            #pygame.draw.rect(screen, red, obstacle)
        
        #take input from brain
        command = check_for_push()
        if command == "right":
            player_direction = 1
        elif command == "left":
            player_direction = -1
        # Move the player
        move_player()
        player_x += player_x_speed

        # Draw the player
        player_rect.x = player_x
        player_rect.y = player_y
        screen.blit(slime_image, player_rect)
        #pygame.draw.rect(screen, (0, 255, 0), player_rect)

        # Display the score
        display_score()

        
        # Speed up the game over time
        obstacle_speed = min(5, obstacle_speed + 0.000001)  # Increase speed gradually, max speed is 5

        # Refresh the screen
        pygame.display.flip()

        # Frame rate
        clock.tick(60)

# Run the game
game_loop()

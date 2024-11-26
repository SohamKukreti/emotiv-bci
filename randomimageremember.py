import pygame
import sys
import random
from multiprocessing import shared_memory
import struct

shm = shared_memory.SharedMemory(name="command_buffer")
def check_for_push():
    command_value = struct.unpack('I', shm.buf[:4])[0]
    if command_value == 1:  # 1 represents "push"
        shm.buf[:4] = struct.pack('I', 0)  # Reset to "no command"
        return True
    elif command_value == 2:
        shm.buf[:4] = struct.pack('I', 0)
        #print("drop received")
    return False

def check_for_push():
    command_value = struct.unpack('I', shm.buf[:4])[0]
    if command_value == 1:  # 1 represents "push"
        shm.buf[:4] = struct.pack('I', 0)  # Reset to "no command"
        print("push received")
        return True
    elif command_value == 2:
        shm.buf[:4] = struct.pack('I', 0)
        print("drop received")
    return False


# def check_for_push():
#     with open("python/command.txt", "r") as file:
#         command = file.read().strip()
#         print(command)
#         if command == "push":
#             with open("python/command.txt", "w") as file:  # Clear the command
#                 file.write("")
#             return True
#     return False

def load_image_from_url(url, size):
    """Load an image from a URL and scale it to the desired size."""
    image = pygame.image.load(url)
    return pygame.transform.scale(image, size)

def memory_game():
    # Initialize Pygame
    pygame.init()

    # Screen setup
    screen_width, screen_height = 1066, 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Memory Game")
    clock = pygame.time.Clock()

    # Colors
    black = (0, 0, 0)
    white = (255, 255, 255)
    green = (0, 255, 0)
    red = (255, 0, 0)

    # Load images from Picsum with new size
    image_urls = [f"images/image_{i}.jpg" for i in range(1, 100)]
    images = [load_image_from_url(url, (150, 150)) for url in random.sample(image_urls, 30)]

    # Game variables
    levels = 10
    current_level = 1
    score = 0
    font = pygame.font.Font(None, 50)
    timer_font = pygame.font.Font(None, 40)

    def display_message(text, color, y_offset=0):
        """Displays a message on the screen."""
        message = font.render(text, True, color)
        screen.blit(message, (screen_width // 2 - message.get_width() // 2, screen_height // 2 - message.get_height() // 2 + y_offset))

    while current_level <= levels:
        # Step 1: Display a random target image
        target_image = random.choice(images)
        screen.fill(black)
        display_message(f"Level {current_level}", white, -100)
        display_message("Memorize this image!", white, 100)
        screen.blit(target_image, (screen_width // 2 - target_image.get_width() // 2, screen_height // 2 - target_image.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(1000)  # Show the image for 3 seconds

        # Step 2: Decide whether target image is in the group (50% chance)
        target_present = random.choice([True, False])
        
        # Step 3: Display a group of random images
        num_images = 15
        group = random.sample(images, num_images)
        
        if target_present:
            # Replace a random image with the target
            group[random.randint(0, len(group) - 1)] = target_image
        else:
            for i in group:
                if i == target_image:
                    group.remove(i)

        screen.fill(black)
        grid_cols = 4
        start_x = (screen_width - (grid_cols * 160)) // 2
        start_y = 100

        for i, img in enumerate(group):
            x = start_x + (i % grid_cols) * 160
            y = start_y + (i // grid_cols) * 160
            screen.blit(img, (x, y))

        display_message("Is the original image here? Press Enter.", white, 250)
        pygame.display.flip()

        # Step 4: Wait for user input with a timer
        start_time = pygame.time.get_ticks()
        user_input = False
        time_limit = 5000  # 5 seconds
        while pygame.time.get_ticks() - start_time < time_limit:
            screen.fill(black)

            # Re-draw images and timer
            for i, img in enumerate(group):
                x = start_x + (i % grid_cols) * 160
                y = start_y + (i // grid_cols) * 160
                screen.blit(img, (x, y))

            # Display timer
            time_left = max(0, (time_limit - (pygame.time.get_ticks() - start_time)) // 1000)
            timer_text = timer_font.render(f"Time left: {time_left}s", True, white)
            screen.blit(timer_text, (10, 10))

            display_message("Is the original image here? Press Enter.", white, 370)
            pygame.display.flip()
            user_input = check_for_push()
            # Check for input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    user_input = True
                    break
            
            if user_input:
                break
        
        # Step 5: Check the result
        screen.fill(black)
        if (target_present and user_input) or (not target_present and not user_input):
            score += 1
            display_message("Correct!", green)
        else:
            display_message("Wrong!", red)
        display_message(f"Score: {score}", white, 100)
        pygame.display.flip()
        pygame.time.wait(2000)

        # Step 6: Advance to the next level
        current_level += 1

    # End of game
    screen.fill(black)
    display_message("Game Over!", white, -50)
    display_message(f"Final Score: {score}/{levels}", white, 50)
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    sys.exit()

# Run the game
memory_game()

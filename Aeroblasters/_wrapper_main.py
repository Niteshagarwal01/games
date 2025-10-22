
import os
import sys
import subprocess
import pygame

# Initialize pygame to capture key events
pygame.init()

# Set up a minimal display to capture key events
info = pygame.display.Info()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
pygame.display.set_caption("Aeroblasters - Press F10 to return to launcher")

# Function to show return message overlay
def show_return_message():
    screen = pygame.display.get_surface()
    font = pygame.font.SysFont('Arial', 18)
    text = font.render("Press F10 to return to launcher", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width()//2, 20))
    
    # Semi-transparent overlay
    overlay = pygame.Surface((screen.get_width(), 40))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    
    screen.blit(overlay, (0, 0))
    screen.blit(text, text_rect)
    pygame.display.update(pygame.Rect(0, 0, screen.get_width(), 40))

# Variables to track state
show_message_timer = 180  # Show message for 3 seconds (60fps)
message_shown = False

# Start the game process
game_process = subprocess.Popen([sys.executable, "main.py"])

# Main loop to check for F10 key press
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F10:  # F10 key to return to launcher
                running = False
            elif event.key == pygame.K_F1:  # F1 key to show help
                message_shown = True
                show_message_timer = 180
    
    # Check if process is still running
    if game_process.poll() is not None:
        running = False
    
    # Show return message on startup or when F1 is pressed
    if show_message_timer > 0:
        if not message_shown:
            show_return_message()
            message_shown = True
        show_message_timer -= 1
    
    clock.tick(60)

# Terminate the game process if it's still running
if game_process.poll() is None:
    game_process.terminate()

pygame.quit()

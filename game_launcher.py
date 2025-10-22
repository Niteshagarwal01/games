import os
import sys
import pygame
import importlib.util
import subprocess

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
TITLE = "Game Collection Launcher"
FPS = 60
GAMES_DIR = os.path.dirname(os.path.abspath(__file__))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
BLUE = (30, 144, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
GOLD = (255, 215, 0)

# Function to get the correct path for resources
def get_path(relative_path):
    return os.path.join(GAMES_DIR, relative_path)

# Load font
try:
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
except:
    font_large = pygame.font.SysFont('Arial', 48)
    font_medium = pygame.font.SysFont('Arial', 36)
    font_small = pygame.font.SysFont('Arial', 24)

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_GRAY, hover_color=WHITE, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=15)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=15)
        
        text_surf = font_medium.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
        
    def clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

# Game class to store information about each game
class Game:
    def __init__(self, name, directory, description=""):
        self.name = name
        self.directory = directory
        self.description = description
        self.image_path = os.path.join(directory, "app.png")
        if not os.path.exists(self.image_path):
            # Try other common screenshot filenames
            for alt_name in ["app.gif", "screenshot.png", "preview.png", "app.jpg"]:
                alt_path = os.path.join(directory, alt_name)
                if os.path.exists(alt_path):
                    self.image_path = alt_path
                    break
            else:
                self.image_path = None
        
        self.main_file = os.path.join(directory, "main.py")
        if not os.path.exists(self.main_file):
            for alt_name in ["game.py", "run.py"]:
                alt_path = os.path.join(directory, alt_name)
                if os.path.exists(alt_path):
                    self.main_file = alt_path
                    break
        
        # Load icon/preview image if available
        self.image = None
        if self.image_path and os.path.exists(self.image_path):
            try:
                self.image = pygame.image.load(self.image_path)
                # Standardize thumbnail size
                self.image = pygame.transform.scale(self.image, (200, 150))
            except Exception as e:
                print(f"Error loading image for {name}: {e}")
                self.image = None

# Find all games in the directory
def find_games():
    games = []
    # List all directories in the Games folder
    for item in os.listdir(GAMES_DIR):
        item_path = os.path.join(GAMES_DIR, item)
        # Check if it's a directory and has a main.py or game.py file
        if os.path.isdir(item_path) and item != "__pycache__":
            main_py = os.path.join(item_path, "main.py")
            game_py = os.path.join(item_path, "game.py")
            if os.path.exists(main_py) or os.path.exists(game_py):
                # Read README.md for description if available
                description = ""
                readme_path = os.path.join(item_path, "README.md")
                if os.path.exists(readme_path):
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            if lines:
                                description = lines[0].strip()
                    except:
                        pass
                
                games.append(Game(item, item_path, description))
    
    # Sort games alphabetically
    games.sort(key=lambda g: g.name)
    return games

# Create a wrapper for launching games with a back button
def create_game_wrapper(game_path, game_name):
    wrapper_code = f"""
import os
import sys
import subprocess
import pygame

# Initialize pygame to capture key events
pygame.init()

# Set up a minimal display to capture key events
info = pygame.display.Info()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
pygame.display.set_caption("{game_name} - Press F10 to return to launcher")

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
game_process = subprocess.Popen([sys.executable, "{os.path.basename(game_path)}"])

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
"""
    
    # Get the wrapper path
    wrapper_dir = os.path.dirname(game_path)
    wrapper_name = f"_wrapper_{os.path.basename(game_path)}"
    wrapper_path = os.path.join(wrapper_dir, wrapper_name)
    
    # Write the wrapper script
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_code)
    
    return wrapper_path

# Launch a game with back button functionality
def launch_game(game, screen):
    # Save the current directory
    original_dir = os.getcwd()
    
    try:
        # Change to the game's directory
        os.chdir(game.directory)
        
        # Create a wrapper script for the game
        game_file = os.path.basename(game.main_file)
        wrapper_path = create_game_wrapper(game_file, game.name)
        
        # Display a message about the back button
        back_msg = f"Press F10 to return to launcher while playing {game.name}"
        print(back_msg)
        
        # Run the wrapper as a subprocess
        process = subprocess.Popen([sys.executable, os.path.basename(wrapper_path)])
        
        # Wait for the wrapper to finish
        process.wait()
        
        # Clean up the wrapper file
        try:
            os.remove(wrapper_path)
        except:
            pass
        
    except Exception as e:
        print(f"Error launching {game.name}: {e}")
        
    finally:
        # Restore the original directory
        os.chdir(original_dir)
        
        # Re-initialize pygame after the game exits
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        return screen

# Draw a fancy title
def draw_title(screen, text, y_pos):
    shadow_offset = 2
    
    # Draw shadow
    title_shadow = font_large.render(text, True, BLACK)
    shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + shadow_offset, y_pos + shadow_offset))
    screen.blit(title_shadow, shadow_rect)
    
    # Draw main text
    title_text = font_large.render(text, True, WHITE)
    text_rect = title_text.get_rect(center=(WIDTH // 2, y_pos))
    screen.blit(title_text, text_rect)

# Main function
def main():
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Game Collection Launcher")
    parser.add_argument("--launch", help="Launch a specific game directly")
    args = parser.parse_args()
    
    # Create window inside the main function to avoid scope issues
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    
    # Try to set window icon
    try:
        icon = pygame.image.load(get_path("game_launcher_icon.png"))
        pygame.display.set_icon(icon)
    except:
        pass
    
    # If launch argument is provided, directly launch that game
    if args.launch:
        games = find_games()
        for game in games:
            if game.name.lower() == args.launch.lower():
                print(f"Directly launching {game.name}...")
                launch_game(game, screen)
                break
        else:
            print(f"Game '{args.launch}' not found.")
    
    running = True
    games = find_games()
    page = 0
    games_per_page = 4
    max_pages = (len(games) - 1) // games_per_page + 1
    
    # Create navigation buttons
    back_button = Button(50, HEIGHT - 70, 100, 40, "Back", BLUE, LIGHT_GRAY)
    next_button = Button(WIDTH - 150, HEIGHT - 70, 100, 40, "Next", BLUE, LIGHT_GRAY)
    exit_button = Button(WIDTH // 2 - 50, HEIGHT - 70, 100, 40, "Exit", RED, LIGHT_GRAY)
    
    # Create game buttons
    game_buttons = []
    for i in range(min(games_per_page, len(games))):
        x = WIDTH // 2 - 200
        y = 150 + i * 100
        game_buttons.append(Button(x, y, 350, 80, ""))
    
    selected_game = None
    
    while running:
        screen.fill(GRAY)
        
        # Draw background gradient
        for y in range(HEIGHT):
            # Create a gradient from dark gray to light gray
            color_value = 80 + int(y / HEIGHT * 40)  
            pygame.draw.line(screen, (color_value, color_value, color_value), (0, y), (WIDTH, y))
        
        # Handle events
        click = False
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if selected_game:
                        selected_game = None
                    else:
                        running = False
                elif event.key == pygame.K_LEFT and page > 0:
                    page -= 1
                elif event.key == pygame.K_RIGHT and page < max_pages - 1:
                    page += 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        
        if selected_game:
            # Display game details screen
            pygame.draw.rect(screen, LIGHT_GRAY, (50, 100, WIDTH - 100, HEIGHT - 200), border_radius=15)
            pygame.draw.rect(screen, BLACK, (50, 100, WIDTH - 100, HEIGHT - 200), 2, border_radius=15)
            
            # Game title
            title_text = font_large.render(selected_game.name, True, BLACK)
            title_rect = title_text.get_rect(center=(WIDTH // 2, 130))
            screen.blit(title_text, title_rect)
            
            # Game image with border
            if selected_game.image:
                # Draw border
                img_border = pygame.Rect(WIDTH // 2 - 110, 170, 220, 170)
                pygame.draw.rect(screen, BLUE, img_border, border_radius=10)
                
                # Draw image
                img_rect = selected_game.image.get_rect(center=(WIDTH // 2, 255))
                screen.blit(selected_game.image, img_rect)
            else:
                # Draw placeholder if no image
                placeholder_rect = pygame.Rect(WIDTH // 2 - 100, 180, 200, 150)
                pygame.draw.rect(screen, WHITE, placeholder_rect)
                pygame.draw.rect(screen, BLACK, placeholder_rect, 1)
                
                no_img_text = font_small.render("No Preview Available", True, BLACK)
                no_img_rect = no_img_text.get_rect(center=placeholder_rect.center)
                screen.blit(no_img_text, no_img_rect)
            
            # Description
            if selected_game.description:
                desc_text = font_small.render(selected_game.description[:80], True, BLACK)
                desc_rect = desc_text.get_rect(center=(WIDTH // 2, 370))
                screen.blit(desc_text, desc_rect)
                
                if len(selected_game.description) > 80:
                    desc_text2 = font_small.render(selected_game.description[80:160], True, BLACK)
                    desc_rect2 = desc_text2.get_rect(center=(WIDTH // 2, 400))
                    screen.blit(desc_text2, desc_rect2)
            
            # Play and Back buttons
            play_btn = Button(WIDTH // 2 - 150, HEIGHT - 150, 120, 50, "Play", GREEN)
            back_btn = Button(WIDTH // 2 + 30, HEIGHT - 150, 120, 50, "Back", RED)
            
            play_btn.check_hover((mx, my))
            back_btn.check_hover((mx, my))
            play_btn.draw(screen)
            back_btn.draw(screen)
            
            if play_btn.clicked((mx, my), click):
                # Launch the game
                pygame.display.quit()
                screen = launch_game(selected_game, screen)
                # Screen is re-initialized in the launch_game function
            
            if back_btn.clicked((mx, my), click):
                selected_game = None
                
        else:
            # Draw title with drop shadow
            draw_title(screen, "Game Collection", 50)
            
            # Instructions
            text_surf = font_medium.render("Select a game to play", True, WHITE)
            text_rect = text_surf.get_rect(center=(WIDTH // 2, 100))
            screen.blit(text_surf, text_rect)
            
            # Page indicator
            max_pages = (len(games) - 1) // games_per_page + 1
            page_text = font_small.render(f"Page {page + 1}/{max_pages}", True, WHITE)
            screen.blit(page_text, (WIDTH // 2 - 40, HEIGHT - 30))
            
            # Draw game buttons for current page
            start_idx = page * games_per_page
            end_idx = min(start_idx + games_per_page, len(games))
            
            # Make sure we have enough buttons
            while len(game_buttons) < end_idx - start_idx:
                i = len(game_buttons)
                x = WIDTH // 2 - 200
                y = 150 + (i % games_per_page) * 100
                game_buttons.append(Button(x, y, 350, 80, ""))
            
            for i in range(start_idx, end_idx):
                btn_idx = i % games_per_page
                game = games[i]
                
                # Create and draw button
                btn = game_buttons[btn_idx]
                btn.text = game.name
                btn.check_hover((mx, my))
                btn.draw(screen)
                
                # Show thumbnail if available
                if game.image:
                    # Draw image border
                    border_rect = pygame.Rect(btn.rect.x + btn.rect.width + 10, btn.rect.y - 5, 210, 160)
                    border_color = GOLD if btn.hovered else BLUE
                    pygame.draw.rect(screen, border_color, border_rect, 2, border_radius=10)
                    
                    # Draw image
                    thumb_x = btn.rect.x + btn.rect.width + 15
                    thumb_y = btn.rect.y
                    screen.blit(game.image, (thumb_x, thumb_y))
                
                # Handle click
                if btn.clicked((mx, my), click):
                    selected_game = game
            
            # Navigation buttons
            back_button.check_hover((mx, my))
            next_button.check_hover((mx, my))
            exit_button.check_hover((mx, my))
            
            if page > 0:
                back_button.draw(screen)
                if back_button.clicked((mx, my), click):
                    page -= 1
            
            if (page + 1) * games_per_page < len(games):
                next_button.draw(screen)
                if next_button.clicked((mx, my), click):
                    page += 1
            
            exit_button.draw(screen)
            if exit_button.clicked((mx, my), click):
                running = False
        
        # Draw a decorative border around the screen    
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, HEIGHT), 3, border_radius=4)
                
        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
# filepath: c:\Users\offic\OneDrive\Documents\Games\FRONTEND\server.py
import http.server
import socketserver
import os
import json
import shutil
import sys
import subprocess
import time
import threading
from pathlib import Path

from matplotlib.pylab import var

# Configuration
PORT = 8000
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
GAMES_DIR = os.path.dirname(FRONTEND_DIR)
PYGBAG_DIR = os.path.join(FRONTEND_DIR, "pygbag_builds")

# Create assets directory structure if it doesn't exist
def setup_asset_directories():
    # Create game-assets subdirectories for each game
    game_dirs = [d for d in os.listdir(GAMES_DIR) if os.path.isdir(os.path.join(GAMES_DIR, d)) and d != "FRONTEND" and d != "__pycache__"]
    
    for game_dir in game_dirs:
        # Clean game name for URL/directory purposes
        clean_name = game_dir.replace(" ", "-")
        asset_dir = os.path.join(FRONTEND_DIR, "game-assets", clean_name)
        
        # Create the asset directory if it doesn't exist
        if not os.path.exists(asset_dir):
            os.makedirs(asset_dir)
        
        # Copy app image if it exists
        source_app_img = None
        for img_name in ["app.png", "app.gif", "screenshot.png", "preview.png"]:
            img_path = os.path.join(GAMES_DIR, game_dir, img_name)
            if os.path.exists(img_path):
                source_app_img = img_path
                break
        
        if source_app_img:
            # Copy the app image to the asset directory
            dest_path = os.path.join(asset_dir, os.path.basename(source_app_img))
            if not os.path.exists(dest_path):
                shutil.copy2(source_app_img, dest_path)

    # Create pygbag builds directory if it doesn't exist
    if not os.path.exists(PYGBAG_DIR):
        os.makedirs(PYGBAG_DIR)

# Create a player HTML file for each game
def create_game_players():
    template_path = os.path.join(FRONTEND_DIR, "game-players", "template.html")
    
    if not os.path.exists(template_path):
        print(f"Error: Template file not found at {template_path}")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    game_dirs = [d for d in os.listdir(GAMES_DIR) if os.path.isdir(os.path.join(GAMES_DIR, d)) and d != "FRONTEND" and d != "__pycache__"]
    
    for game_dir in game_dirs:
        # Clean game name for URL/directory purposes
        clean_name = game_dir.lower().replace(" ", "-")
        player_path = os.path.join(FRONTEND_DIR, "game-players", f"{clean_name}.html")
        
        # Read game description if available
        description = ""
        readme_path = os.path.join(GAMES_DIR, game_dir, "README.md")
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        description = lines[0].strip()
            except Exception as e:
                print(f"Warning: Could not read README for {game_dir}: {e}")
        
        # Create customized player file
        game_config = {
            'title': game_dir,
            'description': description,
            'gameUrl': f"/game_launcher?game={clean_name}",
            'homeUrl': "/"
        }
        
        # Replace game config in template
        new_content = template.replace(
            'const gameConfig = {\n            title: "Game Title",\n            gameUrl: "../path/to/game-runner.html",\n            homeUrl: "../index.html"\n        };',
            f'const gameConfig = {{\n            title: "{game_dir}",\n            gameUrl: "/game_launcher?game={clean_name}",\n            homeUrl: "/"\n        }};'
        )
        
        # Write the customized player file
        with open(player_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

# Generate the games-data.js file with actual game data
def generate_games_data():
    games_data = []
    game_dirs = [d for d in os.listdir(GAMES_DIR) if os.path.isdir(os.path.join(GAMES_DIR, d)) and d != "FRONTEND" and d != "__pycache__"]
    
    for game_dir in game_dirs:
        # Skip directories without main.py or game.py
        main_py = os.path.join(GAMES_DIR, game_dir, "main.py")
        game_py = os.path.join(GAMES_DIR, game_dir, "game.py")
        if not (os.path.exists(main_py) or os.path.exists(game_py)):
            continue
            
        # Clean name for URL/directory purposes
        clean_name = game_dir.lower().replace(" ", "-")
        
        # Get description from README
        description = ""
        readme_path = os.path.join(GAMES_DIR, game_dir, "README.md")
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        description = lines[0].strip()
            except Exception as e:
                print(f"Warning: Could not read README for {game_dir}: {e}")
        
        # Find thumbnail
        thumbnail = None
        for img_name in ["app.png", "app.gif", "screenshot.png", "preview.png"]:
            img_path = f"game-assets/{clean_name}/{img_name}"
            full_path = os.path.join(FRONTEND_DIR, img_path)
            if os.path.exists(full_path):
                thumbnail = img_path
                break
        
        game_data = {
            'id': clean_name,
            'title': game_dir,
            'description': description or f"Play {game_dir} right in your browser!",
            'thumbnail': thumbnail,
            'playUrl': f"game-players/{clean_name}.html",
            'screenshots': [thumbnail] if thumbnail else [],
            'webReady': False  # Will be updated after pygbag builds
        }
        
        # Check if the game is web-ready
        build_dir = os.path.join(PYGBAG_DIR, clean_name)
        index_file = os.path.join(build_dir, "index.html")
        game_data['webReady'] = os.path.exists(index_file)
        
        games_data.append(game_data)
    
    # Write the games data to the games-data.js file
    with open(os.path.join(FRONTEND_DIR, "games-data.js"), 'w', encoding='utf-8') as f:
        f.write("// Game collection data\nconst games = ")
        f.write(json.dumps(games_data, indent=4))
        f.write(";")

# Custom request handler that serves the frontend and launches games
class GameHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to the frontend directory
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def end_headers(self):
        # Add CORS headers to all responses for proper functioning of WebAssembly
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
        # Add additional headers for WebAssembly
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        # Handle OPTIONS requests for CORS preflight
        if self.command == 'OPTIONS':
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            return

        # Handle launch-game endpoint - actually launches the game if on the same machine
        if self.path.startswith('/launch-game'):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            
            if 'game' in query:
                game_name = query['game'][0]
                
                # Find the actual game directory
                actual_game_dir = None
                for d in os.listdir(GAMES_DIR):
                    if d.lower().replace(" ", "-") == game_name and os.path.isdir(os.path.join(GAMES_DIR, d)):
                        actual_game_dir = d
                        break
                
                if actual_game_dir:
                    # Launch the game directly 
                    try:
                        # Run the game launcher with the specific game
                        subprocess.Popen([sys.executable, os.path.join(GAMES_DIR, "game_launcher.py"), "--launch", actual_game_dir])
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(f"<html><body><script>window.location.href='/game-launched?game={game_name}';</script></body></html>".encode())
                    except Exception as e:
                        self.serve_error_page(f"Error launching game: {e}")
                    return
                else:
                    self.serve_error_page(f"Game not found: {game_name}")
                    return

        # Handle game-launched endpoint - shows a success page
        if self.path.startswith('/game-launched'):
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            
            if 'game' in query:
                game_name = query['game'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Game Launched</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #2c3e50;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            padding: 20px;
            text-align: center;
        }}
        .container {{
            background-color: rgba(0,0,0,0.3);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 600px;
        }}
        h1 {{
            color: #2ecc71;
        }}
        p {{
            font-size: 1.2rem;
            line-height: 1.6;
            margin: 20px 0;
        }}
        .reminder {{
            background-color: rgba(52, 152, 219, 0.2);
            border-left: 4px solid #3498db;
            padding: 10px 15px;
            margin: 20px 0;
            text-align: left;
            border-radius: 0 5px 5px 0;
        }}
        button {{
            background-color: #3498db;
            color: white;
            border: none;
            padding: 12px 25px;
            font-size: 1.1rem;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 20px;
        }}
        .keyboard {{
            display: inline-block;
            background-color: #34495e;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: Consolas, monospace;
            margin: 0 2px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Game Launched!</h1>
        <p>The game is now running in a separate window.</p>
        <div class="reminder">
            <p><strong>Remember:</strong> Press <span class="keyboard">F10</span> to return to the game launcher when you're done playing.</p>
        </div>
        <button onclick="window.location.href='/'">Return to Game Collection</button>
    </div>
</body>
</html>"""
                self.wfile.write(html.encode())
                return

        # Handle game launcher requests
        if self.path.startswith('/game_launcher'):
            # Parse query parameters
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            
            if 'game' in query:
                game_name = query['game'][0]
                
                # Find the actual game directory
                actual_game_dir = None
                for d in os.listdir(GAMES_DIR):
                    if d.lower().replace(" ", "-") == game_name and os.path.isdir(os.path.join(GAMES_DIR, d)):
                        actual_game_dir = d
                        break
                
                if actual_game_dir:
                    # Use the direct HTML approach instead of trying to build with Pygbag
                    # This is more reliable across different systems
                    self.serve_direct_game_page(game_name, actual_game_dir)
                    return
                else:
                    self.serve_error_page(f"Game not found: {game_name}")
                    return
        
        # Handle play-desktop-game requests - provides instructions for playing locally
        if self.path.startswith('/play-desktop-game'):
            # Parse query parameters
            from urllib.parse import urlparse, parse_qs
            query = parse_qs(urlparse(self.path).query)
            
            if 'game' in query:
                game_name = query['game'][0]
                
                # Find the actual game directory
                actual_game_dir = None
                for d in os.listdir(GAMES_DIR):
                    if d.lower().replace(" ", "-") == game_name and os.path.isdir(os.path.join(GAMES_DIR, d)):
                        actual_game_dir = d
                        break
                
                if actual_game_dir:
                    self.serve_play_instructions(actual_game_dir, game_name)
                    return
                else:
                    self.serve_error_page(f"Game not found: {game_name}")
                    return
        
        # For all other requests, let SimpleHTTPRequestHandler handle it
        super().do_GET()

    def serve_direct_game_page(self, game_name, actual_game_dir):
        """Serves a direct HTML page with game info and screenshots"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        game_path = os.path.join(GAMES_DIR, actual_game_dir)
        
        # Find an image to display
        image_path = None
        for img_name in ["app.png", "app.gif", "screenshot.png", "preview.png"]:
            img_path = os.path.join(game_path, img_name)
            if os.path.exists(img_path):
                image_path = img_path
                break
        
        # Get game description
        description = ""
        readme_path = os.path.join(game_path, "README.md")
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        description = lines[0].strip()
                        # Get more description if available
                        if len(lines) > 1:
                            description += "<br><br>" + lines[1].strip()
            except Exception as e:
                print(f"Warning: Could not read README for {actual_game_dir}: {e}")
        
        # Create the HTML page
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{actual_game_dir} - Game Info</title>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(to bottom, #2c3e50, #1a2533);
            color: white;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            text-align: center;
            padding: 20px 0;
            margin-bottom: 30px;
            border-bottom: 2px solid #3498db;
        }}
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            color: #3498db;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .game-info {{
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            margin-bottom: 40px;
        }}
        .game-image {{
            flex: 1;
            min-width: 300px;
            text-align: center;
        }}
        .game-image img {{
            max-width: 100%;
            max-height: 400px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            border: 3px solid #3498db;
        }}
        .game-details {{
            flex: 1;
            min-width: 300px;
        }}
        .description {{
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 30px;
            background-color: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 10px;
        }}
        .buttons {{
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }}
        button {{
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.1rem;
            cursor: pointer;
            transition: transform 0.2s, background-color 0.3s;
        }}
        .play-button {{
            background-color: #2ecc71;
            color: white;
            flex: 2;
        }}
        .play-button:hover {{
            background-color: #27ae60;
            transform: scale(1.05);
        }}
        .back-button {{
            background-color: #e74c3c;
            color: white;
            flex: 1;
        }}
        .back-button:hover {{
            background-color: #c0392b;
        }}
        .info-section {{
            margin-top: 40px;
            padding: 20px;
            background-color: rgba(0,0,0,0.2);
            border-radius: 10px;
        }}
        .info-section h2 {{
            color: #3498db;
            margin-top: 0;
        }}
        footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #bbb;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{actual_game_dir}</h1>
        </header>
        
        <div class="game-info">
"""

        # Add image if available
        if image_path:
            # Get relative path for the image
            rel_image_path = os.path.join("/game-assets", game_name, os.path.basename(image_path))
            html += f"""
            <div class="game-image">
                <img src="{rel_image_path}" alt="{actual_game_dir} screenshot">
            </div>
"""

        html += f"""
            <div class="game-details">
                <div class="description">
                    <p>{description if description else f"Welcome to {actual_game_dir}! This exciting game is part of your game collection."}</p>
                </div>
                
                <div class="buttons">
                    <button class="play-button" onclick="window.location.href='/play-desktop-game?game={game_name}'">Play Local Game</button>
                    <button class="back-button" onclick="window.location.href='/'">Back to Games</button>
                </div>
            </div>
        </div>
        
        <div class="info-section">
            <h2>About This Game</h2>
            <p>This game has been created using Python and Pygame. To play this game:</p>
            <ul>
                <li>Click "Play Local Game" to launch the game through your desktop game launcher</li>
                <li>To return to the game collection after playing, press F10 while in the game</li>
            </ul>
            
            <p>Browser-based play with WebAssembly is still experimental and may not work correctly for all games. 
            For the best experience, we recommend playing through the desktop game launcher.</p>
        </div>
        
        <footer>
            &copy; 2025 Game Collection. All rights reserved.
        </footer>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
        var playButton = document.querySelector('.play-button');
        if (playButton) {{
            playButton.addEventListener('click', function(e) {{
                // Just let the button work normally - no alert
                // The href in the button will take us to the play instructions page
            }});
        }}
    }});
    </script>
</body>
</html>
"""
        
        self.wfile.write(html.encode())

    def serve_error_page(self, message):
        """Creates an error page"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Error</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #2c3e50;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            background-color: rgba(0,0,0,0.3);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
        }}
        h1 {{
            color: #e74c3c;
        }}
        button {{
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Error</h1>
        <p>{message}</p>
        <button onclick="window.history.back()">Go Back</button>
    </div>
</body>
</html>"""
        self.wfile.write(html.encode())

    def serve_play_instructions(self, actual_game_dir, game_name):
        """Serves instructions for playing the game locally with a direct launch option"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Play {actual_game_dir}</title>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(to bottom, #2c3e50, #1a2533);
            color: white;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 30px;
            text-align: center;
        }}
        h1 {{
            font-size: 2.2rem;
            color: #3498db;
            margin-bottom: 20px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .play-box {{
            background-color: rgba(0,0,0,0.3);
            border-radius: 15px;
            padding: 30px;
            margin: 30px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .direct-launch {{
            background-color: rgba(46, 204, 113, 0.2);
            border: 2px solid #2ecc71;
            border-radius: 15px;
            padding: 20px;
            margin: 20px auto;
            max-width: 400px;
            text-align: center;
        }}
        .direct-launch h2 {{
            color: #2ecc71;
            margin-top: 0;
        }}
        .play-now-btn {{
            background-color: #2ecc71;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.3rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
            display: inline-block;
            margin: 15px 0;
            text-decoration: none;
        }}
        .play-now-btn:hover {{
            background-color: #27ae60;
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }}
        .instruction-steps {{
            text-align: left;
            max-width: 600px;
            margin: 40px auto;
        }}
        .instruction-title {{
            color: #3498db;
            font-size: 1.5rem;
            border-bottom: 1px solid #3498db;
            padding-bottom: 10px;
            margin: 30px 0 20px;
        }}
        .step {{
            margin: 25px 0;
            display: flex;
            align-items: flex-start;
        }}
        .step-number {{
            background-color: #2ecc71;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            flex-shrink: 0;
            font-weight: bold;
        }}
        .step-content {{
            flex: 1;
        }}
        .step-title {{
            font-size: 1.2rem;
            color: #3498db;
            margin-bottom: 5px;
        }}
        .code-block {{
            background-color: rgba(0,0,0,0.4);
            padding: 12px;
            border-radius: 5px;
            font-family: Consolas, monospace;
            margin: 10px 0;
            white-space: nowrap;
            overflow-x: auto;
        }}
        .note {{
            background-color: rgba(52, 152, 219, 0.2);
            border-left: 4px solid #3498db;
            padding: 10px 15px;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }}
        .note-title {{
            color: #3498db;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        button, .btn {{
            background-color: #3498db;
            color: white;
            border: none;
            padding: 12px 25px;
            font-size: 1.1rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: background-color 0.3s;
            margin-top: 20px;
            display: inline-block;
            text-decoration: none;
        }}
        button:hover, .btn:hover {{
            background-color: #2980b9;
        }}
        .keyboard {{
            display: inline-block;
            background-color: #34495e;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: Consolas, monospace;
            margin: 0 2px;
            border: 1px solid #7f8c8d;
        }}
        .or-divider {{
            display: flex;
            align-items: center;
            margin: 30px 0;
            color: #7f8c8d;
        }}
        .or-divider:before, .or-divider:after {{
            content: "";
            flex: 1;
            height: 1px;
            background-color: #7f8c8d;
            margin: 0 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Play {actual_game_dir}</h1>
        
        <div class="play-box">
            <div class="direct-launch">
                <h2>Quick Play</h2>
                <p>Launch the game directly from your browser:</p>
                <a href="/launch-game?game={game_name}" class="play-now-btn">PLAY NOW</a>
                <p><small>This will open the game in a separate window</small></p>
            </div>
            
            <div class="or-divider">OR</div>
            
            <div class="instruction-title">Manual Launch Instructions</div>
            <div class="instruction-steps">
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <div class="step-title">Launch the Game Collection</div>
                        <p>Open your Game Collection Launcher by running the game_launcher.py file:</p>
                        <div class="code-block">python "c:\\Users\\offic\\OneDrive\\Documents\\Games\\game_launcher.py"</div>
                    </div>
                </div>
                
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <div class="step-title">Find and Select {actual_game_dir}</div>
                        <p>Browse through the available games in the launcher.</p>
                    </div>
                </div>
                
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <div class="step-title">Launch the Game</div>
                        <p>Click the "Play" button to start the game.</p>
                    </div>
                </div>
                
                <div class="step">
                    <div class="step-number">4</div>
                    <div class="step-content">
                        <div class="step-title">Return to Launcher</div>
                        <p>When you want to exit the game and return to the launcher, press <span class="keyboard">F10</span> at any time.</p>
                    </div>
                </div>
                
                <div class="note">
                    <div class="note-title">Note:</div>
                    <p>The game launcher uses Python and Pygame. Make sure you have Python and Pygame properly installed on your system.</p>
                </div>
            </div>
            
            <a href="/" class="btn">Back to Game Collection</a>
        </div>
    </div>

    <script>
        // Track if a game was launched
        let gameLaunched = false;
        
        // Check if direct launch button was clicked
        document.querySelector('.play-now-btn').addEventListener('click', function() {{
            gameLaunched = true;
        }});
        
        // Warn user if they try to navigate away while a game might be running
        window.addEventListener('beforeunload', function(e) {{
            if (gameLaunched) {{
                // This message might not show in all browsers due to security features
                e.preventDefault();
                e.returnValue = 'A game may be running. Are you sure you want to leave?';
                return e.returnValue;
            }}
        }});
    </script>
</body>
</html>"""
        self.wfile.write(html.encode())

def main():
    # Create necessary directories and files
    setup_asset_directories()
    create_game_players()
    
    # Prepare games data
    generate_games_data()
    
    # Start the server
    handler = GameHandler
    
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"Server started at http://localhost:{PORT}")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
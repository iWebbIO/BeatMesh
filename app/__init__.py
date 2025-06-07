from flask import Flask
from flask_socketio import SocketIO
import os

# Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    
    # Ensure the music directory exists
    music_dir = os.path.join(os.path.dirname(__file__), 'static', 'music')
    os.makedirs(music_dir, exist_ok=True)
    
    # Initialize SocketIO with the app
    socketio.init_app(app)
    
    # Import and register routes
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    return app

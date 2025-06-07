import os

MUSIC_DIR = os.path.join(os.path.dirname(__file__), 'static', 'music')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'm4a'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file_size):
    """Check if file size is within limits"""
    return file_size <= MAX_FILE_SIZE

def get_file_info(filename):
    """Get file information including size"""
    file_path = get_file_path(filename)
    if os.path.exists(file_path):
        stat = os.stat(file_path)
        return {
            'name': filename,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'modified': stat.st_mtime
        }
    return None

def get_music_files():
    """Get list of music files from the music directory"""
    try:
        if not os.path.exists(MUSIC_DIR):
            os.makedirs(MUSIC_DIR)
        files = os.listdir(MUSIC_DIR)
        # Filter only allowed files
        return [f for f in files if allowed_file(f)]
    except Exception as e:
        print(f"Error getting music files: {str(e)}")
        return []

def get_file_path(filename):
    """Get the full path of a music file"""
    return os.path.join(MUSIC_DIR, filename)

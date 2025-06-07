from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
import time
import uuid
from werkzeug.utils import secure_filename
from app.audio import get_music_files, allowed_file, validate_file_size, MAX_FILE_SIZE
from flask_socketio import emit, join_room, leave_room, rooms
from app import socketio

main_bp = Blueprint('main', __name__)

# Global state management
room_states = {}
connected_users = {}

def get_room_state(room_id):
    """Get or create room state"""
    if room_id not in room_states:
        room_states[room_id] = {
            'current_track': None,
            'is_playing': False,
            'current_time': 0,
            'last_update': time.time(),
            'volume': 1.0,
            'playlist': [],
            'users': {}
        }
    return room_states[room_id]

def update_room_state(room_id, **kwargs):
    """Update room state with timestamp"""
    state = get_room_state(room_id)
    state.update(kwargs)
    state['last_update'] = time.time()
    return state

@main_bp.route('/')
def index():
    music_files = get_music_files()
    return render_template('index.html', music_files=music_files)

@main_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
    
    # Check file extension
    if not allowed_file(file.filename):
        return {'error': 'Invalid file type. Allowed: mp3, wav, ogg, flac, m4a'}, 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if not validate_file_size(file_size):
        return {'error': f'File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB'}, 400
    
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join('app', 'static', 'music', filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        file.save(file_path)
        
        return {
            'message': 'File uploaded successfully', 
            'filename': filename,
            'size_mb': round(file_size / (1024 * 1024), 2)
        }, 200
        
    except Exception as e:
        return {'error': f'Upload failed: {str(e)}'}, 500

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    user_id = str(uuid.uuid4())
    session['user_id'] = user_id
    room_id = 'default'  # For now, use default room. Can be enhanced later with URL parameters
    session['room_id'] = room_id
    
    join_room(room_id)
    
    # Add user to connected users
    connected_users[user_id] = {
        'id': user_id,
        'room': room_id,
        'connected_at': time.time()
    }
    
    # Add user to room state
    room_state = get_room_state(room_id)
    room_state['users'][user_id] = connected_users[user_id]
    
    print(f'Client {user_id} connected to room {room_id}')
    
    try:
        # Send current room state to new client
        emit('sync', {
            'status': 'connected',
            'user_id': user_id,
            'room_id': room_id,
            'room_state': room_state,
            'server_time': time.time()
        })
        
        # Notify other users in the room
        emit('user_joined', {
            'user_id': user_id,
            'users_count': len(room_state['users'])
        }, room=room_id, include_self=False)
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    room_id = session.get('room_id')
    
    if user_id and room_id:
        # Remove user from connected users
        if user_id in connected_users:
            del connected_users[user_id]
        
        # Remove user from room state
        room_state = get_room_state(room_id)
        if user_id in room_state['users']:
            del room_state['users'][user_id]
        
        # Notify other users in the room
        emit('user_left', {
            'user_id': user_id,
            'users_count': len(room_state['users'])
        }, room=room_id)
        
        leave_room(room_id)
        print(f'Client {user_id} disconnected from room {room_id}')

@socketio.on('play')
def handle_play(data):
    try:
        room_id = session.get('room_id', 'default')
        user_id = session.get('user_id')
        
        # Update room state
        room_state = update_room_state(room_id, 
            is_playing=True,
            current_time=data.get('currentTime', 0),
            current_track=data.get('filename')
        )
        
        # Add server timestamp for better sync
        sync_data = {
            **data,
            'server_time': time.time(),
            'room_state': room_state
        }
        
        # Broadcast to room
        emit('play', sync_data, room=room_id)
        print(f'User {user_id} started playback in room {room_id}')
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('pause')
def handle_pause(data):
    try:
        room_id = session.get('room_id', 'default')
        user_id = session.get('user_id')
        
        # Update room state
        room_state = update_room_state(room_id,
            is_playing=False,
            current_time=data.get('currentTime', 0)
        )
        
        sync_data = {
            **data,
            'server_time': time.time(),
            'room_state': room_state
        }
        
        emit('pause', sync_data, room=room_id)
        print(f'User {user_id} paused playback in room {room_id}')
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('load_track')
def handle_load_track(data):
    try:
        room_id = session.get('room_id', 'default')
        user_id = session.get('user_id')
        
        # Update room state
        room_state = update_room_state(room_id,
            current_track=data.get('filename'),
            current_time=0,
            is_playing=False
        )
        
        sync_data = {
            **data,
            'server_time': time.time(),
            'room_state': room_state
        }
        
        emit('load_track', sync_data, room=room_id)
        print(f'User {user_id} loaded track {data.get("filename")} in room {room_id}')
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('volume_change')
def handle_volume_change(data):
    try:
        room_id = session.get('room_id', 'default')
        user_id = session.get('user_id')
        
        # Update room state
        room_state = update_room_state(room_id, volume=data.get('volume', 1.0))
        
        sync_data = {
            **data,
            'server_time': time.time(),
            'room_state': room_state
        }
        
        emit('volume_change', sync_data, room=room_id, include_self=False)
        print(f'User {user_id} changed volume to {data.get("volume")} in room {room_id}')
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('sync_request')
def handle_sync_request(data):
    try:
        room_id = session.get('room_id', 'default')
        room_state = get_room_state(room_id)
        
        emit('sync', {
            'room_state': room_state,
            'server_time': time.time()
        })
        
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('seek')
def handle_seek(data):
    try:
        room_id = session.get('room_id', 'default')
        user_id = session.get('user_id')
        
        # Update room state
        room_state = update_room_state(room_id, current_time=data.get('currentTime', 0))
        
        sync_data = {
            **data,
            'server_time': time.time(),
            'room_state': room_state
        }
        
        emit('seek', sync_data, room=room_id)
        print(f'User {user_id} seeked to {data.get("currentTime")} in room {room_id}')
        
    except Exception as e:
        emit('error', {'message': str(e)})

@main_bp.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_message="404 Not Found"), 404

@main_bp.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_message="500 Internal Server Error"), 500

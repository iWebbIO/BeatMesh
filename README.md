# BeatMesh

BeatMesh is a real-time synchronized audio player that allows multiple users to listen to music together in perfect sync. Built with Flask and SocketIO, it provides a seamless collaborative listening experience.

## Features

- **Real-Time Sync**: Listen to music in perfect synchronization with other users
- **Track Management**: Upload and manage your audio tracks
- **Collaborative Control**: Play, pause, and control playback across all connected clients

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/iWebbIO/BeatMesh.git
   cd BeatMesh
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:5000`

## Project Structure

```
BeatMesh/
│
├── app/
│   ├── __init__.py     # Flask app and SocketIO initialization
│   ├── audio.py        # Audio processing functionality
│   ├── main.py         # Main routes and socket events
│   ├── static/         # Static files (music, etc.)
│   └── templates/      # HTML templates
│
├── run.py              # Application entry point
└── requirements.txt    # Project dependencies
```

## Dependencies

- Flask
- Flask-SocketIO
- Python 3.x

## Usage

1. Start the server using `python run.py`
2. Open your browser and navigate to `http://localhost:5000`
3. Upload audio files or select from existing tracks
4. Share the URL with others to listen together

by iWebbIO

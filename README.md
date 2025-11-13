# MP3 Audio Transcriber

A minimal web application that transcribes MP3 audio files using OpenAI's latest GPT-4o Mini transcription model for high-quality results.

## Features

- 🎵 Upload MP3, WAV, or M4A audio files (up to 200MB)
- 🚀 **Large file support**: Automatically splits files larger than 25MB into chunks
- ✨ **High-quality transcription** using OpenAI's GPT-4o Mini model
- 📊 **Real-time progress bar**: Visual feedback during transcription
- 💻 **Native Mac Application**: Double-click launcher for easy access
- 📝 View transcript directly in the browser
- ⬇️ Download transcript as a .txt file
- 🎨 Clean, responsive user interface
- ✅ Comprehensive error handling

## Tech Stack

- **Backend**: Flask (Python)
- **AI**: OpenAI GPT-4o Mini Transcription Model (`gpt-4o-mini-transcribe`)
- **Frontend**: Server-rendered HTML with embedded CSS
- **Deployment**: Gunicorn WSGI server (production-ready)

## Prerequisites

- Python 3.8 or higher
- An OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- FFmpeg (required for processing audio files)
  - **macOS**: `brew install ffmpeg`
  - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `choco install ffmpeg`

## Local Setup

### 1. Clone or Download the Repository

```bash
git clone https://github.com/hockeystick/audiotranscriber.git
cd audiotranscriber
```

### 2. Install FFmpeg

FFmpeg is required for processing audio files:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ffmpeg

# Windows (with Chocolatey)
choco install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### 3. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Set Environment Variables

Create a `.env` file in the project root or export the variables directly:

```bash
# Option 1: Create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env

# Option 2: Export directly (macOS/Linux)
export OPENAI_API_KEY="your-api-key-here"

# Option 2: Export directly (Windows)
set OPENAI_API_KEY=your-api-key-here
```

**Required Environment Variables:**

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `SECRET_KEY`: Flask secret key (optional, defaults to a dev key)

### 6. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:8000`

Open your browser and navigate to `http://localhost:8000` to use the app.

**Note**: The app uses port 8000 by default to avoid conflicts with macOS AirPlay (which uses port 5000). You can change the port by setting the `PORT` environment variable: `PORT=5000 python app.py`

## Usage

### As a Mac Application (Recommended for macOS)

1. **One-time setup**: Run `bash create_mac_app.sh` in the project directory
2. **Double-click** "MP3 Audio Transcriber.app" to launch
3. The app opens in Terminal and your browser automatically
4. Upload your audio file and transcribe!

### Manual Start (All Platforms)

```bash
# Make the launcher executable (first time only)
chmod +x start_app.sh

# Start the app
./start_app.sh
```

### Using the Web Interface

1. Click "Choose File" and select an MP3 audio file from your computer
2. Click the "Transcribe Audio" button
3. Watch the progress bar as your file is transcribed
4. View the transcript in the text area
5. Click "Download .txt" to save the transcript to your computer

### How Large File Processing Works

OpenAI's Whisper API has a 25MB file size limit. This app automatically handles larger files:

1. **Files ≤ 24MB**: Transcribed directly in a single API call
2. **Files > 24MB**: Automatically split into 10-minute chunks, transcribed separately, then combined

**Example**: A 58MB file (≈40 minutes) will be:
- Split into 4 chunks of ~10 minutes each
- Each chunk transcribed via OpenAI API
- Transcripts combined into a single result

This process is completely automatic and transparent to the user. Progress is logged to the server console.

## Project Structure

```
audiotranscriber/
├── app.py                  # Main Flask application
├── templates/
│   └── index.html         # HTML template with embedded CSS
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore           # Git ignore file
└── .env.example         # Example environment variables
```

## Deployment

### Deploy to Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your Git repository
3. Configure the service:
   - **Build Command**: `apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**: Add `OPENAI_API_KEY`
4. Deploy!

**Note**: Render's native environment includes ffmpeg, but if you encounter issues, you can use the build command above to ensure it's installed.

### Deploy to Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your Git repository
3. Railway will auto-detect the Python app
4. Add environment variable `OPENAI_API_KEY` in the settings
5. Add a build command if needed: `apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt`
6. Deploy!

**Note**: Railway typically includes ffmpeg in their base images.

### Deploy to Heroku

1. Install the Heroku CLI
2. Create a `Procfile` with: `web: gunicorn app:app`
3. Add the ffmpeg buildpack and deploy:

```bash
heroku create your-app-name
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
heroku buildpacks:add --index 2 heroku/python
heroku config:set OPENAI_API_KEY=your-api-key-here
git push heroku main
```

**Note**: The ffmpeg buildpack is required for processing large audio files.

### General PaaS Deployment

Most Platform-as-a-Service providers support Python apps. You'll need:

- **System Dependencies**: Ensure ffmpeg is installed (most modern PaaS providers include it)
- **Build Command**: `pip install -r requirements.txt` (or `apt-get install -y ffmpeg && pip install -r requirements.txt` if ffmpeg is not available)
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
- **Environment Variables**: Set `OPENAI_API_KEY`

## Configuration

### File Size Limits

The app supports files up to 200MB by default. Files larger than 24MB are automatically split into chunks for processing.

- `MAX_FILE_SIZE`: Maximum upload size (default: 200MB)
- `OPENAI_MAX_SIZE`: OpenAI's API limit (24MB) - files larger than this are automatically chunked
- `CHUNK_LENGTH_MS`: Length of each audio chunk (default: 10 minutes)

To modify these limits, edit the constants at the top of `app.py`.

### Supported Audio Formats

By default, the app accepts:
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- MPEG (.mpeg)

To add more formats, update the `ALLOWED_EXTENSIONS` set in `app.py`.

### Transcription Model

The app uses OpenAI's `whisper-1` model by default. This is cost-effective and accurate. To use a different model (if available), modify the `model` parameter in the `client.audio.transcriptions.create()` call in `app.py`.

## Error Handling

The app handles common errors gracefully:

- **No file selected**: Shows a friendly error message
- **Invalid file type**: Validates file extension
- **Missing API key**: Alerts user to set the environment variable
- **API errors**: Catches exceptions and displays a generic error message while logging details to the console

## Security Notes

- Never commit your `.env` file or expose your API keys
- The app uses `secure_filename()` to prevent directory traversal attacks
- Files are temporarily stored and immediately deleted after processing
- In production, always set a strong `SECRET_KEY` environment variable

## Cost Considerations

OpenAI charges for transcription based on audio length:
- Whisper API: $0.006 per minute of audio

**Examples**:
- 30-minute MP3: ~$0.18
- 60-minute MP3: ~$0.36
- 120-minute MP3: ~$0.72

**Note**: Large files are automatically split into chunks and transcribed separately. The cost is based on the total audio duration, regardless of whether it's processed as one file or multiple chunks.

## Troubleshooting

### "OPENAI_API_KEY environment variable is not set"

Make sure you've set the environment variable before running the app. See step 4 in Local Setup.

### "An error occurred during transcription"

- Check your OpenAI API key is valid
- Ensure your audio file is under 25MB
- Verify you have sufficient API credits in your OpenAI account
- Check the server console for detailed error messages

### Port already in use

The app now uses port 8000 by default to avoid conflicts with macOS AirPlay. If you need to use a different port, set the `PORT` environment variable:

```bash
PORT=9000 python app.py
```

### "ffmpeg not found" or audio processing errors

If you see errors related to ffmpeg or audio processing:

1. Verify ffmpeg is installed: `ffmpeg -version`
2. Make sure it's in your system PATH
3. On Windows, you may need to restart your terminal after installing ffmpeg
4. For deployment, ensure the platform has ffmpeg available (see deployment sections above)

## Development

To run in development mode with auto-reload:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

## License

This project is provided as-is for educational and production use.

## Support

For issues related to:
- **OpenAI API**: Visit [OpenAI Help Center](https://help.openai.com/)
- **This application**: Check the error messages in the browser and server console

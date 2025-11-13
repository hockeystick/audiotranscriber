# MP3 Audio Transcriber

A minimal web application that transcribes MP3 audio files using the OpenAI Audio Transcription API (Whisper).

## Features

- Upload MP3, WAV, or M4A audio files (up to 25MB)
- Automatic transcription using OpenAI's Whisper model
- View transcript directly in the browser
- Download transcript as a .txt file
- Clean, responsive user interface
- Comprehensive error handling

## Tech Stack

- **Backend**: Flask (Python)
- **AI**: OpenAI Audio Transcription API (Whisper)
- **Frontend**: Server-rendered HTML with embedded CSS
- **Deployment**: Gunicorn WSGI server (production-ready)

## Prerequisites

- Python 3.8 or higher
- An OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Local Setup

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd audiotranscriber
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

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

### 5. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

Open your browser and navigate to `http://localhost:5000` to use the app.

## Usage

1. Click "Choose File" and select an MP3 audio file from your computer
2. Click the "Transcribe Audio" button
3. Wait for the transcription to complete (may take a few moments for long files)
4. View the transcript in the text area
5. Click "Download .txt" to save the transcript to your computer

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
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**: Add `OPENAI_API_KEY`
4. Deploy!

### Deploy to Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your Git repository
3. Railway will auto-detect the Python app
4. Add environment variable `OPENAI_API_KEY` in the settings
5. Deploy!

### Deploy to Heroku

1. Install the Heroku CLI
2. Create a `Procfile` with: `web: gunicorn app:app`
3. Run:

```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-api-key-here
git push heroku main
```

### General PaaS Deployment

Most Platform-as-a-Service providers support Python apps. You'll need:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
- **Environment Variables**: Set `OPENAI_API_KEY`

## Configuration

### File Size Limits

The app enforces OpenAI's 25MB file size limit. To change this, modify the `MAX_FILE_SIZE` constant in `app.py`.

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

A 30-minute MP3 would cost approximately $0.18 to transcribe.

## Troubleshooting

### "OPENAI_API_KEY environment variable is not set"

Make sure you've set the environment variable before running the app. See step 4 in Local Setup.

### "An error occurred during transcription"

- Check your OpenAI API key is valid
- Ensure your audio file is under 25MB
- Verify you have sufficient API credits in your OpenAI account
- Check the server console for detailed error messages

### Port already in use

If port 5000 is already in use, you can change it by modifying the `app.run()` call in `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

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

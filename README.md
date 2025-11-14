# MP3 Audio Transcriber

A minimal web application that transcribes MP3 audio files using multiple AI providers (OpenAI and Google Cloud) for high-quality results with speaker diarization support.

## Features

- 🎵 Upload MP3, WAV, or M4A audio files (up to 200MB)
- 🚀 **Large file support**: Automatically splits files larger than provider limits into chunks
- ✨ **Multi-provider support**: Choose between OpenAI or Google Cloud Speech-to-Text
- 🎙️ **Speaker diarization**: Identify and label different speakers in conversations (Google Cloud)
- 🌍 **Multi-language support**: Auto-detect or select from 14+ languages
- 📊 **Real-time progress bar**: Visual feedback during transcription
- 💻 **Native Mac Application**: Double-click launcher for easy access
- 📝 View transcript directly in the browser
- ⬇️ Download transcript as a .txt file
- 🎨 Clean, responsive user interface
- ✅ Comprehensive error handling

## Tech Stack

- **Backend**: Flask (Python)
- **AI Providers**:
  - OpenAI GPT-4o Mini Transcription Model (`gpt-4o-mini-transcribe`)
  - Google Cloud Speech-to-Text V2 API (Chirp 3 model)
- **Frontend**: Server-rendered HTML with embedded CSS
- **Deployment**: Gunicorn WSGI server (production-ready)

## Provider Comparison

| Feature | OpenAI | Google Cloud (Chirp 3) |
|---------|--------|------------------------|
| **Max File Size** | 24MB (auto-chunks larger files) | 200MB (auto-chunks larger files) |
| **Diarization** | Not currently available in SDK | ✅ Full speaker diarization support |
| **Languages** | 50+ languages | 100+ languages |
| **Pricing** | $0.006/minute | Pay-as-you-go (varies by region) |
| **Setup** | API key only | Project ID + Authentication |
| **Best For** | Quick transcription, cost-effective | Speaker identification, enterprise use |

## Prerequisites

- Python 3.8 or higher
- FFmpeg (required for processing audio files)
  - **macOS**: `brew install ffmpeg`
  - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `choco install ffmpeg`

### Provider Requirements

**For OpenAI:**
- An OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

**For Google Cloud (optional, for diarization support):**
- A Google Cloud project with Speech-to-Text API enabled
- Google Cloud authentication configured (see setup below)

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

**For OpenAI (Basic Setup):**
```bash
# Option 1: Create a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env

# Option 2: Export directly (macOS/Linux)
export OPENAI_API_KEY="your-api-key-here"

# Option 2: Export directly (Windows)
set OPENAI_API_KEY=your-api-key-here
```

**For Google Cloud (Optional, for Diarization):**

1. **Create a Google Cloud Project:**
   ```bash
   # Install gcloud CLI if not already installed
   # Visit: https://cloud.google.com/sdk/docs/install

   # Create a new project (or use existing)
   gcloud projects create your-project-id
   gcloud config set project your-project-id
   ```

2. **Enable Speech-to-Text API:**
   ```bash
   gcloud services enable speech.googleapis.com
   ```

3. **Set up authentication:**
   ```bash
   # Authenticate with your Google account
   gcloud auth application-default login

   # Or create a service account and download credentials
   gcloud iam service-accounts create transcriber-sa
   gcloud projects add-iam-policy-binding your-project-id \
     --member="serviceAccount:transcriber-sa@your-project-id.iam.gserviceaccount.com" \
     --role="roles/speech.client"
   gcloud iam service-accounts keys create credentials.json \
     --iam-account=transcriber-sa@your-project-id.iam.gserviceaccount.com

   # Set the credentials path
   export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
   ```

4. **Set environment variables:**
   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GOOGLE_CLOUD_REGION="us"  # Optional, defaults to 'us'
   ```

**Environment Variables Summary:**

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | For OpenAI | Your OpenAI API key |
| `GOOGLE_CLOUD_PROJECT` | For Google Cloud | Your Google Cloud project ID |
| `GOOGLE_APPLICATION_CREDENTIALS` | For Google Cloud | Path to service account JSON (if using service account) |
| `GOOGLE_CLOUD_REGION` | Optional | Google Cloud region (default: 'us') |
| `SECRET_KEY` | Optional | Flask secret key (defaults to dev key) |

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

1. **Select a Provider:** Choose between OpenAI or Google Cloud from the dropdown
   - OpenAI: Fast, cost-effective, no diarization
   - Google Cloud: Speaker diarization support, larger file support

2. **Select Language:** Choose "Auto-detect" or a specific language (English, Spanish, etc.)

3. **Enable Diarization (Optional):** Check the box to identify different speakers
   - Only available with Google Cloud provider
   - Automatically disabled when OpenAI is selected

4. **Upload File:** Click "Choose File" and select an MP3 audio file from your computer

5. **Transcribe:** Click the "Transcribe Audio" button and watch the progress bar

6. **View Results:** The transcript appears below, with speaker labels if diarization was enabled

7. **Download:** Click "Download .txt" to save the transcript to your computer

### How Large File Processing Works

Each provider has different file size limits. The app automatically handles files that exceed provider limits:

**OpenAI:**
- File size limit: 24MB
- Files > 24MB: Automatically split into 10-minute chunks, transcribed separately, then combined

**Google Cloud:**
- File size limit: 200MB
- Files > 200MB: Automatically split into 10-minute chunks, transcribed separately, then combined

**Example**: A 58MB file (≈40 minutes) will be:
- **With OpenAI**: Split into 4 chunks of ~10 minutes each, transcribed separately, then combined
- **With Google Cloud**: Transcribed directly in a single API call (no splitting needed)

This process is completely automatic and transparent to the user. Progress is logged to the server console.

### Speaker Diarization

When using Google Cloud with diarization enabled, the transcript will include speaker labels:

```
Speaker 1: Hello, how are you today?
Speaker 2: I'm doing great, thanks for asking.
Speaker 1: That's wonderful to hear.
```

Diarization is particularly useful for:
- Interview transcription
- Meeting recordings
- Podcast transcription
- Multi-speaker conversations

## Project Structure

```
audiotranscriber/
├── app.py                      # Main Flask application
├── providers/                  # Transcription provider implementations
│   ├── __init__.py            # Provider factory and registry
│   ├── base.py                # Abstract base provider class
│   ├── openai_provider.py     # OpenAI implementation
│   └── google_provider.py     # Google Cloud implementation
├── templates/
│   └── index.html             # HTML template with embedded CSS
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .gitignore                # Git ignore file
├── start_app.sh              # Launcher script
├── create_mac_app.sh         # Mac app creator
└── .env.example              # Example environment variables
```

## Deployment

### Deploy to Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your Git repository
3. Configure the service:
   - **Build Command**: `apt-get update && apt-get install -y ffmpeg && pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**:
     - Add `OPENAI_API_KEY` (required for OpenAI)
     - Add `GOOGLE_CLOUD_PROJECT` (optional, for Google Cloud)
     - Add `GOOGLE_APPLICATION_CREDENTIALS` as a secret file if using Google Cloud service account
4. Deploy!

**Note**: For Google Cloud on Render, you may need to add the service account JSON as a secret file and set the path in environment variables.

### Deploy to Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your Git repository
3. Railway will auto-detect the Python app
4. Add environment variables in the settings:
   - `OPENAI_API_KEY` (required for OpenAI)
   - `GOOGLE_CLOUD_PROJECT` (optional, for Google Cloud)
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
# Optional: Add Google Cloud credentials
heroku config:set GOOGLE_CLOUD_PROJECT=your-project-id
git push heroku main
```

**Note**: The ffmpeg buildpack is required for processing large audio files.

### General PaaS Deployment

Most Platform-as-a-Service providers support Python apps. You'll need:

- **System Dependencies**: Ensure ffmpeg is installed (most modern PaaS providers include it)
- **Build Command**: `pip install -r requirements.txt` (or `apt-get install -y ffmpeg && pip install -r requirements.txt` if ffmpeg is not available)
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
- **Environment Variables**:
  - Set `OPENAI_API_KEY` (required for OpenAI)
  - Set `GOOGLE_CLOUD_PROJECT` (optional, for Google Cloud)
  - Set `GOOGLE_APPLICATION_CREDENTIALS` path if using service account

## Configuration

### File Size Limits

The app supports files up to 200MB by default. Provider-specific limits:

- **OpenAI**: 24MB limit - files larger than this are automatically chunked
- **Google Cloud**: 200MB limit - files larger than this are automatically chunked
- `MAX_FILE_SIZE`: Maximum upload size (default: 200MB)
- `CHUNK_LENGTH_MS`: Length of each audio chunk (default: 10 minutes)

To modify these limits, edit the constants in the provider files under `providers/`.

### Supported Audio Formats

By default, the app accepts:
- MP3 (.mp3)
- WAV (.wav)
- M4A (.m4a)
- MPEG (.mpeg)

To add more formats, update the `ALLOWED_EXTENSIONS` set in `app.py`.

### Transcription Models

The app supports multiple transcription models:

- **OpenAI**: Uses `gpt-4o-mini-transcribe` model for high-quality, cost-effective transcription
- **Google Cloud**: Uses Chirp 3 model for advanced features like speaker diarization

To modify models, edit the respective provider files in `providers/openai_provider.py` or `providers/google_provider.py`.

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

### OpenAI Pricing
- Whisper API: $0.006 per minute of audio
- **Examples**:
  - 30-minute MP3: ~$0.18
  - 60-minute MP3: ~$0.36
  - 120-minute MP3: ~$0.72

### Google Cloud Pricing
- Speech-to-Text V2 (Chirp 3): Varies by region and features
- Standard audio: ~$0.024 per minute for first 60 minutes per month (free tier available)
- Diarization adds additional cost
- Check [Google Cloud Pricing](https://cloud.google.com/speech-to-text/pricing) for current rates

**Note**: Large files are automatically split into chunks and transcribed separately. The cost is based on the total audio duration, regardless of whether it's processed as one file or multiple chunks.

## Troubleshooting

### Provider Configuration Issues

**"No providers are configured!"**
- Make sure you've set at least one provider's environment variables
- For OpenAI: Set `OPENAI_API_KEY`
- For Google Cloud: Set `GOOGLE_CLOUD_PROJECT` and authenticate with `gcloud auth application-default login`

**"Provider is not configured"**
- OpenAI: Check that `OPENAI_API_KEY` is set and valid
- Google Cloud: Verify `GOOGLE_CLOUD_PROJECT` is set and you've authenticated properly

### Transcription Errors

**"An error occurred during transcription"**
- Check your provider credentials are valid
- Ensure you have sufficient API credits/quota
- Verify your audio file is in a supported format
- Check the server console for detailed error messages

**Diarization not available**
- Only Google Cloud supports diarization
- Ensure you've selected Google Cloud as the provider
- The diarization checkbox will be automatically disabled if the provider doesn't support it

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

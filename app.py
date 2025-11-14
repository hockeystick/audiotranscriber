"""
MP3 Audio Transcription Web App
================================
A Flask application that allows users to upload MP3 files and transcribe them
using multiple AI providers (OpenAI, Google Cloud).
Supports large files by automatically splitting them into chunks.
"""

import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import tempfile
from io import BytesIO
from pydub import AudioSegment
import math

# Import providers
from providers import get_provider, get_available_providers

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure upload settings
ALLOWED_EXTENSIONS = {'mp3', 'mpeg', 'wav', 'm4a'}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB limit for uploads
CHUNK_LENGTH_MS = 10 * 60 * 1000  # 10 minutes per chunk in milliseconds


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.

    Args:
        filename: The name of the uploaded file

    Returns:
        Boolean indicating if the file extension is allowed
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def split_audio_file(file_path, chunk_length_ms=CHUNK_LENGTH_MS):
    """
    Split a large audio file into smaller chunks for processing.

    Args:
        file_path: Path to the audio file
        chunk_length_ms: Length of each chunk in milliseconds

    Returns:
        List of paths to temporary chunk files
    """
    print(f"Loading audio file for chunking: {file_path}")

    # Load the audio file
    audio = AudioSegment.from_file(file_path)

    # Calculate the number of chunks needed
    total_length_ms = len(audio)
    num_chunks = math.ceil(total_length_ms / chunk_length_ms)

    print(f"Audio length: {total_length_ms/1000:.1f}s, splitting into {num_chunks} chunks")

    chunk_files = []

    # Split the audio into chunks
    for i in range(num_chunks):
        start_ms = i * chunk_length_ms
        end_ms = min((i + 1) * chunk_length_ms, total_length_ms)

        chunk = audio[start_ms:end_ms]

        # Create a temporary file for this chunk
        chunk_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        chunk.export(chunk_file.name, format="mp3")
        chunk_files.append(chunk_file.name)

        print(f"  Chunk {i+1}/{num_chunks}: {start_ms/1000:.1f}s to {end_ms/1000:.1f}s")

    return chunk_files


def transcribe_audio_file(file_path, filename, provider_name='openai', language='auto', enable_diarization=False, model=None):
    """
    Transcribe an audio file using the specified provider.
    Automatically handles large files by chunking.

    Args:
        file_path: Path to the audio file
        filename: Original filename (for logging)
        provider_name: Name of the provider to use ('openai' or 'google')
        language: Language code ('auto', 'en-US', etc.)
        enable_diarization: Enable speaker identification
        model: Model to use (if None, uses provider's default)

    Returns:
        The complete transcript as a string
    """
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size / (1024*1024):.2f}MB")
    print(f"Provider: {provider_name}, Model: {model or 'default'}, Language: {language}, Diarization: {enable_diarization}")

    # Get the provider instance
    try:
        provider = get_provider(provider_name)
    except ValueError as e:
        raise ValueError(f"Invalid provider: {e}")

    # Check if provider is configured
    if not provider.is_configured():
        raise ValueError(
            f"{provider.name} is not configured. "
            f"Please set the required environment variables/credentials."
        )

    # Check if file is within provider's size limit
    if file_size <= provider.max_file_size:
        print(f"File is within {provider.name} size limit, transcribing directly...")
        return provider.transcribe(
            file_path=file_path,
            language=language,
            enable_diarization=enable_diarization,
            model=model
        )

    # File is too large, need to split into chunks
    print(f"File exceeds {provider.name} size limit, splitting into chunks...")
    chunk_files = []

    try:
        # Split the audio file into chunks
        chunk_files = split_audio_file(file_path)

        # Transcribe using provider's chunked method
        transcript = provider.transcribe_chunked(
            chunk_files=chunk_files,
            language=language,
            enable_diarization=enable_diarization,
            model=model
        )

        print(f"All chunks transcribed successfully with {provider.name}")
        return transcript

    finally:
        # Clean up chunk files
        for chunk_file in chunk_files:
            if os.path.exists(chunk_file):
                os.unlink(chunk_file)


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route that handles both displaying the form and processing transcription.

    GET: Display the upload form with available providers
    POST: Process the uploaded MP3 file and return the transcript
    """
    transcript = None
    providers_info = get_available_providers()

    if request.method == 'POST':
        # Get form parameters
        provider_name = request.form.get('provider', 'openai')
        language = request.form.get('language', 'auto')
        enable_diarization = request.form.get('enable_diarization') == 'on'
        model = request.form.get('model', None)  # Get selected model

        # Validate that a file was uploaded
        if 'audio_file' not in request.files:
            flash('No file selected. Please choose an MP3 file to upload.', 'error')
            return render_template('index.html', transcript=None, providers=providers_info)

        file = request.files['audio_file']

        # Check if user actually selected a file
        if file.filename == '':
            flash('No file selected. Please choose an MP3 file to upload.', 'error')
            return render_template('index.html', transcript=None, providers=providers_info)

        # Validate file type
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload an MP3, WAV, or M4A file.', 'error')
            return render_template('index.html', transcript=None, providers=providers_info)

        try:
            # Save uploaded file to a temporary location
            filename = secure_filename(file.filename)

            # Create a temporary file to store the upload
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name

            try:
                # Transcribe the audio file (handles both small and large files)
                print(f"Transcribing file: {filename}")
                transcript = transcribe_audio_file(
                    temp_file_path,
                    filename,
                    provider_name=provider_name,
                    language=language,
                    enable_diarization=enable_diarization,
                    model=model
                )
                print("Transcription successful")

                flash('Transcription completed successfully!', 'success')

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            # Log the error and show a user-friendly message
            print(f"Transcription error: {str(e)}")
            flash(f'An error occurred during transcription: {str(e)}', 'error')
            return render_template('index.html', transcript=None, providers=providers_info)

    return render_template('index.html', transcript=transcript, providers=providers_info)


@app.route('/download')
def download():
    """
    Route to download the transcript as a .txt file.
    Expects the transcript text to be passed as a query parameter.
    """
    transcript_text = request.args.get('text', '')

    if not transcript_text:
        flash('No transcript available to download.', 'error')
        return redirect(url_for('index'))

    # Create a BytesIO object to send as a file
    buffer = BytesIO()
    buffer.write(transcript_text.encode('utf-8'))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name='transcript.txt',
        mimetype='text/plain'
    )


if __name__ == '__main__':
    # Check which providers are configured
    providers_info = get_available_providers()
    configured_providers = [name for name, info in providers_info.items() if info['configured']]

    print("\n" + "="*60)
    print("MP3 Audio Transcriber - Multi-Provider Edition")
    print("="*60)

    if configured_providers:
        print(f"✅ Configured providers: {', '.join(configured_providers)}")
    else:
        print("⚠️  WARNING: No providers are configured!")
        print("\nTo use OpenAI:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nTo use Google Cloud:")
        print("  export GOOGLE_CLOUD_PROJECT='your-project-id'")
        print("  gcloud auth application-default login")

    print("="*60 + "\n")

    # Run the Flask development server
    # In production, use a proper WSGI server like gunicorn
    # Using port 8000 to avoid conflicts with macOS AirPlay on port 5000
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)

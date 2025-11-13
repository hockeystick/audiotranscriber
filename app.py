"""
MP3 Audio Transcription Web App
================================
A Flask application that allows users to upload MP3 files and transcribe them
using the OpenAI Audio Transcription API.
Supports large files by automatically splitting them into chunks.
"""

import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from openai import OpenAI
import tempfile
from io import BytesIO
from pydub import AudioSegment
import math

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure upload settings
ALLOWED_EXTENSIONS = {'mp3', 'mpeg', 'wav', 'm4a'}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB limit for uploads
OPENAI_MAX_SIZE = 24 * 1024 * 1024  # 24MB - OpenAI's API limit (stay under 25MB)
CHUNK_LENGTH_MS = 10 * 60 * 1000  # 10 minutes per chunk in milliseconds

# Initialize OpenAI client
# API key is read from environment variable OPENAI_API_KEY
api_key = os.environ.get('OPENAI_API_KEY')
if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None


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


def format_diarized_transcript(segments):
    """
    Format diarized transcript segments into a readable format.

    Args:
        segments: List of segment objects with speaker, text, start, end

    Returns:
        Formatted transcript string with speaker labels
    """
    formatted_lines = []
    current_speaker = None

    for segment in segments:
        speaker = segment.get('speaker', 'Unknown')
        text = segment.get('text', '').strip()

        if not text:
            continue

        # Group consecutive segments from the same speaker
        if speaker != current_speaker:
            formatted_lines.append(f"\n{speaker}: {text}")
            current_speaker = speaker
        else:
            # Continue the current speaker's text
            formatted_lines.append(f" {text}")

    return "".join(formatted_lines).strip()


def transcribe_audio_file(file_path, filename):
    """
    Transcribe an audio file, automatically handling large files by chunking.

    Args:
        file_path: Path to the audio file
        filename: Original filename (for logging)

    Returns:
        The complete transcript as a string
    """
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size / (1024*1024):.2f}MB")

    # Use GPT-4o Mini for high-quality, reliable transcription
    model = "gpt-4o-mini-transcribe"

    # If file is small enough, transcribe directly
    if file_size <= OPENAI_MAX_SIZE:
        print("File is within size limit, transcribing directly...")
        with open(file_path, 'rb') as audio_file:
            response = client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                response_format="text"
            )
            return response

    # File is too large, need to split into chunks
    print("File exceeds size limit, splitting into chunks...")
    chunk_files = []

    try:
        # Split the audio file into chunks
        chunk_files = split_audio_file(file_path)

        # Transcribe each chunk
        transcripts = []
        for i, chunk_file in enumerate(chunk_files):
            print(f"Transcribing chunk {i+1}/{len(chunk_files)}...")

            with open(chunk_file, 'rb') as audio_file:
                response = client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    response_format="text"
                )
                transcripts.append(response)

        # Combine all transcripts
        complete_transcript = "\n\n".join(transcripts)
        print("All chunks transcribed successfully")

        return complete_transcript

    finally:
        # Clean up chunk files
        for chunk_file in chunk_files:
            if os.path.exists(chunk_file):
                os.unlink(chunk_file)


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route that handles both displaying the form and processing transcription.

    GET: Display the upload form
    POST: Process the uploaded MP3 file and return the transcript
    """
    transcript = None

    if request.method == 'POST':
        # Check if API key is configured
        if not os.environ.get('OPENAI_API_KEY'):
            flash('Error: OPENAI_API_KEY environment variable is not set.', 'error')
            return render_template('index.html', transcript=None)

        # Validate that a file was uploaded
        if 'audio_file' not in request.files:
            flash('No file selected. Please choose an MP3 file to upload.', 'error')
            return render_template('index.html', transcript=None)

        file = request.files['audio_file']

        # Check if user actually selected a file
        if file.filename == '':
            flash('No file selected. Please choose an MP3 file to upload.', 'error')
            return render_template('index.html', transcript=None)

        # Validate file type
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload an MP3, WAV, or M4A file.', 'error')
            return render_template('index.html', transcript=None)

        try:
            # Save uploaded file to a temporary location
            # We need to save it because OpenAI API expects a file-like object with a name
            filename = secure_filename(file.filename)

            # Create a temporary file to store the upload
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                file.save(temp_file.name)
                temp_file_path = temp_file.name

            try:
                # Transcribe the audio file (handles both small and large files)
                print(f"Transcribing file: {filename}")
                transcript = transcribe_audio_file(temp_file_path, filename)
                print("Transcription successful")

                flash('Transcription completed successfully!', 'success')

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            # Log the error and show a user-friendly message
            print(f"Transcription error: {str(e)}")
            flash('An error occurred during transcription. Please try again.', 'error')
            return render_template('index.html', transcript=None)

    return render_template('index.html', transcript=transcript)


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
    # Check if OpenAI API key is set
    if not os.environ.get('OPENAI_API_KEY'):
        print("\n" + "="*60)
        print("WARNING: OPENAI_API_KEY environment variable is not set!")
        print("Please set it before using the application.")
        print("="*60 + "\n")

    # Run the Flask development server
    # In production, use a proper WSGI server like gunicorn
    # Using port 8000 to avoid conflicts with macOS AirPlay on port 5000
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)

"""
MP3 Audio Transcription Web App
================================
A Flask application that allows users to upload MP3 files and transcribe them
using the OpenAI Audio Transcription API.
"""

import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from openai import OpenAI
import tempfile
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure upload settings
ALLOWED_EXTENSIONS = {'mp3', 'mpeg', 'wav', 'm4a'}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB limit (OpenAI's limit)

# Initialize OpenAI client
# API key is read from environment variable OPENAI_API_KEY
try:
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
except Exception as e:
    print(f"Warning: OpenAI client initialization issue: {e}")
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
                # Send the audio file to OpenAI for transcription
                print(f"Transcribing file: {filename}")

                with open(temp_file_path, 'rb') as audio_file:
                    # Call OpenAI Audio Transcription API
                    # Using whisper-1 model which is reliable and cost-effective
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"  # Plain text output
                    )

                # Extract transcript from response
                transcript = response
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
    app.run(debug=True, host='0.0.0.0', port=5000)

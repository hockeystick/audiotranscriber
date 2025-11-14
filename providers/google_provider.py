"""
Google Cloud Speech-to-Text Provider
=====================================
Implements transcription using Google Cloud's Chirp 3 model
"""

import os
from typing import Optional, List
from .base import TranscriptionProvider

try:
    from google.cloud.speech_v2 import SpeechClient
    from google.cloud.speech_v2.types import cloud_speech
    from google.api_core.client_options import ClientOptions
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GoogleCloudProvider(TranscriptionProvider):
    """Google Cloud Speech-to-Text (Chirp 3) provider"""

    def __init__(self):
        super().__init__()
        self.name = "Google Cloud (Chirp 3)"
        self.supports_diarization = True  # Chirp 3 has excellent diarization
        self.max_file_size = 200 * 1024 * 1024  # 200MB via BatchRecognize

        # Configuration
        self.project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.region = os.environ.get('GOOGLE_CLOUD_REGION', 'us')

        # Initialize client if credentials are available
        self.client = None
        if GOOGLE_AVAILABLE and self.is_configured():
            try:
                self.client = SpeechClient(
                    client_options=ClientOptions(
                        api_endpoint=f"{self.region}-speech.googleapis.com"
                    )
                )
            except Exception as e:
                print(f"[Google Cloud] Failed to initialize client: {e}")
                self.client = None

    def is_configured(self) -> bool:
        """
        Check if Google Cloud is properly configured.

        Requires either:
        - GOOGLE_APPLICATION_CREDENTIALS environment variable
        - gcloud auth application-default credentials
        - GOOGLE_CLOUD_PROJECT environment variable
        """
        if not GOOGLE_AVAILABLE:
            return False

        # Check if project ID is set
        if not self.project_id:
            return False

        # Check if credentials are available
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path and os.path.exists(credentials_path):
            return True

        # Check for application default credentials
        # This is set when using: gcloud auth application-default login
        try:
            import google.auth
            credentials, project = google.auth.default()
            return True
        except Exception:
            return False

    def transcribe(
        self,
        file_path: str,
        language: Optional[str] = None,
        enable_diarization: bool = False,
        **kwargs
    ) -> str:
        """
        Transcribe a single audio file using Google Cloud Chirp 3.

        Args:
            file_path: Path to audio file
            language: BCP-47 language code (e.g., 'en-US', 'auto' for auto-detection)
            enable_diarization: Enable speaker diarization
            **kwargs: Additional options

        Returns:
            Transcript as string
        """
        if not self.is_configured():
            raise ValueError("Google Cloud not configured. Set GOOGLE_CLOUD_PROJECT and authentication.")

        if not self.client:
            raise ValueError("Google Cloud client not initialized")

        print(f"[Google Cloud] Transcribing with Chirp 3 (diarization: {enable_diarization})")

        # Read audio file
        with open(file_path, 'rb') as f:
            audio_content = f.read()

        # Determine language codes
        if language == 'auto' or language is None:
            language_codes = ["auto"]  # Auto-detect language
        elif isinstance(language, list):
            language_codes = language
        else:
            language_codes = [language]

        # Build recognition config
        config = cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=language_codes,
            model="chirp_3",
        )

        # Add diarization if enabled
        if enable_diarization:
            config.features = cloud_speech.RecognitionFeatures(
                diarization_config=cloud_speech.SpeakerDiarizationConfig()
            )

        # Create recognition request
        request = cloud_speech.RecognizeRequest(
            recognizer=f"projects/{self.project_id}/locations/{self.region}/recognizers/_",
            config=config,
            content=audio_content,
        )

        # Transcribe
        response = self.client.recognize(request=request)

        # Format results
        if enable_diarization:
            return self._format_diarized_results(response.results)
        else:
            return self._format_standard_results(response.results)

    def transcribe_chunked(
        self,
        chunk_files: List[str],
        language: Optional[str] = None,
        enable_diarization: bool = False,
        **kwargs
    ) -> str:
        """
        Transcribe multiple audio chunks using Google Cloud.

        Args:
            chunk_files: List of audio chunk file paths
            language: Language code
            enable_diarization: Enable speaker diarization
            **kwargs: Additional options

        Returns:
            Combined transcript
        """
        if not self.is_configured():
            raise ValueError("Google Cloud not configured")

        transcripts = []

        for i, chunk_file in enumerate(chunk_files):
            print(f"[Google Cloud] Transcribing chunk {i+1}/{len(chunk_files)}...")

            transcript = self.transcribe(
                file_path=chunk_file,
                language=language,
                enable_diarization=enable_diarization,
                **kwargs
            )
            transcripts.append(transcript)

        # Combine transcripts with clear chunk separators
        if enable_diarization:
            # For diarized content, use a clear visual separator between chunks
            separator = "\n\n" + "=" * 50 + "\n\n"
            return separator.join(transcripts)
        else:
            # For standard content, use paragraph breaks
            return "\n\n".join(transcripts)

    def _format_standard_results(self, results) -> str:
        """
        Format standard (non-diarized) transcription results.
        Creates properly formatted paragraphs for easy copy-pasting.
        """
        transcript_parts = []
        for result in results:
            if result.alternatives:
                text = result.alternatives[0].transcript.strip()
                if text:
                    transcript_parts.append(text)

        # Join parts with proper spacing
        # If a part ends with sentence-ending punctuation, add paragraph break
        formatted_text = []
        for i, part in enumerate(transcript_parts):
            formatted_text.append(part)

            # Add paragraph break after sentence-ending punctuation
            # or if this is not the last part
            if i < len(transcript_parts) - 1:
                if part.rstrip().endswith(('.', '!', '?')):
                    formatted_text.append('\n\n')
                else:
                    formatted_text.append(' ')

        return "".join(formatted_text)

    def _format_diarized_results(self, results) -> str:
        """
        Format diarized transcription results with speaker labels.
        Creates a copy-paste friendly format with clear speaker segments.
        """
        formatted_lines = []
        current_speaker = None
        current_speaker_text = []
        current_speaker_start_time = None

        for result in results:
            if not result.alternatives:
                continue

            alternative = result.alternatives[0]

            # Check if we have word-level speaker labels
            if hasattr(alternative, 'words') and alternative.words:
                for word_info in alternative.words:
                    speaker = getattr(word_info, 'speaker_label', 'Unknown')
                    word = word_info.word

                    # Get timestamp if available
                    start_time = None
                    if hasattr(word_info, 'start_offset'):
                        start_time = word_info.start_offset

                    # If speaker changed, flush current speaker's text
                    if speaker != current_speaker:
                        if current_speaker is not None and current_speaker_text:
                            # Join the accumulated text and add to output
                            text = ' '.join(current_speaker_text)

                            # Add timestamp if available
                            if current_speaker_start_time:
                                timestamp = self._format_timestamp(current_speaker_start_time)
                                formatted_lines.append(f"[{timestamp}] {current_speaker}: {text}\n\n")
                            else:
                                formatted_lines.append(f"{current_speaker}: {text}\n\n")

                        # Start new speaker
                        current_speaker = speaker
                        current_speaker_text = [word]
                        current_speaker_start_time = start_time
                    else:
                        # Same speaker, accumulate words
                        current_speaker_text.append(word)
            else:
                # No word-level info, just add transcript
                if current_speaker_text:
                    # Flush any pending text first
                    text = ' '.join(current_speaker_text)
                    formatted_lines.append(f"{current_speaker}: {text}\n\n")
                    current_speaker_text = []
                formatted_lines.append(alternative.transcript + "\n\n")

        # Don't forget the last speaker's text
        if current_speaker is not None and current_speaker_text:
            text = ' '.join(current_speaker_text)

            # Add timestamp if available
            if current_speaker_start_time:
                timestamp = self._format_timestamp(current_speaker_start_time)
                formatted_lines.append(f"[{timestamp}] {current_speaker}: {text}\n")
            else:
                formatted_lines.append(f"{current_speaker}: {text}\n")

        return "".join(formatted_lines).strip()

    def _format_timestamp(self, time_offset) -> str:
        """
        Format a time offset into MM:SS format.

        Args:
            time_offset: Google's Duration object or similar

        Returns:
            Formatted timestamp string (e.g., "02:35")
        """
        try:
            # Handle Duration object with seconds and nanos
            if hasattr(time_offset, 'seconds'):
                total_seconds = time_offset.seconds
            elif hasattr(time_offset, 'total_seconds'):
                total_seconds = int(time_offset.total_seconds())
            else:
                total_seconds = int(time_offset)

            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes:02d}:{seconds:02d}"
        except (AttributeError, ValueError, TypeError):
            return "00:00"

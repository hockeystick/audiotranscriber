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
    """Google Cloud Speech-to-Text provider with multiple model support"""

    def __init__(self):
        super().__init__()
        self.name = "Google Cloud Speech-to-Text"
        self.supports_diarization = True  # All Chirp models support diarization
        self.max_file_size = 200 * 1024 * 1024  # 200MB via BatchRecognize

        # Define available models
        self.available_models = [
            {
                "id": "chirp",
                "name": "Chirp (Latest)",
                "description": "Latest Chirp model with best accuracy and features"
            },
            {
                "id": "chirp_2",
                "name": "Chirp 2",
                "description": "Second generation Chirp model"
            },
            {
                "id": "chirp_3",
                "name": "Chirp 3",
                "description": "Third generation Chirp model (stable)"
            },
            {
                "id": "long",
                "name": "Long",
                "description": "Optimized for long-form content (podcasts, meetings)"
            },
            {
                "id": "short",
                "name": "Short",
                "description": "Optimized for short utterances and commands"
            },
            {
                "id": "telephony",
                "name": "Telephony",
                "description": "Optimized for telephony audio (8kHz)"
            },
            {
                "id": "medical_conversation",
                "name": "Medical Conversation",
                "description": "Specialized for medical conversations and terminology"
            },
            {
                "id": "medical_dictation",
                "name": "Medical Dictation",
                "description": "Specialized for medical dictation and clinical notes"
            }
        ]
        self.default_model = "chirp"  # Use latest Chirp as default

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
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Transcribe a single audio file using Google Cloud Speech-to-Text.

        Args:
            file_path: Path to audio file
            language: BCP-47 language code (e.g., 'en-US', 'auto' for auto-detection)
            enable_diarization: Enable speaker diarization
            model: Model to use (e.g., 'chirp', 'chirp_2', 'long', etc.)
            **kwargs: Additional options

        Returns:
            Transcript as string
        """
        if not self.is_configured():
            raise ValueError("Google Cloud not configured. Set GOOGLE_CLOUD_PROJECT and authentication.")

        if not self.client:
            raise ValueError("Google Cloud client not initialized")

        # Use default model if none specified
        selected_model = model or self.default_model

        # Validate model
        valid_models = [m['id'] for m in self.available_models]
        if selected_model not in valid_models:
            raise ValueError(f"Invalid model '{selected_model}'. Valid models: {', '.join(valid_models)}")

        print(f"[Google Cloud] Transcribing with model '{selected_model}' (diarization: {enable_diarization})")

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
            model=selected_model,
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
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Transcribe multiple audio chunks using Google Cloud.

        Args:
            chunk_files: List of audio chunk file paths
            language: Language code
            enable_diarization: Enable speaker diarization
            model: Model to use (e.g., 'chirp', 'chirp_2', 'long', etc.)
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
                model=model,
                **kwargs
            )
            transcripts.append(transcript)

        # Combine transcripts
        if enable_diarization:
            return "\n\n---\n\n".join(transcripts)  # Clear separator for diarized chunks
        else:
            return "\n\n".join(transcripts)

    def _format_standard_results(self, results) -> str:
        """Format standard (non-diarized) transcription results"""
        transcript_parts = []
        for result in results:
            if result.alternatives:
                transcript_parts.append(result.alternatives[0].transcript)
        return " ".join(transcript_parts)

    def _format_diarized_results(self, results) -> str:
        """Format diarized transcription results with speaker labels"""
        formatted_lines = []
        current_speaker = None

        for result in results:
            if not result.alternatives:
                continue

            alternative = result.alternatives[0]

            # Check if we have word-level speaker labels
            if hasattr(alternative, 'words') and alternative.words:
                for word_info in alternative.words:
                    speaker = getattr(word_info, 'speaker_label', 'Unknown')
                    word = word_info.word

                    # Start new speaker line if speaker changed
                    if speaker != current_speaker:
                        formatted_lines.append(f"\n{speaker}: {word}")
                        current_speaker = speaker
                    else:
                        formatted_lines.append(f" {word}")
            else:
                # No word-level info, just add transcript
                formatted_lines.append(alternative.transcript)

        return "".join(formatted_lines).strip()

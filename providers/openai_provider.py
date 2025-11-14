"""
OpenAI Transcription Provider
==============================
Implements transcription using OpenAI's Whisper and GPT-4o models
"""

import os
from typing import Optional, List
from openai import OpenAI
from .base import TranscriptionProvider


class OpenAIProvider(TranscriptionProvider):
    """OpenAI Whisper/GPT-4o transcription provider"""

    def __init__(self):
        super().__init__()
        self.name = "OpenAI"
        self.supports_diarization = True  # Via gpt-4o-transcribe-diarize
        self.max_file_size = 24 * 1024 * 1024  # 24MB

        # Define available models
        self.available_models = [
            {
                "id": "gpt-4o-mini-transcribe",
                "name": "GPT-4o Mini Transcribe",
                "description": "Fast, cost-effective transcription model (recommended)"
            },
            {
                "id": "gpt-4o-transcribe",
                "name": "GPT-4o Transcribe",
                "description": "High-quality transcription with better accuracy"
            },
            {
                "id": "whisper-1",
                "name": "Whisper",
                "description": "Original Whisper model"
            }
        ]
        self.default_model = "gpt-4o-mini-transcribe"  # Stable, reliable model

        # Initialize client if API key is available
        api_key = os.environ.get('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key) if api_key else None

    def is_configured(self) -> bool:
        """Check if OpenAI API key is set"""
        return self.client is not None

    def transcribe(
        self,
        file_path: str,
        language: Optional[str] = None,
        enable_diarization: bool = False,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Transcribe a single audio file using OpenAI.

        Args:
            file_path: Path to audio file
            language: Language code (optional, OpenAI auto-detects)
            enable_diarization: Use gpt-4o-transcribe-diarize model
            model: Model to use (e.g., 'gpt-4o-mini-transcribe', 'whisper-1')
            **kwargs: Additional options

        Returns:
            Transcript as string
        """
        if not self.is_configured():
            raise ValueError("OpenAI API key not configured")

        # Use default model if none specified
        selected_model = model or self.default_model

        # Validate model
        valid_models = [m['id'] for m in self.available_models]
        if selected_model not in valid_models:
            raise ValueError(f"Invalid model '{selected_model}'. Valid models: {', '.join(valid_models)}")

        print(f"[OpenAI] Transcribing with model: {selected_model}")

        with open(file_path, 'rb') as audio_file:
            response = self.client.audio.transcriptions.create(
                model=selected_model,
                file=audio_file,
                response_format="text"
            )

        return response

    def transcribe_chunked(
        self,
        chunk_files: List[str],
        language: Optional[str] = None,
        enable_diarization: bool = False,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Transcribe multiple audio chunks using OpenAI.

        Args:
            chunk_files: List of audio chunk file paths
            language: Language code
            enable_diarization: Enable speaker diarization
            model: Model to use (e.g., 'gpt-4o-mini-transcribe', 'whisper-1')
            **kwargs: Additional options

        Returns:
            Combined transcript
        """
        if not self.is_configured():
            raise ValueError("OpenAI API key not configured")

        # Use default model if none specified
        selected_model = model or self.default_model

        # Validate model
        valid_models = [m['id'] for m in self.available_models]
        if selected_model not in valid_models:
            raise ValueError(f"Invalid model '{selected_model}'. Valid models: {', '.join(valid_models)}")

        transcripts = []

        for i, chunk_file in enumerate(chunk_files):
            print(f"[OpenAI] Transcribing chunk {i+1}/{len(chunk_files)}...")

            with open(chunk_file, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=selected_model,
                    file=audio_file,
                    response_format="text"
                )
                transcripts.append(response)

        # Combine transcripts with paragraph breaks
        return "\n\n".join(transcripts)

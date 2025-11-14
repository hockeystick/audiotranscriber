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
        **kwargs
    ) -> str:
        """
        Transcribe a single audio file using OpenAI.

        Args:
            file_path: Path to audio file
            language: Language code (optional, OpenAI auto-detects)
            enable_diarization: Use gpt-4o-transcribe-diarize model
            **kwargs: Additional options

        Returns:
            Transcript as string
        """
        if not self.is_configured():
            raise ValueError("OpenAI API key not configured")

        # Choose model based on diarization requirement
        # Note: Diarization is currently disabled due to SDK instability
        # model = "gpt-4o-transcribe-diarize" if enable_diarization else "gpt-4o-mini-transcribe"
        model = "gpt-4o-mini-transcribe"  # Stable, reliable model

        print(f"[OpenAI] Transcribing with model: {model}")

        with open(file_path, 'rb') as audio_file:
            response = self.client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                response_format="text"
            )

        return response

    def transcribe_chunked(
        self,
        chunk_files: List[str],
        language: Optional[str] = None,
        enable_diarization: bool = False,
        **kwargs
    ) -> str:
        """
        Transcribe multiple audio chunks using OpenAI.

        Args:
            chunk_files: List of audio chunk file paths
            language: Language code
            enable_diarization: Enable speaker diarization
            **kwargs: Additional options

        Returns:
            Combined transcript
        """
        if not self.is_configured():
            raise ValueError("OpenAI API key not configured")

        model = "gpt-4o-mini-transcribe"
        transcripts = []

        for i, chunk_file in enumerate(chunk_files):
            print(f"[OpenAI] Transcribing chunk {i+1}/{len(chunk_files)}...")

            with open(chunk_file, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    response_format="text"
                )
                transcripts.append(response)

        # Combine transcripts with paragraph breaks
        return "\n\n".join(transcripts)

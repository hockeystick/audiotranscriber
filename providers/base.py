"""
Base Provider Interface
=======================
Abstract base class for transcription providers (OpenAI, Google Cloud, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class TranscriptionProvider(ABC):
    """Abstract base class for all transcription providers"""

    def __init__(self):
        self.name = "Base Provider"
        self.supports_diarization = False
        self.max_file_size = 25 * 1024 * 1024  # 25MB default

    @abstractmethod
    def transcribe(
        self,
        file_path: str,
        language: Optional[str] = None,
        enable_diarization: bool = False,
        **kwargs
    ) -> str:
        """
        Transcribe an audio file.

        Args:
            file_path: Path to the audio file
            language: Language code (e.g., 'en-US', 'auto')
            enable_diarization: Enable speaker identification
            **kwargs: Provider-specific options

        Returns:
            Transcribed text as a string
        """
        pass

    @abstractmethod
    def transcribe_chunked(
        self,
        chunk_files: List[str],
        language: Optional[str] = None,
        enable_diarization: bool = False,
        **kwargs
    ) -> str:
        """
        Transcribe multiple audio chunks and combine results.

        Args:
            chunk_files: List of paths to audio chunk files
            language: Language code
            enable_diarization: Enable speaker identification
            **kwargs: Provider-specific options

        Returns:
            Combined transcript as a string
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """
        Check if the provider is properly configured with credentials.

        Returns:
            True if configured, False otherwise
        """
        pass

    def get_info(self) -> Dict[str, any]:
        """
        Get provider information.

        Returns:
            Dictionary with provider details
        """
        return {
            "name": self.name,
            "supports_diarization": self.supports_diarization,
            "max_file_size": self.max_file_size,
            "configured": self.is_configured()
        }

from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class VideoTask:
    url: str
    extracted: bool = False
    enhanced: bool = False
    filename: Optional[str] = None
    audio_path: Optional[Path] = None
    transcript_path: Optional[Path] = None
    enhanced_path: Optional[Path] = None
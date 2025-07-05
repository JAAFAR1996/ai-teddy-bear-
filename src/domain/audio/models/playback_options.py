from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PlaybackOptions:
    """Options for audio playback."""

    loop: bool = False
    fade_in: float = 0.0
    fade_out: float = 0.0
    volume: Optional[float] = None

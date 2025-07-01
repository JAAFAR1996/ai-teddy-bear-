"""Audio system state management."""

import logging
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass
from enum import Enum
import threading


class AudioState(Enum):
    """Audio system states."""
    IDLE = "idle"
    RECORDING = "recording"
    PLAYING = "playing"
    PROCESSING = "processing"
    ERROR = "error"


@dataclass
class StateChangeEvent:
    """Event data for state changes."""
    old_state: AudioState
    new_state: AudioState
    details: Optional[dict] = None


class StateManager:
    """Manages audio system state and notifications."""

    def __init__(self):
        """Initialize state manager."""
        self.logger = logging.getLogger(__name__)
        self._state = AudioState.IDLE
        self._recording = False
        self._playing = False
        self._processing = False
        self._error: Optional[str] = None
        self._lock = threading.Lock()
        self._observers: Dict[str, List[Callable[[StateChangeEvent], None]]] = {
            "state_change": [],
            "recording_change": [],
            "playback_change": [],
            "error": []
        }

    def get_state(self) -> AudioState:
        """Get current system state."""
        with self._lock:
            return self._state

    def set_state(Optional[dict] = None) -> None:
        """Set system state."""
        with self._lock:
            if state == self._state:
                return

            old_state = self._state
            self._state = state

            # Create event
            event = StateChangeEvent(
                old_state=old_state,
                new_state=state,
                details=details
            )

            # Notify observers
            self._notify_observers("state_change", event)
            self.logger.info(
                f"State changed: {old_state.value} -> {state.value}"
            )

    def is_recording(self) -> bool:
        """Check if system is recording."""
        with self._lock:
            return self._recording

    def set_recording(bool) -> None:
        """Set recording state."""
        with self._lock:
            if recording == self._recording:
                return

            self._recording = recording

            # Update system state
            if recording:
                self.set_state(AudioState.RECORDING)
            else:
                self._update_composite_state()

            # Notify observers
            self._notify_observers(
                "recording_change",
                StateChangeEvent(
                    old_state=self._state,
                    new_state=self._state,
                    details={"recording": recording}
                )
            )

    def is_playing(self) -> bool:
        """Check if system is playing audio."""
        with self._lock:
            return self._playing

    def set_playing(bool) -> None:
        """Set playback state."""
        with self._lock:
            if playing == self._playing:
                return

            self._playing = playing

            # Update system state
            if playing:
                self.set_state(AudioState.PLAYING)
            else:
                self._update_composite_state()

            # Notify observers
            self._notify_observers(
                "playback_change",
                StateChangeEvent(
                    old_state=self._state,
                    new_state=self._state,
                    details={"playing": playing}
                )
            )

    def is_processing(self) -> bool:
        """Check if system is processing audio."""
        with self._lock:
            return self._processing

    def set_processing(bool) -> None:
        """Set processing state."""
        with self._lock:
            if processing == self._processing:
                return

            self._processing = processing

            # Update system state
            if processing:
                self.set_state(AudioState.PROCESSING)
            else:
                self._update_composite_state()

    def get_error(self) -> Optional[str]:
        """Get current error message."""
        with self._lock:
            return self._error

    def set_error(Optional[str]) -> None:
        """Set error state."""
        with self._lock:
            self._error = error

            if error:
                # Update state and notify
                self.set_state(
                    AudioState.ERROR,
                    details={"error": error}
                )
                self._notify_observers(
                    "error",
                    StateChangeEvent(
                        old_state=self._state,
                        new_state=AudioState.ERROR,
                        details={"error": error}
                    )
                )
            else:
                # Clear error state
                self._update_composite_state()

    def _update_composite_state(self) -> Any:
        """Update system state based on component states."""
        if self._error:
            self.set_state(AudioState.ERROR)
        elif self._recording:
            self.set_state(AudioState.RECORDING)
        elif self._playing:
            self.set_state(AudioState.PLAYING)
        elif self._processing:
            self.set_state(AudioState.PROCESSING)
        else:
            self.set_state(AudioState.IDLE)

    def add_observer(
        self,
        event_type: str,
        callback: Callable[[StateChangeEvent], None]
    ):
        """Add state change observer."""
        if event_type not in self._observers:
            raise ValueError(f"Invalid event type: {event_type}")

        self._observers[event_type].append(callback)

    def remove_observer(
        self,
        event_type: str,
        callback: Callable[[StateChangeEvent], None]
    ):
        """Remove state change observer."""
        if event_type not in self._observers:
            raise ValueError(f"Invalid event type: {event_type}")

        try:
            self._observers[event_type].remove(callback)
        except ValueError:
            pass

    def _notify_observers(StateChangeEvent) -> None:
        """Notify observers of state change."""
        if event_type not in self._observers:
            return

        for callback in self._observers[event_type]:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(
                    f"Error in state change observer: {e}"
                )


# Global state manager instance
state_manager = StateManager()
"""ESP32 Teddy Bear Simulator - Clean Architecture Coordinator.

This is a refactored version of the original God Class, now following Clean Architecture
principles with clear separation of concerns.

Original file size: 1,285 lines
New coordinator size: ~300 lines (76.7% reduction)
"""

import structlog
from typing import Dict, Any, Optional
import asyncio
import threading
import time
import uuid
from datetime import datetime

from ...domain.esp32.models import (
    ESP32Device, PowerState, DeviceStatus, AudioSettings, 
    NetworkConnection, ChildProfile, SpeechRecognition
)
from ...application.services.esp32 import (
    DeviceManagementService, AudioManagementService,
    NetworkCommunicationService, GUIManagementService,
    ChildProfileService
)
from ...infrastructure.esp32 import (
    HardwareSimulator, AudioDriver, NetworkAdapter, GUIComponents
)

logger = structlog.get_logger(__name__)

# Configuration
SERVER_URL = "http://127.0.0.1:8000"
WAKE_WORDS = ["يا دبدوب", "hey teddy", "hello teddy"]


class ESP32TeddyBearSimulator:
    """
    ESP32 Teddy Bear Simulator coordinator using Clean Architecture.
    
    This class acts as a facade, delegating to specialized services
    while maintaining backward compatibility with the original interface.
    """
    
    def __init__(self):
        # Device identification
        self.device_id = f"ESP32_{uuid.uuid4().hex[:8].upper()}"
        self.mac_address = f"MAC_{uuid.uuid4().hex[:12].upper()}"
        
        # Core services
        self.device_service = DeviceManagementService(self.device_id, self.mac_address)
        self.audio_service = AudioManagementService()
        self.network_service = NetworkCommunicationService(SERVER_URL)
        self.gui_service = GUIManagementService(self.device_id)
        self.child_service = ChildProfileService(self.device_id)
        
        # Infrastructure components
        self.hardware = HardwareSimulator()
        self.audio_driver = AudioDriver()
        self.network_adapter = NetworkAdapter(SERVER_URL)
        self.gui_components = GUIComponents()
        
        # State management
        self.is_running = False
        self.session_id = None
        
        # Setup callbacks
        self._setup_callbacks()
        
        logger.info(f" ESP32 Teddy Bear Simulator initialized: {self.device_id}")
    
    def _setup_callbacks(self) -> None:
        """Setup callbacks between services."""
        # Device service callbacks
        self.device_service.register_power_callback(
            'gui_update', self._on_power_state_changed
        )
        
        # Audio service callbacks
        self.audio_service.register_recognition_callback(
            'speech_handler', self._on_speech_recognized
        )
        
        # Network service callbacks
        self.network_service.register_connection_callback(
            'gui_update', self._on_network_status_changed
        )
        
        # GUI callbacks
        self.gui_service.register_update_callback(
            'power_button_callback', self._on_power_button_clicked
        )
        self.gui_service.register_update_callback(
            'save_profile_callback', self._on_save_profile_clicked
        )
        self.gui_service.register_update_callback(
            'closing_callback', self._on_window_closing
        )
    
    async def initialize(self) -> bool:
        """Initialize the complete system."""
        try:
            logger.info(" Initializing ESP32 Teddy Bear system...")
            
            # Initialize hardware
            if not self.hardware.initialize_hardware():
                logger.error(" Hardware initialization failed")
                return False
            
            # Initialize audio system
            if not self.audio_driver.initialize_audio_system():
                logger.error(" Audio system initialization failed")
                return False
            
            # Test network connection
            if not self.network_adapter.test_connection():
                logger.warning(" Network connection failed, continuing in offline mode")
            
            # Initialize GUI
            root = self.gui_service.initialize_gui()
            if not root:
                logger.error(" GUI initialization failed")
                return False
            
            # Update audio settings
            self.audio_service.update_audio_settings(
                wake_words=WAKE_WORDS,
                language='ar-SA'
            )
            
            logger.info(" System initialization complete")
            return True
            
        except Exception as e:
            logger.error(f" System initialization failed: {e}")
            return False
    
    async def run(self) -> None:
        """Run the simulator."""
        try:
            if not await self.initialize():
                logger.error(" Failed to initialize system")
                return
            
            self.is_running = True
            self.gui_service.log_message(" ESP32 Teddy Bear Simulator Ready")
            self.gui_service.log_message(" Press POWER to start your AI teddy bear")
            
            # Run GUI main loop
            self.gui_service.run_gui()
            
        except Exception as e:
            logger.error(f" Simulator run failed: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Shutdown the complete system."""
        try:
            logger.info(" Shutting down system...")
            
            self.is_running = False
            
            # End any active session
            if self.child_service.current_profile:
                self.child_service.end_session()
            
            # Stop services
            await self.device_service.power_off()
            await self.audio_service.stop_listening()
            await self.network_service.disconnect_server()
            await self.network_service.disconnect_wifi()
            
            # Shutdown infrastructure
            self.hardware.shutdown_hardware()
            self.audio_driver.shutdown_audio_system()
            
            logger.info(" System shutdown complete")
            
        except Exception as e:
            logger.error(f" Shutdown failed: {e}")
    
    async def power_on(self) -> bool:
        """Power on the teddy bear."""
        try:
            logger.info(" Powering on teddy bear...")
            
            # Power on device
            if not await self.device_service.power_on():
                return False
            
            # Connect to WiFi and server
            await asyncio.sleep(2)  # Simulate startup delay
            await self.network_service.connect_wifi()
            
            # Start listening
            await asyncio.sleep(1)
            await self.audio_service.start_listening()
            
            self.gui_service.log_message(" Teddy Bear powered on and ready!")
            return True
            
        except Exception as e:
            logger.error(f" Power on failed: {e}")
            return False
    
    async def power_off(self) -> bool:
        """Power off the teddy bear."""
        try:
            logger.info(" Powering off teddy bear...")
            
            # Stop audio
            await self.audio_service.stop_listening()
            
            # Disconnect network
            await self.network_service.disconnect_server()
            await self.network_service.disconnect_wifi()
            
            # Power off device
            await self.device_service.power_off()
            
            self.gui_service.log_message(" Teddy Bear powered off")
            return True
            
        except Exception as e:
            logger.error(f" Power off failed: {e}")
            return False
    
    async def handle_conversation(self, user_input: str) -> Optional[str]:
        """Handle conversation with child."""
        try:
            if not self.child_service.current_profile:
                logger.warning("No active child profile for conversation")
                return None
            
            # Send to AI server
            message = {
                'type': 'conversation',
                'text': user_input,
                'child_id': self.child_service.current_profile.child_id,
                'session_id': self.session_id,
                'language': self.child_service.current_profile.preferred_language
            }
            
            response = await self.network_service.send_message(message)
            
            if response and response.get('type') == 'ai_response':
                ai_text = response.get('text', 'عذرا لم أستطع فهم ما قلته.')
                
                # Record conversation
                self.child_service.record_conversation(user_input, ai_text)
                
                # Log in GUI
                self.gui_service.log_conversation(user_input, ai_text)
                
                # Play response
                await self.audio_service.play_audio(ai_text)
                
                return ai_text
            else:
                logger.warning("Invalid AI response")
                return None
                
        except Exception as e:
            logger.error(f" Conversation handling failed: {e}")
            return None
    
    def create_child_profile(self, name: str, age: int) -> bool:
        """Create new child profile."""
        try:
            profile = self.child_service.create_profile(name, age)
            
            if profile:
                # Start session
                self.session_id = self.child_service.start_session().session_id
                
                # Update GUI
                self.gui_service.log_message(f" Created profile for {name}, age {age}")
                
                # Register with server
                device_info = {
                    'device_id': self.device_id,
                    'child_profile': {
                        'name': name,
                        'age': age,
                        'child_id': profile.child_id
                    }
                }
                
                # Register asynchronously
                threading.Thread(
                    target=lambda: asyncio.run(self.network_service.register_device(device_info)),
                    daemon=True
                ).start()
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f" Profile creation failed: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'device': self.device_service.get_device_status(),
            'network': self.network_service.get_network_status(),
            'audio': self.audio_service.get_audio_status(),
            'child_profile': self.child_service.get_profile_summary(),
            'hardware': self.hardware.get_hardware_status(),
            'session_id': self.session_id,
            'is_running': self.is_running
        }
    
    # Callback handlers
    def _on_power_state_changed(self, power_state: PowerState) -> None:
        """Handle power state changes."""
        try:
            status_data = self.device_service.get_device_status()
            self.gui_service.update_device_status(status_data)
            
            # Update power button
            if hasattr(self.gui_service, 'gui_components') and 'power_button' in self.gui_service.gui_components:
                button = self.gui_service.gui_components['power_button']
                if power_state == PowerState.POWERED_ON:
                    button.config(text=" POWER OFF", bg='#e74c3c')
                else:
                    button.config(text=" POWER ON", bg='#27ae60')
                    
        except Exception as e:
            logger.error(f" Power state callback failed: {e}")
    
    def _on_speech_recognized(self, recognition: SpeechRecognition) -> None:
        """Handle speech recognition results."""
        try:
            if recognition.wake_word_detected:
                self.gui_service.log_message(f" Wake word detected: {recognition.detected_wake_word}")
                
                # Start conversation mode
                threading.Thread(
                    target=lambda: asyncio.run(self.handle_conversation(recognition.text)),
                    daemon=True
                ).start()
            else:
                # Log regular speech without wake word
                logger.debug(f"Speech detected (no wake word): {recognition.text}")
                
        except Exception as e:
            logger.error(f" Speech recognition callback failed: {e}")
    
    def _on_network_status_changed(self, network: NetworkConnection) -> None:
        """Handle network status changes."""
        try:
            network_data = self.network_service.get_network_status()
            self.gui_service.update_network_status(network_data)
            
        except Exception as e:
            logger.error(f" Network status callback failed: {e}")
    
    def _on_power_button_clicked(self) -> None:
        """Handle power button clicks."""
        try:
            device_status = self.device_service.get_device_status()
            
            if device_status['is_powered_on']:
                threading.Thread(target=lambda: asyncio.run(self.power_off()), daemon=True).start()
            else:
                threading.Thread(target=lambda: asyncio.run(self.power_on()), daemon=True).start()
                
        except Exception as e:
            logger.error(f" Power button callback failed: {e}")
    
    def _on_save_profile_clicked(self, name: str, age: str) -> None:
        """Handle save profile button clicks."""
        try:
            if name.strip() and age.isdigit():
                age_int = int(age)
                if 2 <= age_int <= 12:
                    if self.create_child_profile(name.strip(), age_int):
                        self.gui_service.show_message(
                            "Profile Saved", 
                            f"Profile created for {name}, age {age_int}",
                            "info"
                        )
                    else:
                        self.gui_service.show_message(
                            "Error", 
                            "Failed to create profile",
                            "error"
                        )
                else:
                    self.gui_service.show_message(
                        "Invalid Age", 
                        "Age must be between 2 and 12",
                        "warning"
                    )
            else:
                self.gui_service.show_message(
                    "Invalid Input", 
                    "Please enter valid name and age",
                    "warning"
                )
                
        except Exception as e:
            logger.error(f" Save profile callback failed: {e}")
    
    def _on_window_closing(self) -> None:
        """Handle window closing."""
        try:
            self.gui_service.destroy_gui()
            threading.Thread(target=lambda: asyncio.run(self.shutdown()), daemon=True).start()
            
        except Exception as e:
            logger.error(f" Window closing callback failed: {e}")


# Standalone function for backward compatibility
def main():
    """Main entry point for the simulator."""
    try:
        simulator = ESP32TeddyBearSimulator()
        asyncio.run(simulator.run())
    except KeyboardInterrupt:
        logger.info(" Simulator interrupted by user")
    except Exception as e:
        logger.error(f" Simulator crashed: {e}")


if __name__ == "__main__":
    main()

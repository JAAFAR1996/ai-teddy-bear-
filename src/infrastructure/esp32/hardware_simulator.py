"""Hardware simulation for ESP32 teddy bear."""

import random
import threading
import time
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


class HardwareSimulator:
    """Simulates ESP32 hardware components."""

    def __init__(self):
        self.is_initialized = False
        self.power_consumption = 0.0  # mW
        self.temperature = 25.0  # Celsius
        self.battery_level = 100.0  # Percentage
        self.led_states = {"red": False, "green": False, "blue": False}
        self.button_states = {"power": False, "wake": False}
        self.monitoring_active = False
        self.monitor_thread = None

        logger.info(" Hardware simulator initialized")

    def initialize_hardware(self) -> bool:
        """Initialize hardware components."""
        try:
            logger.info(" Initializing hardware components...")

            # Simulate hardware initialization delays
            time.sleep(0.5)

            # Initialize GPIO pins
            self._initialize_gpio()

            # Initialize I2C/SPI buses
            self._initialize_buses()

            # Initialize audio hardware
            self._initialize_audio_hardware()

            self.is_initialized = True
            self.power_consumption = 150.0  # Base consumption

            logger.info(" Hardware initialization complete")
            return True

        except Exception as e:
            logger.error(f" Hardware initialization failed: {e}")
            return False

    def shutdown_hardware(self) -> None:
        """Shutdown hardware components."""
        try:
            logger.info(" Shutting down hardware...")

            # Turn off all LEDs
            self.set_led("red", False)
            self.set_led("green", False)
            self.set_led("blue", False)

            # Reset states
            self.power_consumption = 0.0
            self.is_initialized = False

            logger.info(" Hardware shutdown complete")

        except Exception as e:
            logger.error(f" Hardware shutdown failed: {e}")

    def set_led(self, color: str, state: bool) -> bool:
        """Control LED state."""
        try:
            if color in self.led_states:
                self.led_states[color] = state

                # Update power consumption
                if state:
                    self.power_consumption += 5.0  # 5mW per LED
                else:
                    self.power_consumption = max(0, self.power_consumption - 5.0)

                logger.debug(f" LED {color}: {'ON' if state else 'OFF'}")
                return True
            else:
                logger.error(f"Invalid LED color: {color}")
                return False

        except Exception as e:
            logger.error(f" LED control failed: {e}")
            return False

    def read_button(self, button: str) -> bool:
        """Read button state."""
        try:
            if button in self.button_states:
                # Simulate random button presses for testing
                if random.random() < 0.01:  # 1% chance per read
                    self.button_states[button] = not self.button_states[button]

                return self.button_states[button]
            else:
                logger.error(f"Invalid button: {button}")
                return False

        except Exception as e:
            logger.error(f" Button read failed: {e}")
            return False

    def get_temperature(self) -> float:
        """Get device temperature."""
        try:
            # Simulate temperature changes based on power consumption
            base_temp = 25.0
            temp_increase = (self.power_consumption / 1000.0) * 10  # 10C per W
            self.temperature = base_temp + temp_increase + random.uniform(-2, 2)

            return self.temperature

        except Exception as e:
            logger.error(f" Temperature read failed: {e}")
            return 25.0

    def get_battery_level(self) -> float:
        """Get battery level percentage."""
        try:
            # Simulate battery drain based on power consumption
            if self.power_consumption > 0:
                drain_rate = self.power_consumption / 10000.0  # Simplified calculation
                self.battery_level = max(0, self.battery_level - drain_rate)

            return self.battery_level

        except Exception as e:
            logger.error(f" Battery read failed: {e}")
            return 100.0

    def get_wifi_signal_strength(self) -> int:
        """Simulate WiFi signal strength."""
        try:
            # Simulate varying signal strength
            base_strength = 75
            variation = random.randint(-15, 15)
            strength = max(0, min(100, base_strength + variation))

            return strength

        except Exception as e:
            logger.error(f" WiFi signal read failed: {e}")
            return 0

    def start_monitoring(self) -> None:
        """Start hardware monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_hardware, daemon=True
            )
            self.monitor_thread.start()
            logger.info(" Hardware monitoring started")

    def stop_monitoring(self) -> None:
        """Stop hardware monitoring."""
        if self.monitoring_active:
            self.monitoring_active = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2)
            logger.info(" Hardware monitoring stopped")

    def get_hardware_status(self) -> Dict[str, Any]:
        """Get comprehensive hardware status."""
        return {
            "is_initialized": self.is_initialized,
            "power_consumption_mw": self.power_consumption,
            "temperature_celsius": self.get_temperature(),
            "battery_percentage": self.get_battery_level(),
            "led_states": self.led_states.copy(),
            "button_states": self.button_states.copy(),
            "wifi_signal_strength": self.get_wifi_signal_strength(),
            "monitoring_active": self.monitoring_active,
        }

    def simulate_button_press(self, button: str) -> bool:
        """Simulate button press for testing."""
        try:
            if button in self.button_states:
                self.button_states[button] = True
                logger.info(f" Button pressed: {button}")

                # Auto-release after short time
                threading.Timer(0.1, lambda: self._release_button(button)).start()
                return True
            else:
                logger.error(f"Invalid button: {button}")
                return False

        except Exception as e:
            logger.error(f" Button simulation failed: {e}")
            return False

    def _initialize_gpio(self) -> None:
        """Initialize GPIO pins."""
        logger.debug(" Initializing GPIO pins...")
        time.sleep(0.1)

    def _initialize_buses(self) -> None:
        """Initialize communication buses."""
        logger.debug(" Initializing I2C/SPI buses...")
        time.sleep(0.1)

    def _initialize_audio_hardware(self) -> None:
        """Initialize audio hardware components."""
        logger.debug(" Initializing audio hardware...")
        time.sleep(0.1)

    def _monitor_hardware(self) -> None:
        """Monitor hardware health and status."""
        while self.monitoring_active:
            try:
                # Check temperature
                temp = self.get_temperature()
                if temp > 60:
                    logger.warning(f" High temperature: {temp:.1f}C")

                # Check battery
                battery = self.get_battery_level()
                if battery < 20:
                    logger.warning(f" Low battery: {battery:.1f}%")
                elif battery < 5:
                    logger.error(f" Critical battery: {battery:.1f}%")

                # Check power consumption
                if self.power_consumption > 500:
                    logger.warning(
                        f" High power consumption: {self.power_consumption:.1f}mW"
                    )

                time.sleep(5)  # Monitor every 5 seconds

            except Exception as e:
                logger.error(f" Hardware monitor error: {e}")
                time.sleep(10)

    def _release_button(self, button: str) -> None:
        """Release button after press."""
        if button in self.button_states:
            self.button_states[button] = False
            logger.debug(f" Button released: {button}")

    def __del__(self):
        """Cleanup on destruction."""
        self.stop_monitoring()
        if self.is_initialized:
            self.shutdown_hardware()

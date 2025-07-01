from typing import Any

#!/usr/bin/env python3
"""
🧸 ESP32 Simulator Launcher
Simple script to run the ESP32 simulator independently
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main() -> Any:
    """Run the ESP32 simulator"""
    try:
        # Ensure we're in the right directory
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))

        # Import and run simulator
        from core.simulators.esp32_production_simulator import \
            main as simulator_main

        logging.info("🧸 Starting ESP32 Simulator...")
        simulator_main()

    except ImportError as e:
        logging.error(f"Failed to import simulator: {e}")
        logging.info("Make sure PySide6 is installed: pip install PySide6")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Simulator error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

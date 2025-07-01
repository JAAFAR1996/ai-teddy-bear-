from typing import Any

"""
Waveform Visualization Widget for AI Teddy Bear
Real-time audio waveform display with smooth rendering
"""

import numpy as np
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class WaveformWidget(QWidget):
    """Real-time waveform visualization widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = np.array([])
        self.setMinimumHeight(100)

    def update_data(self, data) -> Any:
        """Update waveform data and trigger repaint"""
        if isinstance(data, (list, np.ndarray)):
            self.data = np.array(data)
            self.update()

    def paintEvent(self, event) -> Any:
        """Custom paint event for waveform rendering"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set background
        painter.fillRect(self.rect(), QColor(40, 44, 52))

        if len(self.data) == 0:
            return

        # Draw waveform
        width = self.width()
        height = self.height()
        center_y = height // 2

        # Prepare pen for waveform
        pen = QPen(QColor(0, 255, 127), 2)
        painter.setPen(pen)

        # Calculate step size for data points
        if len(self.data) > width:
            step = len(self.data) // width
            sampled_data = self.data[::step]
        else:
            sampled_data = self.data

        # Draw waveform line
        if len(sampled_data) > 1:
            x_step = width / len(sampled_data)

            for i in range(len(sampled_data) - 1):
                x1 = int(i * x_step)
                x2 = int((i + 1) * x_step)

                # Normalize amplitude to widget height
                y1 = center_y - int(sampled_data[i] * center_y * 0.8)
                y2 = center_y - int(sampled_data[i + 1] * center_y * 0.8)

                painter.drawLine(x1, y1, x2, y2)

        # Draw center line
        center_pen = QPen(QColor(100, 100, 100), 1)
        painter.setPen(center_pen)
        painter.drawLine(0, center_y, width, center_y)

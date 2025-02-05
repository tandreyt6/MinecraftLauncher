from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QFontMetrics, QFont, QColor
from PyQt6.QtWidgets import *


class SliderTicksLables(QWidget):
    """Slider with labels (instead of tick marks) along each available position"""

    def __init__(self, parent=None):
        super(SliderTicksLables, self).__init__(parent)
        self.isLeftOffest = True
        self.isRightOffest = True
        self.dlsText = ""
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.v = QVBoxLayout(self)
        self.v.addStretch()
        self.v.addWidget(self.slider)
        self.setFixedHeight(70)
        self.heightTextOffest = -10
        self.setRange(1000, 10000)

    def setRange(self, min: int, max: int, values: int=10) -> None:
        self.slider.setRange(min, max)
        self.slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.slider.setTickInterval((max-min)//values)

    def paintEvent(self, event):
        super().paintEvent(event)

        rect = self.slider.geometry()
        painter = QPainter(self)
        painter.setPen(QPen(QColor("#a1d68b")))

        font_metrics = QFontMetrics(self.slider.font())
        style_option = QStyleOptionSlider()
        self.slider.initStyleOption(style_option)

        available = self.slider.style().pixelMetric(QStyle.PixelMetric.PM_SliderSpaceAvailable, style_option, self.slider)
        fudge = self.slider.style().pixelMetric(QStyle.PixelMetric.PM_SliderLength, style_option, self.slider) // 2
        values = [_ for _ in range(self.slider.minimum(), self.slider.maximum()+1, self.slider.tickInterval())]
        for value in values:
            index = value
            value = str(value)+self.dlsText
            pos = self.slider.style().sliderPositionFromValue(self.slider.minimum(), self.slider.maximum(), index, available)
            pos += fudge
            pos = self.slider.mapToParent(QPoint(pos, 0)).x()
            if index == values[0] and self.isLeftOffest:
                painter.drawText(QPoint(pos, rect.height() + self.heightTextOffest), value)
            elif index == values[-1] and self.isRightOffest:
                label_width = font_metrics.boundingRect(value).width()
                painter.drawText(QPoint(pos - label_width, rect.height() + self.heightTextOffest), value)
            else:
                label_width = font_metrics.boundingRect(value).width()
                painter.drawText(QPoint(pos - label_width // 2, rect.height() + self.heightTextOffest), value)



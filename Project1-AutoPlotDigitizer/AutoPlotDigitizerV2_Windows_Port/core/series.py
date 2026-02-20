from PySide6.QtGui import QColor
import csv

class Series:
    def __init__(self, name: str, color: QColor = None):
        self.name = name
        self.color = color if color else QColor(255, 0, 0)
        self.raw_pixels = [] # List of (x, y) tuples
        self.data_points = [] # List of (x, y) tuples (scaled)
        self.line_type = 'auto' # 'auto', 'manual', 'solid'
        self.gap_fill = 3

    def set_data(self, pixels, data_points):
        self.raw_pixels = pixels
        self.data_points = data_points

    def __repr__(self):
        return f"<Series '{self.name}' ({len(self.data_points)} points)>"

    def to_dict(self):
        return {
            'name': self.name,
            'color': self.color.name(),
            'raw_pixels': self.raw_pixels,
            'data_points': self.data_points,
            'line_type': self.line_type,
            'gap_fill': self.gap_fill
        }

    @classmethod
    def from_dict(cls, data):
        series = cls(data['name'], QColor(data['color']))
        series.raw_pixels = data['raw_pixels']
        series.data_points = data['data_points']
        series.line_type = data.get('line_type', 'auto')
        series.gap_fill = data.get('gap_fill', 3)
        return series

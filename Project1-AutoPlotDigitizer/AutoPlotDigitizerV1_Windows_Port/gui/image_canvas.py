from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsEllipseItem, QGraphicsPathItem
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QImage, QPainterPath
from PySide6.QtCore import Qt, QPointF, Signal

class ImageCanvas(QGraphicsView):
    # Signals to notify MainWindow
    calibration_point_added = Signal(int, float, float) # index, x, y
    
    MODE_VIEW = 0
    MODE_CALIBRATE = 1
    MODE_MASK = 2

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.viewport().setMouseTracking(True)
        
        self.image_item = None
        self.current_image = None
        
        # State
        self.mode = self.MODE_VIEW
        self.zoom_factor = 1.15
        
        # Calibration
        self.calibration_points = [] # List of QGraphicsEllipseItem
        
        # Masking
        self.mask_layer = QGraphicsScene() 
        self.drawing_path = None
        self.current_path_item = None
        self.pen_size = 20
        self.mask_items = []
        
        # Extracted Points
        self.extracted_point_items = []

    def set_mode(self, mode):
        self.mode = mode
        if mode == self.MODE_VIEW:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.OpenHandCursor)
        elif mode == self.MODE_CALIBRATE:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.CrossCursor)
        elif mode == self.MODE_MASK:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.ArrowCursor) 

    def load_image(self, file_path):
        self.current_image = QPixmap(file_path)
        self.scene.clear()
        self.calibration_points = []
        self.mask_items = []
        self.extracted_point_items = []
        
        self.image_item = self.scene.addPixmap(self.current_image)
        self.image_item.setZValue(0)
        self.setSceneRect(self.image_item.boundingRect())
        self.fitInView(self.image_item, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            # Zoom
            if event.angleDelta().y() > 0:
                self.scale(self.zoom_factor, self.zoom_factor)
            else:
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if self.image_item is None:
            return

        sp = self.mapToScene(event.pos())
        
        if self.mode == self.MODE_CALIBRATE:
            if event.button() == Qt.LeftButton:
                if len(self.calibration_points) < 4:
                    self.add_calibration_point(sp)
        
        elif self.mode == self.MODE_MASK:
            if event.button() == Qt.LeftButton:
                self.start_drawing(sp)
                
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        sp = self.mapToScene(event.pos())
        
        if self.mode == self.MODE_MASK and self.drawing_path:
            self.continue_drawing(sp)
            
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.mode == self.MODE_MASK and self.drawing_path:
            self.finish_drawing()
            
        super().mouseReleaseEvent(event)

    def add_calibration_point(self, pos):
        idx = len(self.calibration_points)
        colors = [Qt.red, Qt.red, Qt.blue, Qt.blue] # X1, X2, Y1, Y2
        
        marker = QGraphicsEllipseItem(pos.x()-5, pos.y()-5, 10, 10)
        marker.setBrush(colors[idx])
        marker.setPen(QPen(Qt.white, 2))
        marker.setZValue(10)
        self.scene.addItem(marker)
        self.calibration_points.append(marker)
        
        self.calibration_point_added.emit(idx, pos.x(), pos.y())

    def restore_calibration_points(self, points):
        """Restores calibration points from list of (x, y) tuples."""
        # Clear existing
        for item in self.calibration_points:
            self.scene.removeItem(item)
        self.calibration_points = []
        
        colors = [Qt.red, Qt.red, Qt.blue, Qt.blue] # X1, X2, Y1, Y2
        for idx, (x, y) in enumerate(points):
            if idx >= 4: break
            marker = QGraphicsEllipseItem(x-5, y-5, 10, 10)
            marker.setBrush(colors[idx])
            marker.setPen(QPen(Qt.white, 2))
            marker.setZValue(10)
            self.scene.addItem(marker)
            self.calibration_points.append(marker)

    def start_drawing(self, pos):
        self.drawing_path = QPainterPath(pos)
        pen = QPen(QColor(255, 255, 0, 100), self.pen_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        self.current_path_item = QGraphicsPathItem()
        self.current_path_item.setPen(pen)
        self.current_path_item.setZValue(5)
        self.scene.addItem(self.current_path_item)

    def continue_drawing(self, pos):
        self.drawing_path.lineTo(pos)
        self.current_path_item.setPath(self.drawing_path)

    def finish_drawing(self):
        self.mask_items.append(self.current_path_item)
        self.drawing_path = None
        self.current_path_item = None

    def get_mask_image(self):
        """Renders the mask items to a black and white QImage matching the original image size."""
        if self.image_item is None:
            return None
            
        rect = self.image_item.boundingRect()
        width = int(rect.width())
        height = int(rect.height())
        
        image = QImage(width, height, QImage.Format_Grayscale8)
        image.fill(Qt.black)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Simple approach: Draw the paths directly
        pen = QPen(Qt.white, self.pen_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        for item in self.mask_items:
            painter.drawPath(item.path())
            
        painter.end()
        return image

    def clear_mask(self):
        """Clears all drawn mask items from the scene."""
        for item in self.mask_items:
            self.scene.removeItem(item)
        self.mask_items = []
        self.drawing_path = None
        if self.current_path_item:
            self.scene.removeItem(self.current_path_item)
            self.current_path_item = None

    def draw_extracted_points(self, points, color=Qt.green):
        """Draws extracted points (pixels) on the scene."""
        pen = QPen(color, 2)
        radius = 2
        
        for x, y in points:
            item = self.scene.addEllipse(x-radius, y-radius, radius*2, radius*2, pen, color)
            item.setZValue(8) # Below calibration (10) but above mask (5)
            self.extracted_point_items.append(item)

    def clear_extracted_points(self):
        """Clears all extracted point items from the scene."""
        for item in self.extracted_point_items:
            # Check if item is still in scene (might be cleared by scene.clear())
            if item.scene() == self.scene:
                self.scene.removeItem(item)
        self.extracted_point_items = []

    def undo_last_mask(self):
        """Removes the last drawn mask path from the scene."""
        if self.mask_items:
            item = self.mask_items.pop()
            if item.scene() == self.scene:
                self.scene.removeItem(item)


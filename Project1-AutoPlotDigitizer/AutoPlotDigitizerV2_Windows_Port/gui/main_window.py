from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QGroupBox, QLineEdit, QFormLayout,
                               QRadioButton, QButtonGroup, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                               QColorDialog, QComboBox, QSlider, QCheckBox)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QColor
from gui.image_canvas import ImageCanvas
from core.project import Project
from core.series import Series
from core.processor import ImageProcessor
import cv2
import numpy as np
import csv

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoPlotDigitizer V2")
        self.resize(1400, 800)
        
        # Initialize Core Project Model
        self.project_model = Project()
        self.project_model.add_observer(self.on_project_updated)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Menu Bar
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")
        
        action_open_img = file_menu.addAction("Open Image")
        action_open_img.triggered.connect(self.load_image)
        
        file_menu.addSeparator()
        
        action_save_proj = file_menu.addAction("Save Project")
        action_save_proj.triggered.connect(self.save_project_ui)
        
        action_load_proj = file_menu.addAction("Open Project")
        action_load_proj.triggered.connect(self.load_project_ui)

        # Main Layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left Panel (Controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(350)
        
        # 1. Load Image
        gb_load = QGroupBox("1. Load Image")
        load_layout = QVBoxLayout()
        self.btn_load = QPushButton("Load Image")
        self.btn_load.clicked.connect(self.load_image)
        self.lbl_status = QLabel("No Image Loaded")
        load_layout.addWidget(self.btn_load)
        load_layout.addWidget(self.lbl_status)
        gb_load.setLayout(load_layout)
        
        # 2. Calibration
        gb_calib = QGroupBox("2. Calibration")
        calib_layout = QVBoxLayout()
        
        self.btn_calib_mode = QPushButton("Set Calibration Points (0/4)")
        self.btn_calib_mode.setCheckable(True)
        self.btn_calib_mode.clicked.connect(self.toggle_calibration_mode)
        
        form_calib = QFormLayout()
        self.inp_x1 = QLineEdit("0")
        self.inp_x2 = QLineEdit("10")
        self.inp_y1 = QLineEdit("0")
        self.inp_y2 = QLineEdit("100")
        
        self.chk_log_x = QCheckBox("Log Scale X")
        self.chk_log_y = QCheckBox("Log Scale Y")
        self.chk_perspective = QCheckBox("Perspective Mode (Click TL->TR->BR->BL)")
        self.chk_perspective.toggled.connect(self.update_calib_instructions)
        
        form_calib.addRow("X1 Value:", self.inp_x1)
        form_calib.addRow("X2 Value:", self.inp_x2)
        form_calib.addRow("Y1 Value:", self.inp_y1)
        form_calib.addRow("Y2 Value:", self.inp_y2)
        form_calib.addRow("", self.chk_log_x)
        form_calib.addRow(self.chk_log_x)
        form_calib.addRow(self.chk_log_y)
        form_calib.addRow(self.chk_perspective)
        
        calib_layout.addWidget(self.btn_calib_mode)
        calib_layout.addLayout(form_calib)
        gb_calib.setLayout(calib_layout)
        
        # 3. Masking & Color
        gb_mask = QGroupBox("3. Extraction Mask & Color")
        mask_layout = QVBoxLayout()
        self.btn_mask_mode = QPushButton("Draw Mask (Pen)")
        self.btn_mask_mode.setCheckable(True)
        self.btn_mask_mode.clicked.connect(self.toggle_mask_mode)
        
        self.btn_color = QPushButton("Pick Target Color (Default: Dark)")
        self.btn_color.clicked.connect(self.pick_color)
        self.target_color_hsv = None # None means dark
        self.current_series_color = Qt.red # Default color for new series visualization
        
        mask_layout.addWidget(self.btn_mask_mode)
        mask_layout.addWidget(self.btn_color)
        
        mask_layout.addWidget(QLabel("Pattern Mode:"))
        self.combo_pattern = QComboBox()
        self.combo_pattern.addItems(["Auto-Detect Pattern (Default)", "Manual Gap Fill", "Solid Line"])
        self.combo_pattern.currentIndexChanged.connect(self.toggle_gap_slider)
        mask_layout.addWidget(self.combo_pattern)
        
        # Gap Fill Slider (Hidden by default)
        self.lbl_gap = QLabel("Gap Fill: 3px")
        self.slider_gap = QSlider(Qt.Horizontal)
        self.slider_gap.setRange(1, 20)
        self.slider_gap.setValue(3)
        self.slider_gap.valueChanged.connect(self.update_gap_label)
        
        self.container_gap = QWidget()
        gap_layout = QVBoxLayout(self.container_gap)
        gap_layout.addWidget(self.lbl_gap)
        gap_layout.addWidget(self.slider_gap)
        gap_layout.setContentsMargins(0,0,0,0)
        
        mask_layout.addWidget(self.container_gap)
        self.container_gap.setVisible(False)
        
        mask_btn_layout = QHBoxLayout()
        self.btn_undo_mask = QPushButton("Undo Stroke")
        self.btn_undo_mask.clicked.connect(self.undo_mask)
        
        self.btn_clear_mask = QPushButton("Clear/Delete Mask")
        self.btn_clear_mask.clicked.connect(self.clear_mask)
        
        mask_btn_layout.addWidget(self.btn_undo_mask)
        mask_btn_layout.addWidget(self.btn_clear_mask)
        mask_layout.addLayout(mask_btn_layout)
        
        gb_mask.setLayout(mask_layout)
        
        # 4. Extract
        gb_extract = QGroupBox("4. Add Series")
        extract_layout = QVBoxLayout()
        self.btn_extract = QPushButton("Extract & Add Series")
        self.btn_extract.clicked.connect(self.extract_data)
        
        self.inp_series_name = QLineEdit("Series 1")
        
        extract_layout.addWidget(QLabel("Series Name:"))
        extract_layout.addWidget(self.inp_series_name)
        extract_layout.addWidget(self.btn_extract)
        gb_extract.setLayout(extract_layout)
        
        # 5. Series List & Export
        gb_series = QGroupBox("5. Extracted Series")
        series_layout = QVBoxLayout()
        self.table = QTableWidget() 
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Color", "Points"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        self.btn_export = QPushButton("Export All to CSV")
        self.btn_export.clicked.connect(self.export_csv)
        self.btn_export.setEnabled(False)
        
        self.btn_clear_series = QPushButton("Clear All Series")
        self.btn_clear_series.clicked.connect(self.clear_all_series)
        
        self.btn_delete_series = QPushButton("Delete Selected Series")
        self.btn_delete_series.clicked.connect(self.delete_selected_series)
        
        series_layout.addWidget(self.table)
        series_layout.addWidget(self.btn_delete_series)
        series_layout.addWidget(self.btn_clear_series)
        series_layout.addWidget(self.btn_export)
        gb_series.setLayout(series_layout)

        # Add all to left panel
        left_layout.addWidget(gb_load)
        left_layout.addWidget(gb_calib)
        left_layout.addWidget(gb_mask)
        left_layout.addWidget(gb_extract)
        left_layout.addWidget(gb_series)
        
        # Center (Canvas)
        self.canvas = ImageCanvas()
        self.canvas.calibration_point_added.connect(self.on_calibration_point_added)
        
        # Add to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.canvas)
        
        # Mode Group
        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.btn_calib_mode)
        self.mode_group.addButton(self.btn_mask_mode)
        self.mode_group.setExclusive(True)
        
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.project_model.set_image(file_path)
            self.canvas.load_image(file_path)
            self.lbl_status.setText(f"Loaded: {file_path.split('/')[-1]}")
            
            # Reset UI state (Calibration/Mask modes) 
            self.reset_ui_modes()

    def reset_ui_modes(self):
        self.btn_calib_mode.setText("Set Calibration Points (0/4)")
        self.btn_calib_mode.setChecked(False)
        self.btn_mask_mode.setChecked(False)
        self.canvas.set_mode(ImageCanvas.MODE_VIEW)
        self.inp_series_name.setText("Series 1")

    # Observer Callback
    def on_project_updated(self):
        # Update Table from Project Model
        self.table.setRowCount(0)
        for i, series in enumerate(self.project_model.series_list):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(series.name))
            
            color_item = QTableWidgetItem()
            color_item.setBackground(series.color)
            self.table.setItem(i, 1, color_item)
            
            self.table.setItem(i, 2, QTableWidgetItem(f"{len(series.data_points)} points"))
            
        self.btn_export.setEnabled(len(self.project_model.series_list) > 0)
        
        # Redraw Canvas Overlays
        # Note: We need to coordinate drawing calibration vs extracted points.
        # Ideally, Canvas should ask Model what to draw, or Model tells Canvas.
        # For now, we manually push series points to Canvas.
        
        # Clear 'Extracted' points from canvas, but keep image/mask/calibration markers?
        # ImageCanvas.clear_mask() clears mask.
        # We need a clear_extracted_points() in Canvas.
        # Currently we just re-draw fast.
        # 1. Update Image (Only if changed)
        if self.project_model.image_path:
             # Basic check: in a real app, track current loaded path in Canvas
             # For now, we trust set_image/load_image to be efficient or logic to be simple
             # If we just loaded a project, the canvas might need the image.
             
             # Problem: We don't track what image is currently in Canvas efficiently here.
             # We can't easily check `canvas.current_image_path`.
             # Let's assume if the scene is empty or we are initiating load, we do it.
             # But on series add, we don't want to reload.
             
             # Logic:
             # If this update came from `set_image` or `load_project`, we need to reload.
             # If from `add_series`, we don't.
             # But `on_project_updated` is generic.
             # Let's check if the scene has an image.
             if not self.canvas.scene.items(): 
                 self.canvas.load_image(self.project_model.image_path)
             # What if image changed? 
             # For now, let's assume we reload if we detect image path mismatch (TODO)
             
             # FORCE RELOAD for MVP robustness on Load Project (user interaction frequency low)
             # To avoid flickering on adding series, we need a flag?
             # Let's NOT force reload for now. Rely on `load_image` calling `canvas.load_image`.
             # But `load_project` needs to call `canvas.load_image`. 
             # I'll handle that in `load_project_ui`.
             pass

        # 2. Restore Calibration Points Visualization
        # The model has the logical points. We need to visualize them if they are missing.
        if self.project_model.calibration.pixel_points and not self.canvas.calibration_points:
             self.canvas.restore_calibration_points(self.project_model.calibration.pixel_points)
             self.btn_calib_mode.setText("Set Calibration Points (4/4)") # Update text
        
        # 3. Draw Series
        self.canvas.clear_extracted_points()
        
        # Actually draw:
        for series in self.project_model.series_list:
             self.canvas.draw_extracted_points(series.raw_pixels, color=series.color)
        
        # Update next series name
        next_idx = len(self.project_model.series_list) + 1
        self.inp_series_name.setText(f"Series {next_idx}")

    def toggle_calibration_mode(self):
        if self.btn_calib_mode.isChecked():
            self.canvas.set_mode(ImageCanvas.MODE_CALIBRATE)
        else:
            self.canvas.set_mode(ImageCanvas.MODE_VIEW)

    def toggle_gap_slider(self):
        mode = self.combo_pattern.currentText()
        if "Manual" in mode:
            self.container_gap.setVisible(True)
        else:
            self.container_gap.setVisible(False)
            
    def update_gap_label(self):
        val = self.slider_gap.value()
        self.lbl_gap.setText(f"Gap Fill: {val}px")

    def toggle_mask_mode(self):
        if self.btn_mask_mode.isChecked():
            self.canvas.set_mode(ImageCanvas.MODE_MASK)
        else:
            self.canvas.set_mode(ImageCanvas.MODE_VIEW)
            
    def undo_mask(self):
        self.canvas.undo_last_mask()
        
    def clear_mask(self):
        self.canvas.clear_mask()
            
    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            h, s, v, _ = color.getHsv()
            cv_h = int(h / 2)
            cv_s = int(s)
            cv_v = int(v)
            self.target_color_hsv = (cv_h, cv_s, cv_v)
            self.btn_color.setText(f"Color: HSV({cv_h},{cv_s},{cv_v})")
            self.btn_color.setStyleSheet(f"background-color: {color.name()}; color: {'white' if v < 128 else 'black'}")
            self.current_series_color = color 

    def update_calib_instructions(self):
        if self.chk_perspective.isChecked():
            self.lbl_status.setText("Perspective: Click corners TL -> TR -> BR -> BL")
        else:
            self.lbl_status.setText("Standard: Click Axis Points X1, X2, Y1, Y2")

    def on_calibration_point_added(self, idx, x, y):
        count = idx + 1
        self.btn_calib_mode.setText(f"Set Calibration Points ({count}/4)")
        if count == 4:
            self.btn_calib_mode.setChecked(False)
            self.canvas.set_mode(ImageCanvas.MODE_VIEW)
            self.mode_group.setExclusive(False)
            self.btn_calib_mode.setChecked(False)
            self.mode_group.setExclusive(True)

    def extract_data(self):
        if not self.project_model.image_path:
            QMessageBox.warning(self, "Error", "Please load an image first.")
            return
            
        if len(self.canvas.calibration_points) != 4:
            QMessageBox.warning(self, "Error", "Please set 4 calibration points.")
            return

        try:
            x1 = float(self.inp_x1.text())
            x2 = float(self.inp_x2.text())
            y1 = float(self.inp_y1.text())
            y2 = float(self.inp_y2.text())
            is_log_x = self.chk_log_x.isChecked()
            is_log_y = self.chk_log_y.isChecked()
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid calibration values.")
            return

        # Setup Calibration in Project Model
        calib_points_px = []
        for item in self.canvas.calibration_points:
            r = item.rect()
            calib_points_px.append((r.center().x(), r.center().y()))

        try:
            if self.chk_perspective.isChecked():
                # Perspective Mode: Assume points are TL, TR, BR, BL
                # Maps to Values: (x1, y2), (x2, y2), (x2, y1), (x1, y1)
                # Note: Y2 is usually Top (Max Y), Y1 is Bottom (Min Y)
                
                ordered_vals = [
                    (x1, y2), # TL
                    (x2, y2), # TR
                    (x2, y1), # BR
                    (x1, y1)  # BL
                ]
                self.project_model.update_calibration_perspective(calib_points_px, ordered_vals, is_log_x, is_log_y)
                
            else:
                # Standard Mode
                calib_values = [(x1, 0), (x2, 0), (0, y1), (0, y2)] 
                self.project_model.update_calibration(calib_points_px, calib_values, is_log_x, is_log_y)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Calibration failed: {str(e)}")
            return

        # Get Mask
        try:
            mask_qimage = self.canvas.get_mask_image()
            if mask_qimage is None:
                 QMessageBox.warning(self, "Error", "Failed to get mask.")
                 return
            
            ptr = mask_qimage.constBits()
            width = mask_qimage.width()
            height = mask_qimage.height()
            bytes_per_line = mask_qimage.bytesPerLine()

            raw_arr = np.array(ptr, copy=True).reshape(height, bytes_per_line)
            mask_arr = raw_arr[:, :width].copy() 
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Mask Error: {e}")
            return
        
        # Processing
        original_cv_img = cv2.imread(self.project_model.image_path)
        processor = ImageProcessor()
        
        hsv_range = None
        if self.target_color_hsv:
            h, s, v = self.target_color_hsv
            lower = np.array([max(0, h-10), max(0, s-50), max(0, v-50)])
            upper = np.array([min(180, h+10), min(255, s+50), min(255, v+50)])
            hsv_range = (lower, upper)
        
        try:
            mode_text = self.combo_pattern.currentText()
            line_type = 'auto'
            gap_fill = None
            
            if "Solid" in mode_text:
                line_type = 'solid'
            elif "Manual" in mode_text:
                line_type = 'manual'
                gap_fill = self.slider_gap.value()
            
            points_px, _ = processor.process_images(original_cv_img, mask_arr, hsv_range=hsv_range, line_type=line_type, gap_fill=gap_fill)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Processing failed: {str(e)}")
            return
            
        # Map & Add to Project
        series_points = []
        for px, py in points_px:
            dx, dy = self.project_model.calibration.map_to_data(px, py)
            series_points.append((dx, dy))
            
        series_name = self.inp_series_name.text()
        vis_color = self.current_series_color if self.target_color_hsv else QColor(np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
        
        new_series = Series(series_name, vis_color)
        new_series.set_data(points_px, series_points)
        new_series.line_type = line_type
        if gap_fill: new_series.gap_fill = gap_fill
        
        self.project_model.add_series(new_series)
        QMessageBox.information(self, "Success", f"Added Series '{series_name}' with {len(series_points)} points.")
        
    def clear_all_series(self):
        self.project_model.clear_data()
        # Visual clear handled by observer (partially, check logic above)
        # We need to manually clear items in canvas because we decided observer wouldn't wipe image
        self.canvas.clear_extracted_points() # Need to implement this

    def delete_selected_series(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Please select a series to delete.")
            return
        self.project_model.remove_series(row)
        self.canvas.clear_extracted_points() # Implement this!
        self.on_project_updated() # Re-draw remaining

    def export_csv(self):
        if not self.project_model.series_list:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file_path:
            try:
                header, rows = self.project_model.get_csv_data()
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    writer.writerows(rows)
                QMessageBox.information(self, "Saved", f"Data saved to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save: {str(e)}")

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save: {str(e)}")

    def save_project_ui(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON Files (*.json)")
        if file_path:
            try:
                self.project_model.save_project(file_path)
                QMessageBox.information(self, "Success", f"Project saved to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save project: {str(e)}")

    def load_project_ui(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "JSON Files (*.json)")
        if file_path:
            try:
                # Load logic:
                # 1. Load data
                self.project_model.load_project(file_path)
                
                # 2. UI Updates (Image loading)
                if self.project_model.image_path:
                     self.canvas.load_image(self.project_model.image_path)
                     self.lbl_status.setText(f"Loaded Project: {self.project_model.image_path.split('/')[-1]}")
                     # on_project_updated will trigger and restore points
                
                QMessageBox.information(self, "Success", f"Project loaded from {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load project: {str(e)}")

import sys
import os
import cv2
import numpy as np

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.processor import ImageProcessor
from core.calibration import Calibrator
from core.project import Project
from core.series import Series

def create_synthetic_plot():
    width, height = 500, 300
    image = np.ones((height, width, 3), dtype=np.uint8) * 255 # White background
    
    # Draw axes
    cv2.line(image, (50, 250), (450, 250), (0, 0, 0), 2) # X Axis at y=250
    cv2.line(image, (50, 250), (50, 50), (0, 0, 0), 2)   # Y Axis at x=50
    
    # Draw Sine Wave (Linear)
    points = []
    for x in range(50, 450):
        t = (x - 50) / 400.0 * 2 * np.pi
        y_val = np.sin(t)
        # y=1 -> 50, y=-1 -> 250
        y_px = 250 - (y_val + 1) / 2 * 200
        points.append((x, int(y_px)))
    
    pts = np.array(points, np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(image, [pts], False, (0, 0, 0), 2) # Black line for easy detection
    
    return image

def create_mask(width, height):
    # Create a mask that covers the sine wave area strictly, avoiding axes
    mask = np.zeros((height, width), dtype=np.uint8)
    # Axes are at x=50, y=250.
    # Sine wave goes y=50 to 250.
    # Let's shrink mask to x=55 to 445, y=55 to 245
    cv2.rectangle(mask, (55, 55), (445, 245), 255, -1)
    return mask

def test_extraction_and_model():
    print("--- Testing Extraction & Model ---")
    image = create_synthetic_plot()
    mask = create_mask(500, 300)
    
    cv2.imwrite("test_plot_v2.png", image)
    
    # 1. Processing
    processor = ImageProcessor()
    points, skeleton = processor.process_images(image, mask)
    print(f"Extracted {len(points)} points")
    
    if len(points) == 0:
        print("FAIL: No points extracted")
        return

    # 2. Project & Calibration (Linear)
    project = Project()
    calib_px = [(50, 250), (450, 250), (50, 250), (50, 50)]
    calib_val = [(0, 0), (10, 0), (0, 0), (0, 1)]
    
    project.update_calibration(calib_px, calib_val)
    
    # Map Data
    series = Series("SineWave")
    data_points = []
    for px, py in points:
        dx, dy = project.calibration.map_to_data(px, py)
        data_points.append((dx, dy))
    series.set_data(points, data_points)
    project.add_series(series)
    
    # Verify RMSE
    mse = 0
    count = 0
    for dx, dy in series.data_points:
        expected_dy = (np.sin(dx / 10 * 2 * np.pi) + 1) / 2
        mse += (dy - expected_dy) ** 2
        count += 1
        
    rmse = np.sqrt(mse / count)
    print(f"Linear RMSE: {rmse}")
    if rmse < 0.05:
        print("PASS: Linear Calibration")
    else:
        print("FAIL: Linear RMSE too high")

def test_log_calibration():
    print("\n--- Testing Log Calibration ---")
    calib = Calibrator()
    
    # Setup Log X (1 to 100), Linear Y (0 to 1)
    # Screen X: 100 to 300 (200px width)
    # Log(1)=0, Log(100)=2. Range=2. Scale = 200px / 2 = 100 px/decade
    
    calib_px = [(100, 200), (300, 200), (100, 200), (100, 100)]
    calib_val = [(1, 0), (100, 0), (1, 0), (1, 1)]
    
    calib.set_calibration(calib_px, calib_val, is_log_x=True, is_log_y=False)
    
    # Test Point: Middle Pixel (200, 200)
    # Should correspond to Log Midpoint: (Log(100)+Log(1))/2 = 1.
    # 10^1 = 10.
    
    dx, dy = calib.map_to_data(200, 200)
    print(f"Px(200,200) -> Data({dx:.2f}, {dy:.2f})")
    
    if abs(dx - 10.0) < 0.1:
        print("PASS: Log X Calibration (Expected ~10.0)")
    else:
        print(f"FAIL: Expected 10.0, got {dx}")

if __name__ == "__main__":
    test_extraction_and_model()
    test_log_calibration()

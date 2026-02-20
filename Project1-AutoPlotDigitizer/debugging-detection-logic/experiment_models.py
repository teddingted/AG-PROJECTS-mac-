import sys
import os
import cv2
import numpy as np
import json

# Add project root to path to import core modules
sys.path.append('/Users/dm_chamber/Desktop/AutoPlotDigitizerWeb')

from core.auto_detector import AutoDetector

def run_experiment():
    image_path = 'image2.png'
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    print(f"Loading {image_path}...")
    detector = AutoDetector(image_path)
    
    # 1. Detect Axes & Calibration
    print("Detecting axes...")
    axes = detector.detect_axes()
    
    x_min_val, x_max_val = 1990, 2050
    y_min_val, y_max_val = 0, 12000
    
    calibration = None
    if axes:
        print("Axes detected.")
        endpoints = detector.get_axis_endpoints(axes)
        # Assume standard orientation: 
        # x_axis starts at endpoints['x_axis']['start'] and ends at endpoints['x_axis']['end']
        # But get_axis_endpoints returns dict with 'start' and 'end' points
        # Structure of endpoints: {'x_axis': {'start': (x, y), 'end': (x, y)}, ...}
        
        x1_px = endpoints['x_start'][0]
        x2_px = endpoints['x_end'][0]
        y1_px = endpoints['y_start'][1]
        y2_px = endpoints['y_end'][1]
        
        # Calculate scale
        x_scale = (x_max_val - x_min_val) / (x2_px - x1_px) if x2_px != x1_px else 1
        y_scale = (y_max_val - y_min_val) / (y2_px - y1_px) if y2_px != y1_px else 1
        
        calibration = {
            'x1_px': x1_px, 'y1_px': y1_px,
            'x_scale': x_scale, 'y_scale': y_scale,
            'x_min_val': x_min_val, 'y_min_val': y_min_val
        }
    else:
        print("Warning: Axes not detected. Using image bounds as range (approximate).")
        h, w = detector.image.shape[:2]
        calibration = {
            'x1_px': 0, 'y1_px': h,
            'x_scale': (x_max_val - x_min_val) / w,
            'y_scale': (y_max_val - y_min_val) / -h, # Y flips in image coords
            'x_min_val': x_min_val, 'y_min_val': y_min_val
        }

    # Define Models
    models = [
        ('Model_1_Baseline', run_model_1),
        ('Model_2_Strong_Morph', run_model_2),
        ('Model_3_Dilation_Thinning', run_model_3)
    ]
    
    combined_results = {}
    
    for name, func in models:
        print(f"Running {name}...")
        try:
            points = func(detector)
            
            # Filter and Visualize
            vis_img = detector.image.copy()
            valid_points = []
            
            for p in points:
                px, py = p
                # Convert to value
                vx = calibration['x_min_val'] + (px - calibration['x1_px']) * calibration['x_scale']
                vy = calibration['y_min_val'] + (py - calibration['y1_px']) * calibration['y_scale']
                
                # Check range
                if x_min_val <= vx <= x_max_val and y_min_val <= vy <= y_max_val:
                    valid_points.append(p)
                    cv2.circle(vis_img, (px, py), 2, (0, 255, 0), -1) # Green for valid
                else:
                    cv2.circle(vis_img, (px, py), 2, (0, 0, 255), -1) # Red for invalid
            
            # Save result
            output_filename = f"result_{name}.png"
            cv2.imwrite(output_filename, vis_img)
            print(f"Saved {output_filename} with {len(valid_points)} valid points.")
            combined_results[name] = len(valid_points)
            
        except Exception as e:
            print(f"Error in {name}: {e}")
            import traceback
            traceback.print_exc()

def run_model_1(detector):
    # Baseline: Use what's currently in auto_detector (Advanced HSV)
    mask = get_data_mask(detector)
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return extract_points_from_mask(mask)

def run_model_2(detector):
    # Strong Morphology: Connect dashed lines
    mask = get_data_mask(detector)
    kernel = np.ones((3, 3), np.uint8) # Larger kernel
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=5) # More iterations
    return extract_points_from_mask(mask)

def run_model_3(detector):
    # Dilation + Thinning: Connect gaps then thin back
    mask = get_data_mask(detector)
    
    # 1. Dilate to connect gaps
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=3)
    
    # 2. Skeletonize (Manual implementation as cv2.ximgproc is missing)
    skeleton = np.zeros(mask.shape, np.uint8)
    eroded = mask.copy()
    temp = np.zeros(mask.shape, np.uint8)
    skel_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    
    while True:
        cv2.erode(eroded, skel_kernel, eroded)
        cv2.dilate(eroded, skel_kernel, temp)
        cv2.subtract(mask, temp, temp)
        cv2.bitwise_or(skeleton, temp, skeleton)
        mask = eroded.copy()
        if cv2.countNonZero(mask) == 0:
            break
            
    return extract_points_from_mask(skeleton)

def get_data_mask(detector):
    # Helper to get binary mask of data (graph lines)
    hsv = cv2.cvtColor(detector.image, cv2.COLOR_BGR2HSV)
    
    # Exclude background (white/light)
    lower_exclude = np.array([0, 0, 200])
    upper_exclude = np.array([180, 50, 255])
    bg_mask = cv2.inRange(hsv, lower_exclude, upper_exclude)
    
    # Exclude axes (black/gray)
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 100]) # Exclude axes
    axes_mask = cv2.inRange(hsv, lower_dark, upper_dark)
    
    # Combine to exclude
    exclude = cv2.bitwise_or(bg_mask, axes_mask)
    data_mask = cv2.bitwise_not(exclude)
    
    # Remove small noise
    kernel = np.ones((2,2), np.uint8)
    data_mask = cv2.morphologyEx(data_mask, cv2.MORPH_OPEN, kernel)
    
    return data_mask

def extract_points_from_mask(mask):
    # Extract center points
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    points = []
    if not contours:
        return points
        
    # Draw processed mask
    mask_filled = np.zeros_like(mask)
    cv2.drawContours(mask_filled, contours, -1, 255, -1)
    
    y_coords, x_coords = np.where(mask_filled > 0)
    
    # Center alignment
    x_to_y = {}
    for x, y in zip(x_coords, y_coords):
        if x not in x_to_y:
            x_to_y[x] = []
        x_to_y[x].append(y)
    
    for x in sorted(x_to_y.keys()):
        ys = x_to_y[x]
        mean_y = int(round(sum(ys) / len(ys)))
        points.append((x, mean_y))
        
    return points

if __name__ == "__main__":
    run_experiment()

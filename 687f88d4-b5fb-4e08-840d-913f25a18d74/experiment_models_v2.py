import sys
import os
import cv2
import numpy as np

sys.path.append('/Users/dm_chamber/Desktop/AutoPlotDigitizerWeb')
from core.auto_detector import AutoDetector

def run_experiment_v2():
    image_path = 'image2.png'
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    print(f"Loading {image_path}...")
    detector = AutoDetector(image_path)
    
    # 1. Detect Axes
    print("Detecting axes...")
    axes = detector.detect_axes()
    endpoints = None
    
    calibration = {}
    x_min_val, x_max_val = 1990, 2050
    y_min_val, y_max_val = 0, 12000

    if axes:
        print("Axes detected. Calculating Plot Area...")
        endpoints = detector.get_axis_endpoints(axes)
        print(f"Endpoints: {endpoints}")
        
        x1_px = endpoints['x_start'][0]
        x2_px = endpoints['x_end'][0]
        y1_px = endpoints['y_start'][1]
        y2_px = endpoints['y_end'][1]
        
        calibration = {
            'x1_px': x1_px, 'y1_px': y1_px,
            'x_scale': (x_max_val - x_min_val) / (x2_px - x1_px) if x2_px != x1_px else 1,
            'y_scale': (y_max_val - y_min_val) / (y2_px - y1_px) if y2_px != y1_px else 1,
            'x_min_val': x_min_val, 'y_min_val': y_min_val
        }
    else:
        print("Error: Axes not detected.")
        h, w = detector.image.shape[:2]
        calibration = {
            'x1_px': 0, 'y1_px': h,
            'x_scale': (x_max_val - x_min_val) / w,
            'y_scale': (y_max_val - y_min_val) / -h,
            'x_min_val': x_min_val, 'y_min_val': y_min_val
        }

    # Define Plot Area Mask
    plot_mask = get_plot_area_mask(detector, endpoints)
    
    # Define Models
    models = [
        ('Model_1_ROI_Baseline', run_model_1),
        ('Model_2_ROI_Strong', run_model_2),
        ('Model_3_ROI_Skel', run_model_3)
    ]
    
    for name, func in models:
        print(f"Running {name}...")
        try:
            points = func(detector, plot_mask)
            
            # Visualize
            vis_img = detector.image.copy()
            contours, _ = cv2.findContours(plot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(vis_img, contours, -1, (255, 0, 0), 2)
            
            valid_count = 0
            for p in points:
                px, py = p
                # Check Mask
                if plot_mask[py, px] == 0:
                    cv2.circle(vis_img, (px, py), 2, (0, 0, 255), -1) # Red (Outside ROI)
                    continue
                    
                # Check Value Range
                vx = calibration['x_min_val'] + (px - calibration['x1_px']) * calibration['x_scale']
                vy = calibration['y_min_val'] + (py - calibration['y1_px']) * calibration['y_scale']
                
                if x_min_val <= vx <= x_max_val and y_min_val <= vy <= y_max_val:
                    cv2.circle(vis_img, (px, py), 2, (0, 255, 0), -1) # Green
                    valid_count += 1
                else:
                    cv2.circle(vis_img, (px, py), 2, (0, 255, 255), -1) # Yellow (Inside ROI but Value out)
            
            output_filename = f"result_v2_{name}.png"
            cv2.imwrite(output_filename, vis_img)
            print(f"Saved {output_filename} with {valid_count} valid points.")
            
        except Exception as e:
            print(f"Error in {name}: {e}")
            import traceback
            traceback.print_exc()

def get_plot_area_mask(detector, endpoints):
    mask = np.zeros(detector.image.shape[:2], dtype=np.uint8)
    
    if not endpoints:
        return mask
        
    roi_x1 = int(endpoints['x_start'][0])
    roi_x2 = int(endpoints['x_end'][0])
    roi_y1 = int(endpoints['y_end'][1]) # Top
    roi_y2 = int(endpoints['x_start'][1]) # Bottom
    
    # Ensure min/max
    roi_x1, roi_x2 = min(roi_x1, roi_x2), max(roi_x1, roi_x2)
    roi_y1, roi_y2 = min(roi_y1, roi_y2), max(roi_y1, roi_y2)
    
    print(f"ROI Raw: x1={roi_x1}, x2={roi_x2}, y1={roi_y1}, y2={roi_y2}")
    
    margin = 5
    roi_x1 += margin
    roi_x2 -= margin
    roi_y1 += margin
    roi_y2 -= margin
    
    h, w = mask.shape
    roi_x1 = max(0, min(w, roi_x1))
    roi_x2 = max(0, min(w, roi_x2))
    roi_y1 = max(0, min(h, roi_y1))
    roi_y2 = max(0, min(h, roi_y2))
    
    print(f"ROI Final: x1={roi_x1}, x2={roi_x2}, y1={roi_y1}, y2={roi_y2}")
    
    if roi_x2 > roi_x1 and roi_y2 > roi_y1:
        mask[roi_y1:roi_y2, roi_x1:roi_x2] = 255
    else:
        print("Warning: ROI invalid. Falling back.")
        mask[int(h*0.1):int(h*0.9), int(w*0.1):int(w*0.9)] = 255
        
    return mask

def get_data_mask(detector, plot_mask):
    hsv = cv2.cvtColor(detector.image, cv2.COLOR_BGR2HSV)
    lower_exclude = np.array([0, 0, 200])
    upper_exclude = np.array([180, 50, 255])
    bg_mask = cv2.inRange(hsv, lower_exclude, upper_exclude)
    data_mask = cv2.bitwise_not(bg_mask)
    data_mask = cv2.bitwise_and(data_mask, plot_mask)
    return data_mask

def extract_points_from_mask(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours: return []
    mask_filled = np.zeros_like(mask)
    cv2.drawContours(mask_filled, contours, -1, 255, -1)
    y_coords, x_coords = np.where(mask_filled > 0)
    x_to_y = {}
    for x, y in zip(x_coords, y_coords):
        if x not in x_to_y: x_to_y[x] = []
        x_to_y[x].append(y)
    points = []
    for x in sorted(x_to_y.keys()):
        ys = x_to_y[x]
        mean_y = int(round(sum(ys) / len(ys)))
        points.append((x, mean_y))
    return points

def run_model_1(detector, plot_mask):
    mask = get_data_mask(detector, plot_mask)
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return extract_points_from_mask(mask)

def run_model_2(detector, plot_mask):
    mask = get_data_mask(detector, plot_mask)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=5)
    return extract_points_from_mask(mask)

def run_model_3(detector, plot_mask):
    mask = get_data_mask(detector, plot_mask)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=3)
    skeleton = np.zeros(mask.shape, np.uint8)
    eroded = mask.copy()
    temp = np.zeros(mask.shape, np.uint8)
    skel_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    for _ in range(100):
        cv2.erode(eroded, skel_kernel, eroded)
        cv2.dilate(eroded, skel_kernel, temp)
        cv2.subtract(mask, temp, temp)
        cv2.bitwise_or(skeleton, temp, skeleton)
        mask = eroded.copy()
        if cv2.countNonZero(mask) == 0:
            break
    return extract_points_from_mask(skeleton)

if __name__ == "__main__":
    run_experiment_v2()

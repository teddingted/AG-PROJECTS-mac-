import sys
import os
import cv2
import numpy as np

sys.path.append('/Users/dm_chamber/Desktop/AutoPlotDigitizerWeb')
from core.auto_detector import AutoDetector

def run_experiment_v3():
    image_path = 'image2.png'
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    print(f"Loading {image_path}...")
    detector = AutoDetector(image_path)
    
    # 1. Detect Axes & Calibration
    print("Detecting axes...")
    axes = detector.detect_axes()
    endpoints = None
    calibration = {}
    x_min_val, x_max_val = 1990, 2050
    y_min_val, y_max_val = 0, 12000

    if axes:
        print("Axes detected. Calculating Plot Area...")
        endpoints = detector.get_axis_endpoints(axes)
        
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
    
    # Run Advanced Separation Model
    run_separation_model(detector, plot_mask, calibration, x_min_val, x_max_val, y_min_val, y_max_val)

def get_plot_area_mask(detector, endpoints):
    mask = np.zeros(detector.image.shape[:2], dtype=np.uint8)
    if not endpoints: return mask
    
    roi_x1 = int(endpoints['x_start'][0])
    roi_x2 = int(endpoints['x_end'][0])
    roi_y1 = int(endpoints['y_end'][1])
    roi_y2 = int(endpoints['x_start'][1])
    
    roi_x1, roi_x2 = min(roi_x1, roi_x2), max(roi_x1, roi_x2)
    roi_y1, roi_y2 = min(roi_y1, roi_y2), max(roi_y1, roi_y2)
    
    margin = 5
    roi_x1 += margin; roi_x2 -= margin; roi_y1 += margin; roi_y2 -= margin
    
    h, w = mask.shape
    roi_x1 = max(0, min(w, roi_x1)); roi_x2 = max(0, min(w, roi_x2))
    roi_y1 = max(0, min(h, roi_y1)); roi_y2 = max(0, min(h, roi_y2))
    
    if roi_x2 > roi_x1 and roi_y2 > roi_y1:
        mask[roi_y1:roi_y2, roi_x1:roi_x2] = 255
    else:
        # Fallback
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

def run_separation_model(detector, plot_mask, calibration, x_min_range, x_max_range, y_min_range, y_max_range):
    print("Running Density-Based Separation Model (V3.3)...")
    
    # 1. Get Base Mask
    mask = get_data_mask(detector, plot_mask)
    
    # 2. Dilate to connect components
    kernel = np.ones((3, 3), np.uint8)
    # Use standard 3x3 kernel, iterated 4 times to bridge gaps
    dilated_mask = cv2.dilate(mask, kernel, iterations=4) 
    
    # 3. Find Contours on Dilated Mask
    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    type_map = np.zeros(mask.shape, dtype=np.uint8) # 1: Solid, 2: Dashed
    vis_debug = detector.image.copy()
    
    print(f"Found {len(contours)} meta-contours.")
    
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        if area < 50: continue 
        
        # Create mask for this contour to calculate density
        c_mask = np.zeros(mask.shape, dtype=np.uint8)
        cv2.drawContours(c_mask, [cnt], -1, 255, -1)
        
        # Density Calculation
        # Count pixels of *original* mask inside this dilated contour
        dilated_area = cv2.countNonZero(c_mask)
        original_in_contour = cv2.bitwise_and(mask, mask, mask=c_mask)
        original_area = cv2.countNonZero(original_in_contour)
        
        ratio = original_area / dilated_area if dilated_area > 0 else 0
        
        is_solid = False
        cls_name = "Unknown"
        
        # Heuristic: 
        # Solid lines are dense (Ratio ~ 0.3-0.5 depending on dilation)
        # Dashed lines are sparse (Ratio < 0.25)
        # Assuming original line width ~2px and dilated width ~10px -> Ratio ~0.2
        # But Dashed has gaps -> Ratio even lower.
        
        if w > 30: 
            # Threshold needs tuning based on log output
            if ratio > 0.28: 
                is_solid = True
                cls_name = "Solid"
            else:
                is_solid = False
                cls_name = "Dashed"
        else:
            is_solid = False
            cls_name = "Short/Dashed"
            
        print(f"Contour {i}: w={w}, area={area}, ratio={ratio:.3f} -> {cls_name}")
        
        cv2.drawContours(type_map, [cnt], -1, 1 if is_solid else 2, -1)
        color = (255, 0, 0) if is_solid else (0, 0, 255)
        cv2.putText(vis_debug, f"{ratio:.2f}", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        cv2.rectangle(vis_debug, (x, y), (x+w, y+h), color, 1)

    cv2.imwrite("debug_density.png", vis_debug)
    
    # 4. Extract Path (Skeleton)
    skeleton = np.zeros(dilated_mask.shape, np.uint8)
    eroded = dilated_mask.copy()
    temp = np.zeros(dilated_mask.shape, np.uint8)
    skel_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    
    for _ in range(100):
        cv2.erode(eroded, skel_kernel, eroded)
        cv2.dilate(eroded, skel_kernel, temp)
        cv2.subtract(dilated_mask, temp, temp)
        cv2.bitwise_or(skeleton, temp, skeleton)
        dilated_mask = eroded.copy()
        if cv2.countNonZero(dilated_mask) == 0: break
        
    points = extract_points_from_mask(skeleton)
    points.sort(key=lambda p: p[0])
    
    final_solid = []
    final_dashed = []
    
    for px, py in points:
        if plot_mask[py, px] == 0: continue
        vx = calibration['x_min_val'] + (px - calibration['x1_px']) * calibration['x_scale']
        vy = calibration['y_min_val'] + (py - calibration['y1_px']) * calibration['y_scale']
        if not (x_min_range <= vx <= x_max_range and y_min_range <= vy <= y_max_range):
            continue
            
        # Check type map
        cls = type_map[py, px]
        
        if cls == 1:
            final_solid.append((px, py))
        elif cls == 2:
            final_dashed.append((px, py))
        else:
            # Check neighbors if skeleton is slightly off
            w_size = 2
            roi = type_map[max(0, py-w_size):min(py+w_size, type_map.shape[0]), 
                           max(0, px-w_size):min(px+w_size, type_map.shape[1])]
            if np.any(roi == 1): final_solid.append((px, py))
            elif np.any(roi == 2): final_dashed.append((px, py))
            
    # Visualize
    vis_result = detector.image.copy()
    for px, py in final_solid:
        cv2.circle(vis_result, (px, py), 2, (255, 0, 0), -1)
    for px, py in final_dashed:
        cv2.circle(vis_result, (px, py), 2, (0, 0, 255), -1)
        
    # Also Draw Legend
    cv2.putText(vis_result, f"Solid: {len(final_solid)}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    cv2.putText(vis_result, f"Dashed: {len(final_dashed)}", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
    cv2.imwrite("result_v3_separated.png", vis_result)
    print(f"Saved result_v3_separated.png with {len(final_solid)} solid and {len(final_dashed)} dashed points.")

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

if __name__ == "__main__":
    run_experiment_v3()

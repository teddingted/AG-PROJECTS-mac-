import sys
import os
import cv2
import numpy as np

sys.path.append('/Users/dm_chamber/Desktop/AutoPlotDigitizerWeb')
from core.auto_detector import AutoDetector

def run_experiment_v4():
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
        h, w = detector.image.shape[:2]
        calibration = {
            'x1_px': 0, 'y1_px': h,
            'x_scale': (x_max_val - x_min_val) / w,
            'y_scale': (y_max_val - y_min_val) / -h,
            'x_min_val': x_min_val, 'y_min_val': y_min_val
        }

    # Define Plot Area Mask
    plot_mask = get_plot_area_mask(detector, endpoints)
    
    # Run Seed Growing Model
    run_seed_growing_model(detector, plot_mask, calibration, x_min_range=x_min_val, x_max_range=x_max_val, y_min_range=y_min_val, y_max_range=y_max_val)

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

def run_seed_growing_model(detector, plot_mask, calibration, x_min_range, x_max_range, y_min_range, y_max_range):
    print("Running Seed Growing Separation Model (V4)...")
    
    mask = get_data_mask(detector, plot_mask)
    
    # Minimal morphology to reduce noise but keep structure
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    boxes = []
    vis_debug = detector.image.copy()
    
    for i, cnt in enumerate(contours):
        if cv2.contourArea(cnt) < 5: continue
        x, y, w, h = cv2.boundingRect(cnt)
        boxes.append({
            'id': i,
            'rect': (x, y, w, h),
            'w': w,
            'h': h,
            'contour': cnt,
            'center': (x + w/2, y + h/2),
            'group': -1 # -1: Unassigned
        })
        cv2.rectangle(vis_debug, (x, y), (x+w, y+h), (0, 255, 0), 1)

    # Identify Seeds
    # Solid Seeds: Width > 40px
    seeds = [b for b in boxes if b['w'] > 40]
    
    print(f"Found {len(boxes)} boxes. {len(seeds)} are solid seeds (>40px).")
    
    # Assign Group ID 1 (Solid) to Seeds
    for s in seeds:
        s['group'] = 1
        cv2.rectangle(vis_debug, (s['rect'][0], s['rect'][1]), 
                      (s['rect'][0]+s['rect'][2], s['rect'][1]+s['rect'][3]), (255, 0, 0), 2)
        
    # Iterative Region Growing
    changed = True
    iterations = 0
    max_dist = 20 # 20px gap allowed
    
    while changed and iterations < 20:
        changed = False
        iterations += 1
        
        # Try to merge Unassigned boxes to Group 1
        unassigned = [b for b in boxes if b['group'] == -1]
        solid_group = [b for b in boxes if b['group'] == 1]
        
        for u in unassigned:
            # Check distance to any solid box
            min_dist = float('inf')
            
            for s in solid_group:
                # Calc distance between rectangles
                # Approx distance between centers
                dist = np.sqrt((u['center'][0] - s['center'][0])**2 + (u['center'][1] - s['center'][1])**2)
                
                # More precise: distance between edges? 
                # Center distance is roughly okay for small gaps
                # Subtract radii approx
                dist_edge = dist - (u['w'] + s['w'])/2 - (u['h'] + s['h'])/2
                # If negative, they overlap or close.
                # Let's use simple center distance logic:
                # If center distance < (sum of dimensions)/2 + gap
                if dist < (u['w']/2 + s['w']/2 + max_dist) and dist < (u['h']/2 + s['h']/2 + max_dist):
                     min_dist = 0 # Match
                     break
                     
            if min_dist == 0:
                u['group'] = 1
                changed = True
                
    # Assign remaining to Group 2 (Dashed)
    for b in boxes:
        if b['group'] == -1:
            b['group'] = 2
            
    # Visualize categorization
    type_map = np.zeros(mask.shape, dtype=np.uint8)
    for b in boxes:
        color = (255, 0, 0) if b['group'] == 1 else (0, 0, 255)
        cv2.drawContours(type_map, [b['contour']], -1, b['group'], -1)
        cv2.rectangle(vis_debug, (b['rect'][0], b['rect'][1]), 
                      (b['rect'][0]+b['rect'][2], b['rect'][1]+b['rect'][3]), color, 2)
                      
    cv2.imwrite("debug_grouping.png", vis_debug)
    
    # Extract Points
    # Create mask for solid and dashed
    mask_solid = np.zeros_like(mask)
    mask_dashed = np.zeros_like(mask)
    
    for b in boxes:
        if b['group'] == 1:
            cv2.drawContours(mask_solid, [b['contour']], -1, 255, -1)
        else:
            cv2.drawContours(mask_dashed, [b['contour']], -1, 255, -1)
            
    # Extract points using standard method
    points_solid = extract_points_from_mask(mask_solid)
    points_dashed = extract_points_from_mask(mask_dashed)
    
    # Visualize Final
    vis_result = detector.image.copy()
    
    final_solid = []
    final_dashed = []
    
    for px, py in points_solid:
        vx = calibration['x_min_val'] + (px - calibration['x1_px']) * calibration['x_scale']
        vy = calibration['y_min_val'] + (py - calibration['y1_px']) * calibration['y_scale']
        if x_min_range <= vx <= x_max_range and y_min_range <= vy <= y_max_range:
             cv2.circle(vis_result, (px, py), 2, (255, 0, 0), -1)
             final_solid.append((px, py))

    for px, py in points_dashed:
        vx = calibration['x_min_val'] + (px - calibration['x1_px']) * calibration['x_scale']
        vy = calibration['y_min_val'] + (py - calibration['y1_px']) * calibration['y_scale']
        if x_min_range <= vx <= x_max_range and y_min_range <= vy <= y_max_range:
             cv2.circle(vis_result, (px, py), 2, (0, 0, 255), -1)
             final_dashed.append((px, py))
             
    cv2.putText(vis_result, f"Solid: {len(final_solid)}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    cv2.putText(vis_result, f"Dashed: {len(final_dashed)}", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    cv2.imwrite("result_v4_separated.png", vis_result)
    print(f"Saved result_v4_separated.png with {len(final_solid)} solid and {len(final_dashed)} dashed points.")

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
    run_experiment_v4()

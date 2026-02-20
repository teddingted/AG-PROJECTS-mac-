import sys
import os
import cv2
import numpy as np

sys.path.append('/Users/dm_chamber/Desktop/AutoPlotDigitizerWeb')
from core.auto_detector import AutoDetector

def run_experiment_v5():
    image_path = 'image2.png'
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found.")
        return

    print(f"Loading {image_path}...")
    detector = AutoDetector(image_path)
    
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

    plot_mask = get_plot_area_mask(detector, endpoints)
    
    run_graph_clustering_model(detector, plot_mask, calibration, x_min_range=x_min_val, x_max_range=x_max_val, y_min_range=y_min_val, y_max_range=y_max_val)

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

def run_graph_clustering_model(detector, plot_mask, calibration, x_min_range, x_max_range, y_min_range, y_max_range):
    print("Running Graph Clustering Separation Model (V5)...")
    
    mask = get_data_mask(detector, plot_mask)
    
    # 1. Close small gaps in Solid line
    kernel = np.ones((2, 2), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # 2. Find Contours
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
            'merged': False,
            'group_id': i # Initially self-group
        })
        cv2.rectangle(vis_debug, (x, y), (x+w, y+h), (0, 255, 0), 1)

    print(f"Found {len(boxes)} boxes.")
    
    # 3. Cluster by Proximity (Strong Links only)
    # Distance Threshold: 3px (Since kernel 2x2 already closed 2px gaps)
    dist_threshold = 4.0 
    
    # Union-Find / Adjacency
    # Just iterative merge
    changed = True
    while changed:
        changed = False
        groups = {}
        for b in boxes:
            gid = b['group_id']
            if gid not in groups: groups[gid] = []
            groups[gid].append(b)
            
        # Check merges between groups
        group_ids = list(groups.keys())
        for i in range(len(group_ids)):
            for j in range(i+1, len(group_ids)):
                gid1 = group_ids[i]
                gid2 = group_ids[j]
                
                # Check distance between any box in g1 and g2
                has_close = False
                for b1 in groups[gid1]:
                    for b2 in groups[gid2]:
                        # Approx edge distance
                        dx = max(0, abs(b1['center'][0] - b2['center'][0]) - (b1['w'] + b2['w'])/2)
                        dy = max(0, abs(b1['center'][1] - b2['center'][1]) - (b1['h'] + b2['h'])/2)
                        dist = np.sqrt(dx*dx + dy*dy)
                        
                        if dist < dist_threshold:
                            has_close = True
                            break
                    if has_close: break
                
                if has_close:
                    # Merge g2 into g1
                    for b in groups[gid2]:
                        b['group_id'] = gid1
                    changed = True
                    break # Restart loop to refresh groups dict
            if changed: break
            
    # 4. Classify Groups
    # Re-gather groups
    groups = {}
    for b in boxes:
        gid = b['group_id']
        if gid not in groups: groups[gid] = []
        groups[gid].append(b)
        
    final_solid = []
    final_dashed = []
    
    vis_res = detector.image.copy()
    
    for gid, group_boxes in groups.items():
        # Calculate Group bounding box and metrics
        min_x = min(b['rect'][0] for b in group_boxes)
        max_x = max(b['rect'][0] + b['rect'][2] for b in group_boxes)
        total_width = max_x - min_x
        
        # Calculate Density inside Group Bounds? No need.
        # Just Width Threshold.
        # Solid Series: > 30px width
        # Dashed Series: < 30px width (since they couldn't merge)
        
        is_solid = total_width > 30
        
        cls_name = "Solid" if is_solid else "Dashed"
        color = (255, 0, 0) if is_solid else (0, 0, 255)
        
        print(f"Group {gid}: boxes={len(group_boxes)}, width={total_width} -> {cls_name}")
        
        # Draw Group BBox
        cv2.rectangle(vis_debug, (min_x, min(b['rect'][1] for b in group_boxes)), 
                      (max_x, max(b['rect'][1]+b['rect'][3] for b in group_boxes)), color, 2)
        
        # Add points
        target_list = final_solid if is_solid else final_dashed
        
        for b in group_boxes:
            # Extract points from this contour
            mask_b = np.zeros(mask.shape, dtype=np.uint8)
            cv2.drawContours(mask_b, [b['contour']], -1, 255, -1)
            pts = extract_points_from_mask(mask_b)
            for p in pts:
                target_list.append(p)
                cv2.circle(vis_res, p, 2, color, -1)

    cv2.imwrite("debug_clustering.png", vis_debug)
    cv2.imwrite("result_v5_separated.png", vis_res)
    print(f"Saved result_v5_separated.png with {len(final_solid)} solid and {len(final_dashed)} dashed points.")

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
    run_experiment_v5()

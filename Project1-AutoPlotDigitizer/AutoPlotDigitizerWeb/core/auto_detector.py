import cv2
import numpy as np
from typing import Tuple, List, Optional, Any

class AutoDetector:
    """Automatic detection of axes and data curves in graph images"""
    
    def __init__(self, image_path: str, calibration_points: Optional[dict] = None):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.height, self.width = self.gray.shape
        self.calibration_points = calibration_points
        self.plot_area = self._calculate_plot_area_from_calibration(calibration_points) if calibration_points else None
    
    def _sample_color_at_click(self, x: int, y: int, radius: int = 2) -> Tuple[int, int, int]:
        """Extract actual color at click position by sampling nearby pixels"""
        y_min = max(0, y - radius)
        y_max = min(self.height, y + radius + 1)
        x_min = max(0, x - radius)
        x_max = min(self.width, x + radius + 1)
        
        local_region = self.image[y_min:y_max, x_min:x_max]
        # Use median to be robust against outliers
        actual_color = np.median(local_region.reshape(-1, 3), axis=0).astype(int)
        return tuple(actual_color)  # BGR format
    
    def _sample_pattern_at_click(self, mask: np.ndarray, x: int, y: int, radius: int = 10) -> str:
        """Analyze pattern density in local region to classify line style"""
        y_min = max(0, y - radius)
        y_max = min(self.height, y + radius + 1)
        x_min = max(0, x - radius)
        x_max = min(self.width, x + radius + 1)
        
        local_mask = mask[y_min:y_max, x_min:x_max]
        if local_mask.size == 0:
            return 'solid'
        
        density = np.sum(local_mask > 0) / local_mask.size
        
        # Classify based on density
        if density > 0.7:
            return 'solid'
        elif density > 0.25:
            return 'dashed'
        else:
            return 'dotted'
    
    def _extract_connected_component(self, mask: np.ndarray, x: int, y: int) -> np.ndarray:
        """Extract only the connected component that contains the click position"""
        # Find all connected components
        num_labels, labels = cv2.connectedComponents(mask)
        
        if num_labels <= 1:  # No components or only background
            return mask
        
        # Get the label at click position
        if 0 <= y < labels.shape[0] and 0 <= x < labels.shape[1]:
            clicked_label = labels[y, x]
            
            if clicked_label == 0:  # Clicked on background
                return mask
            
            # Create mask for only the clicked component
            # Fix: Explicitly create numpy array from boolean mask
            component_mask = np.array(labels == clicked_label, dtype=np.uint8) * 255
            return component_mask
        
        return mask
    
    def _calculate_plot_area_from_calibration(self, calibration_data: Any) -> Optional[dict]:
        """Calculate plot area boundaries from calibration data (dict or list) - Robust Version"""
        if not calibration_data:
            print("DEBUG: Calibration data is empty")
            return None
        
        try:
            points = []
            
            # Helper to extract point from various formats
            def extract_xy(pt):
                # Case 1: List/Tuple [x, y]
                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                    return int(pt[0]), int(pt[1])
                
                # Case 2: Dict with 'pixel' key (Legacy & Frontend Standard)
                elif isinstance(pt, dict) and 'pixel' in pt:
                    px = pt['pixel']
                    # If pixel is [x, y]
                    if isinstance(px, (list, tuple)) and len(px) >= 2:
                        return int(px[0]), int(px[1])
                    # If pixel is scalar x (legacy)
                    return int(px), int(pt.get('y',0))
                
                # Case 3: Dict with 'x', 'y' keys
                elif isinstance(pt, dict) and 'x' in pt and 'y' in pt:
                     return int(pt['x']), int(pt['y'])
                return None

            # Strategy 1: 'points' key in dict
            if isinstance(calibration_data, dict) and 'points' in calibration_data:
                raw_points = calibration_data['points']
                if isinstance(raw_points, list):
                    for p in raw_points:
                        pt = extract_xy(p)
                        if pt: points.append(pt)
            
            # Strategy 2: Direct list
            elif isinstance(calibration_data, list):
                for p in calibration_data:
                    pt = extract_xy(p)
                    if pt: points.append(pt)
                    
            # Strategy 3: Legacy keys (x1, x2...) and extract 'pixel' values
            elif isinstance(calibration_data, dict):
                 # Try to find any keys that look like points or contain 'pixel'
                 # Legacy: x1={'pixel': 100}, x2={'pixel': 200}...
                 # Actually, let's just look for numerical values if others fail
                 if 'x1' in calibration_data:
                     # Legacy specific
                     try:
                        pts = []
                        for key in ['x1', 'x2', 'y1', 'y2']:
                             val = calibration_data.get(key)
                             if isinstance(val, dict): val = val.get('pixel')
                             if val is not None: pts.append(int(val))
                        if len(pts) == 4:
                            # We have x1, x2, y1, y2 coords. Construct rect.
                            x_coords = pts[0:2]; y_coords = pts[2:4]
                            points = [[min(x_coords), min(y_coords)], [max(x_coords), max(y_coords)]]
                     except: pass

            if not points or len(points) < 2:
                print(f"DEBUG: Could not extract valid points from: {calibration_data}")
                return None
            
            print(f"DEBUG: Successfully extracted {len(points)} points: {points}")
                
            # Calculate Bounding Box
            x_coords = [p[0] for p in points]
            y_coords = [p[1] for p in points]
            
            x_min = min(x_coords)
            x_max = max(x_coords)
            y_min = min(y_coords)
            y_max = max(y_coords)
            
            # Valid plot area?
            if x_max <= x_min or y_max <= y_min:
                print(f"DEBUG: Invalid area dimensions: {x_min}-{x_max}, {y_min}-{y_max}")
                return None

            # Add Margin
            margin = 5
            plot_area = {
                'x_min': max(0, x_min - margin),
                'x_max': min(self.width, x_max + margin),
                'y_min': max(0, y_min - margin),
                'y_max': min(self.height, y_max + margin) 
            }
            print(f"DEBUG: Calculated Plot Area: {plot_area}")
            return plot_area
            
        except Exception as e:
            print(f"Error calculating plot area: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _filter_points_in_plot_area(self, points: List[Tuple[int, int]], plot_area: Optional[dict]) -> List[Tuple[int, int]]:
        """Filter points to only include those inside the plot area"""
        if not plot_area:
            return points  # No filtering if plot area not defined
        
        valid_points = []
        for (x, y) in points:
            if (plot_area['x_min'] <= x <= plot_area['x_max'] and
                plot_area['y_min'] <= y <= plot_area['y_max']):
                valid_points.append((x, y))
        
        return valid_points
        
    def detect_axes(self) -> Optional[dict]:
        """
        Detect X and Y axes using Hough Line Transform
        Returns: dict with 'x_axis' and 'y_axis' line coordinates
        """
        # Edge detection - relaxed thresholds for better detection
        edges = cv2.Canny(self.gray, 30, 100, apertureSize=3)
        
        # Hough Line Transform - lowered threshold and increased gap tolerance
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80, 
                                minLineLength=self.width//5, maxLineGap=20)
        
        if lines is None:
            return None
        
        # Separate horizontal and vertical lines
        horizontal_lines = []
        vertical_lines = []
        
        margin = 15 # Ignore lines within 15px of border
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
            
            # Horizontal (close to 0 or 180 degrees)
            if angle < 15 or angle > 165:
                # Filter borders
                if margin < y1 < self.height - margin:
                    horizontal_lines.append((x1, y1, x2, y2, length))
                    
            # Vertical (close to 90 degrees)
            elif 75 < angle < 105:
                # Filter borders
                if margin < x1 < self.width - margin:
                    vertical_lines.append((x1, y1, x2, y2, length))
        
        if not horizontal_lines or not vertical_lines:
            return None
        
        # Find the longest lines (likely to be axes)
        # X-axis: longest horizontal line near bottom
        horizontal_lines.sort(key=lambda l: (l[4], l[1]), reverse=True) # Prioritize Length, then Bottom (large Y)
        x_axis = horizontal_lines[0][:4]  # (x1, y1, x2, y2)
        
        # Y-axis: longest vertical line near left
        # Fix: Sort by Length DESC, then X ASC (small X is left). 
        # So key should be (Length, -X). 
        vertical_lines.sort(key=lambda l: (l[4], -l[0]), reverse=True)
        y_axis = vertical_lines[0][:4]
        
        return {
            'x_axis': x_axis,
            'y_axis': y_axis
        }
    
    def get_axis_endpoints(self, axes: dict) -> dict:
        """
        Extract calibration points from detected axes
        Returns: dict with pixel coordinates for X1, X2, Y1, Y2
        """
        x1, y1, x2, y2 = axes['x_axis']
        # X-axis endpoints
        x_start = (min(x1, x2), y1)
        x_end = (max(x1, x2), y2)
        
        vx1, vy1, vx2, vy2 = axes['y_axis']
        # Y-axis endpoints
        y_start = (vx1, max(vy1, vy2))  # Bottom
        y_end = (vx2, min(vy1, vy2))    # Top
        
        return {
            'x_start': x_start,
            'x_end': x_end,
            'y_start': y_start,
            'y_end': y_end
        }
    
    def detect_curve(self, color_threshold: Optional[Tuple[int, int, int]] = None) -> List[Tuple[int, int]]:
        """
        Detect data points along a curve
        Args:
            color_threshold: BGR color to detect (if None, uses darkest pixels)
        Returns: List of (x, y) pixel coordinates
        """
        if color_threshold is None:
            # Use adaptive thresholding to find dark lines
            _, binary = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            # Color-based detection - increased tolerance for better matching
            lower = np.array([max(0, c - 50) for c in color_threshold])
            upper = np.array([min(255, c + 50) for c in color_threshold])
            mask = cv2.inRange(self.image, lower, upper)
            binary = mask
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return []
        
        # Get the largest contour (likely the main curve)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Extract points
        points = []
        for point in largest_contour:
            x, y = point[0]
            points.append((int(x), int(y)))
        
        # Sort by x-coordinate
        points.sort(key=lambda p: p[0])
        
        # Sample points evenly
        if len(points) > 100:
            step = len(points) // 100
            # Fix list slicing type error by using list comprehension
            points = [points[i] for i in range(0, len(points), step)]
        
        return points
    
    def visualize_detection(self, axes: Optional[dict] = None, points: Optional[List[Tuple[int, int]]] = None) -> np.ndarray:
        """
        Create a visualization of detected axes and curves
        """
        vis = self.image.copy()
        
        if axes:
            # Draw X-axis in red
            x1, y1, x2, y2 = axes['x_axis']
            cv2.line(vis, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            # Draw Y-axis in green
            vx1, vy1, vx2, vy2 = axes['y_axis']
            cv2.line(vis, (vx1, vy1), (vx2, vy2), (0, 255, 0), 2)
        
        if points:
            # Draw detected points in blue
            for x, y in points:
                cv2.circle(vis, (x, y), 2, (255, 0, 0), -1)
        
        return vis
    
    def detect_auto(self, mode: str = 'guided', colors: List[List[int]] = [], n_series: int = 1, detection_method: str = 'color', calibration_points: Optional[dict] = None) -> List[dict]:
        """
        Main entry point for auto-detection called by app.py
        Handles Guided Mode (Color-based) and Automatic Mode (Clustering)
        """
        print(f"DEBUG: detect_auto called with mode={mode}, method={detection_method}")
        
        # 1. Automatic Mode (Legacy / No Colors)
        if mode == 'auto' or not colors:
            return self.detect_multiple_series(n_series)
            
        # 2. Guided Mode (Color Picked)
        series_results = []
        
        # Calculate ROI once
        plot_area = None
        if calibration_points:
            plot_area = self._calculate_plot_area_from_calibration(calibration_points)
            print(f"DEBUG: detect_auto using plot_area: {plot_area}")
        else:
            print("DEBUG: detect_auto called WITHOUT calibration_points")
            
        for i, color in enumerate(colors):
            label = f"Graph {i+1}"
            
            if detection_method == 'color' or detection_method == 'both':
                # V7 Logic returns a LIST of series (Solid + Dashed)
                extracted = self._extract_series_by_color(tuple(color), label, plot_area=plot_area)
                if extracted:
                    series_results.extend(extracted)
                    
            elif detection_method == 'style':
                # Legacy Style extraction (single dict)
                extracted = self._extract_series_by_style(tuple(color), label)
                if extracted:
                    series_results.append(extracted)
                    
        return series_results

    def detect_multiple_series(self, n_series: int = 3, exclude_background: bool = True) -> List[dict]:
        """
        Detect multiple data series using Graph Clustering and ROI Masking (V6 Logic)
        Automatically excludes axis labels, red annotations, and background.
        Separates Solid and Dashed lines based on connectivity.
        """
        # 1. Calculate ROI based on Axes
        axes = self.detect_axes()
        plot_mask = None
        
        if axes:
            endpoints = self.get_axis_endpoints(axes)
            plot_mask = self._get_plot_area_mask(endpoints)
        else:
            # Fallback to central area if no axes found
            plot_mask = np.zeros(self.image.shape[:2], dtype=np.uint8)
            h, w = self.image.shape[:2]
            plot_mask[int(h*0.05):int(h*0.95), int(w*0.05):int(w*0.95)] = 255

        # 2. Get Data Mask (Red Exclusion)
        data_mask, _ = self._get_data_mask_refined(plot_mask)
        
        # 3. Graph Clustering Separation
        series_list = self._detect_series_by_clustering(data_mask)
        
        return series_list

    def _get_plot_area_mask(self, endpoints: dict) -> np.ndarray:
        mask = np.zeros(self.image.shape[:2], dtype=np.uint8)
        
        roi_x1 = int(endpoints['x_start'][0])
        roi_x2 = int(endpoints['x_end'][0])
        roi_y1 = int(endpoints['y_end'][1])
        roi_y2 = int(endpoints['x_start'][1])
        
        roi_x1, roi_x2 = min(roi_x1, roi_x2), max(roi_x1, roi_x2)
        roi_y1, roi_y2 = min(roi_y1, roi_y2), max(roi_y1, roi_y2)
        
        margin = 5
        roi_x1 += margin; roi_x2 -= margin; roi_y1 += margin; roi_y2 -= margin
        
        h, w = mask.shape
        roi_x1 = max(0, min(w, roi_x1))
        roi_x2 = max(0, min(w, roi_x2))
        roi_y1 = max(0, min(h, roi_y1))
        roi_y2 = max(0, min(h, roi_y2))
        
        if roi_x2 > roi_x1 and roi_y2 > roi_y1:
            mask[roi_y1:roi_y2, roi_x1:roi_x2] = 255
        else:
            mask[int(h*0.1):int(h*0.9), int(w*0.1):int(w*0.9)] = 255
        return mask

    def _get_data_mask_refined(self, plot_mask: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        
        # 1. Background Exclude
        lower_bg = np.array([0, 0, 200])
        upper_bg = np.array([180, 50, 255])
        bg_mask = cv2.inRange(hsv, lower_bg, upper_bg)
        
        # 2. Red Color (Text) Exclude
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        
        red_mask = cv2.bitwise_or(mask_red1, mask_red2)
        
        # Combine exclusions
        exclude_mask = cv2.bitwise_or(bg_mask, red_mask)
        data_mask = cv2.bitwise_not(exclude_mask)
        
        # Apply ROI
        if plot_mask is not None:
            data_mask = cv2.bitwise_and(data_mask, plot_mask)
            
        return data_mask, red_mask

    def _detect_series_by_clustering(self, mask: np.ndarray) -> List[dict]:
        # 1. Close small gaps
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # 2. Find Contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        boxes = []
        for i, cnt in enumerate(contours):
            if cv2.contourArea(cnt) < 5: continue
            x, y, w, h = cv2.boundingRect(cnt)
            boxes.append({
                'id': i,
                'rect': (x, y, w, h),
                'w': w, 'h': h,
                'contour': cnt,
                'center': (x + w/2, y + h/2),
                'group_id': i 
            })
            
        # 3. Cluster by Proximity
        dist_threshold = 4.0 
        
        changed = True
        while changed:
            changed = False
            groups = {}
            for b in boxes:
                gid = b['group_id']
                if gid not in groups: groups[gid] = []
                groups[gid].append(b)
                
            group_ids = list(groups.keys())
            for i in range(len(group_ids)):
                for j in range(i+1, len(group_ids)):
                    gid1 = group_ids[i]
                    gid2 = group_ids[j]
                    
                    has_close = False
                    for b1 in groups[gid1]:
                        for b2 in groups[gid2]:
                            dx = max(0, abs(b1['center'][0] - b2['center'][0]) - (b1['w'] + b2['w'])/2)
                            dy = max(0, abs(b1['center'][1] - b2['center'][1]) - (b1['h'] + b2['h'])/2)
                            dist = np.sqrt(dx*dx + dy*dy)
                            if dist < dist_threshold:
                                has_close = True
                                break
                        if has_close: break
                    
                    if has_close:
                        for b in groups[gid2]:
                            b['group_id'] = gid1
                        changed = True
                        break
                if changed: break
                
        # 4. Classify and Extract
        groups = {}
        for b in boxes:
            gid = b['group_id']
            if gid not in groups: groups[gid] = []
            groups[gid].append(b)
            
        series_list = []
        
        # Collect solid and dashed points
        solid_points = []
        dashed_points = []
        
        for gid, group_boxes in groups.items():
            min_x = min(b['rect'][0] for b in group_boxes)
            max_x = max(b['rect'][0] + b['rect'][2] for b in group_boxes)
            total_width = max_x - min_x
            
            # Vertical Artifact Check
            min_y = min(b['rect'][1] for b in group_boxes)
            max_y = max(b['rect'][1] + b['rect'][3] for b in group_boxes)
            total_height = max_y - min_y
            
            if total_height > total_width * 3 and total_width < 10:
                continue # Ignore vertical artifacts
            
            is_solid = total_width > 30
            
            target_list = solid_points if is_solid else dashed_points
            
            for b in group_boxes:
                mask_b = np.zeros(mask.shape, dtype=np.uint8)
                cv2.drawContours(mask_b, [b['contour']], -1, 255, -1)
                pts = self._extract_points_from_mask_internal(mask_b)
                target_list.extend(pts)
        
        # Sort and Create Series Dicts
        if solid_points:
            solid_points = sorted(list(set(solid_points)), key=lambda p: p[0])
            series_list.append({
                'label': 'Solid Line',
                'color': [0, 0, 0], # Default Black/Blue
                'points': solid_points,
                'style': 'solid',
                'count': len(solid_points)
            })
            
        if dashed_points:
            dashed_points = sorted(list(set(dashed_points)), key=lambda p: p[0])
            series_list.append({
                'label': 'Dashed Line',
                'color': [0, 0, 255], # Red indicator for dashed
                'points': dashed_points,
                'style': 'dashed',
                'count': len(dashed_points)
            })
            
        return series_list

    def _extract_points_from_mask_internal(self, mask: np.ndarray) -> List[Tuple[int, int]]:
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
    
    def _extract_series_by_color(self, target_color: Tuple[int, int, int], label: str, plot_area: Optional[dict] = None) -> List[dict]:
        """
        Extract series by color using Clustering Logic (V6) to separate Solid/Dashed
        Returns a LIST of series (dict) because one color might contain multiple separated curves.
        """
        try:
            # Ensure target_color contains native ints
            target_color = tuple(int(c) for c in target_color)
            
            # Convert BGR to HSV
            target_bgr = np.uint8([[list(target_color)]])
            target_hsv = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2HSV)[0][0]
            
            try:
                hsv_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
            except Exception:
                hsv_image = self.image
            
            h, s, v = int(target_hsv[0]), int(target_hsv[1]), int(target_hsv[2])
            
            # Tolerance Refined for V6
            if s > 50:
                # Colorful pixel: Strict on Saturation to avoid Greyscale/Black
                h_tolerance = 20
                s_tolerance = 80
                v_tolerance = 255 # Allow value variation (light/shadow)
                min_saturation = 40 # Force minimum saturation to avoid black/grey
            else:
                # Already low saturation (User clicked grey/black?)
                h_tolerance = 30
                s_tolerance = 120
                v_tolerance = 120
                min_saturation = 0
            
            lower_hsv = np.array([
                max(0, h - h_tolerance),
                max(min_saturation, s - s_tolerance),
                max(0, v - v_tolerance)
            ], dtype=np.uint8)
            upper_hsv = np.array([
                min(180, h + h_tolerance),
                min(255, s + s_tolerance),
                min(255, v + v_tolerance)
            ], dtype=np.uint8)
            
            mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)
            
            # Fallback BGR (Weighted less or intersection?)
            # BGR mask can sometimes include blacks if tolerance is high. 
            # Let's make BGR fallback strict or rely mostly on HSV for color.
            # Only use BGR fallback if saturation is low.
            
            if s > 50:
                # Trust HSV more for colors
                combined_mask = mask
            else:
                bgr_tolerance = 60
                lower_bgr = np.array([max(0, c - bgr_tolerance) for c in target_color], dtype=np.uint8)
                upper_bgr = np.array([min(255, c + bgr_tolerance) for c in target_color], dtype=np.uint8)
                bgr_mask = cv2.inRange(self.image, lower_bgr, upper_bgr)
                combined_mask = cv2.bitwise_or(mask, bgr_mask)
            
            print(f"DEBUG: Initial Color Mask count: {cv2.countNonZero(combined_mask)}")
            
            # Apply ROI Masking IF AVAILABLE, otherwise use heuristics
            roi_rect = None
            if plot_area is not None:
                # Convert plot_area dict to mask
                roi_mask = np.zeros_like(combined_mask)
                roi_mask[int(plot_area['y_min']):int(plot_area['y_max']), 
                         int(plot_area['x_min']):int(plot_area['x_max'])] = 255
                
                print(f"DEBUG: ROI MASK Created: {plot_area}")
                combined_mask = cv2.bitwise_and(combined_mask, roi_mask)
                roi_rect = plot_area 
                print(f"DEBUG: After ROI Mask count: {cv2.countNonZero(combined_mask)}")
            else:
                 print("DEBUG: No Plot Area provided -> Using Full Image with Heuristics")
                 # Heuristic: Mask out likely axis areas (outer 5%) unless strong signal
                 h, w = combined_mask.shape
                 margin_x = int(w * 0.05)
                 margin_y = int(h * 0.05)
                 # Create a central mask
                 central_mask = np.zeros_like(combined_mask)
                 central_mask[margin_y:h-margin_y, margin_x:w-margin_x] = 255
                 combined_mask = cv2.bitwise_and(combined_mask, central_mask)
                 print("DEBUG: Applied Central 90% Mask")

            # Morphological Clean-up (Remove Text/Noise)
            # Text is usually small detached blobs. Lines are long.
            # 1. Open to remove small noise
            kernel_open = np.ones((2,2), np.uint8) 
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel_open)
            
            # 2. Close to bridge small gaps in lines
            kernel_close = np.ones((3,3), np.uint8)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel_close)
            
            # --- V7 LOGIC: Structural Separation (Solid vs Dashed) ---
            print("DEBUG: Executing V7 Structural Separation")
            
            # 1. Find Contours (Components)
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # DEBUG VISUALIZATION
            debug_img = cv2.cvtColor(combined_mask, cv2.COLOR_GRAY2BGR)
            
            solid_segments = []
            dash_candidates = []
            
            # 2. Classify Components by Size/Shape
            min_solid_length = 40 # Increased slightly for robustness
            
            for cnt in contours:
                length = cv2.arcLength(cnt, True)
                area = cv2.contourArea(cnt)
                x,y,w,h = cv2.boundingRect(cnt)
                
                # Filter small noise (likely text artifacts remaining)
                if area < 10 or length < 10: 
                    continue
                    
                # Filter "Square-ish" blobs (Text characters are often square-ish)
                aspect_ratio = float(w)/h if h>0 else 0
                if 0.5 < aspect_ratio < 2.0 and area < 100:
                    # Likely a character/symbol, not a line part
                    continue

                if length > min_solid_length or w > min_solid_length or h > min_solid_length:
                    solid_segments.append(cnt)
                    # Draw Green for Solid
                    cv2.drawContours(debug_img, [cnt], -1, (0, 255, 0), 2)
                else:
                    dash_candidates.append(cnt)
                    # Draw Red for Dashed
                    cv2.drawContours(debug_img, [cnt], -1, (0, 0, 255), -1)
            
            # Save Debug Image to Desktop
            import time
            import os
            desktop = os.path.expanduser("~/Desktop")
            debug_path = os.path.join(desktop, f"debug_v7_components_{int(time.time())}.png")
            cv2.imwrite(debug_path, debug_img)
            print(f"DEBUG: Saved V7 debug image to {debug_path}")
            
            final_list = []
            
            # 3. Process SOLID segments
            if solid_segments:
                # Merge all solid segments into one mask/series
                # (Or keep them separate? Usually one main solid line)
                # Let's merge them for the "Solid" series
                solid_mask = np.zeros_like(combined_mask)
                cv2.drawContours(solid_mask, solid_segments, -1, 255, -1)
                
                # Extract points
                solid_points = self._extract_points_from_mask(solid_mask)
                if len(solid_points) > 5:
                    final_list.append({
                        'label': f"{label} (Solid)",
                        'points': solid_points,
                        'color': [int(c) for c in target_color],
                        'type': 'solid'
                    })
            
            # 4. Process DASH candidates (Grouping)
            if dash_candidates:
                # We need to see if these small blobs form a line (Cluster them)
                # Simple approach: If we have enough dash candidates nearby, treat as dashed line.
                
                # Check 1: Count. A dashed line needs multiple segments.
                if len(dash_candidates) > 3:
                    # Create mask for dashes
                    dash_mask = np.zeros_like(combined_mask)
                    cv2.drawContours(dash_mask, dash_candidates, -1, 255, -1)
                    
                    # Refine: Only keep dashes that are somewhat aligned? 
                    # For V7, let's assume if they passed color filter & ROI & Size check, they are dashes.
                    dash_points = self._extract_points_from_mask(dash_mask)
                    
                    if len(dash_points) > 5:
                        final_list.append({
                            'label': f"{label} (Dashed)",
                            'points': dash_points,
                            'color': [int(c) for c in target_color],
                            'type': 'dashed'
                        })
            
            # Fallback: If V7 failed to split (e.g. everything was "solid"), 
            # just return the original clustering result? 
            # No, if solid_segments found, we are good.
            
            if not final_list:
                print("DEBUG: V7 found nothing, falling back to basic clustering")
                # Fallback to simple clustering
                series_list = self._detect_series_by_clustering(combined_mask)
                for s in series_list:
                    s['label'] = label
                    s['color'] = [int(c) for c in target_color]
                    final_list.append(s)

            # Add Debug ROI helper
            for series in final_list:
                if roi_rect: series['debug_roi'] = roi_rect

            print(f"DEBUG: V7 Result: {len(final_list)} series found.")
            return final_list
            
        except Exception as e:
            print(f"Error in _extract_series_by_color: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _extract_points_from_mask(self, mask: np.ndarray) -> List[Tuple[int, int]]:
        """Extract all non-zero points from a mask (V7 Helper)"""
        y_indices, x_indices = np.nonzero(mask)
        points = []
        # Downsample for performance if needed
        step = 1
        if len(x_indices) > 5000: step = 2
        
        for i in range(0, len(x_indices), step):
            points.append((int(x_indices[i]), int(y_indices[i])))
        
        # Sort by X
        points.sort(key=lambda p: p[0])
        return points
    
    def _detect_line_style(self, points: List[Tuple[int, int]]) -> str:
        """
        Detect if line is solid or dashed based on point distribution
        """
        if len(points) < 10:
            return 'solid'
        
        # Calculate gaps between consecutive points
        gaps = []
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            gaps.append(dist)
        
        # If there are regular large gaps, it's dashed
        gaps = np.array(gaps)
        large_gaps = gaps[gaps > 10]
        
        if len(large_gaps) > len(gaps) * 0.3:  # More than 30% large gaps
            # Check if gaps are somewhat regular
            if len(large_gaps) > 5:
                gap_std = np.std(large_gaps)
                gap_mean = np.mean(large_gaps)
                if gap_std < gap_mean * 0.5:  # Regular pattern
                    return 'dashed'
        
        return 'solid'
    
    def _validate_series(self, series_data: dict) -> bool:
        """
        Validate if detected series is a real data curve
        Returns False for noise/scattered points
        """
        points = series_data['points']
        
        if len(points) < 50:
            return False
        
        # Check horizontal span (should cover reasonable x-range)
        x_coords = [p[0] for p in points]
        x_span = max(x_coords) - min(x_coords)
        min_span = self.width * 0.3  # Should cover at least 30% of image width
        
        if x_span < min_span:
            return False
        
        # Check point density - avoid sparse scattered points
        # Calculate average gap between consecutive x-coordinates
        sorted_points = sorted(points, key=lambda p: p[0])
        x_gaps = []
        for i in range(len(sorted_points) - 1):
            gap = sorted_points[i+1][0] - sorted_points[i][0]
            if gap > 0:  # Skip duplicates
                x_gaps.append(gap)
        
        if x_gaps:
            avg_gap = sum(x_gaps) / len(x_gaps)
            max_gap = max(x_gaps)
            
            # If there are very large gaps, it might be scattered noise
            # Max gap shouldn't be more than 10x the average
            if max_gap > avg_gap * 10 and max_gap > 50:
                return False
        
        return True
    
    def _extract_series_by_style(self, sample_color: Tuple[int, int, int], label: str) -> Optional[dict]:
        """Extract series based on line style (pattern) at clicked location"""
        # Step 1: Analyze pattern at click location (tighter tolerance)
        tolerance = 40  # Reduced from 60
        lower = np.array([max(0, c - tolerance) for c in sample_color])
        upper = np.array([min(255, c + tolerance) for c in sample_color])
        mask = cv2.inRange(self.image, lower, upper)
        
        # Step 2: Find the clicked region pattern
        # Sample a small area to determine if it's solid, dotted, or dashed
        kernel = np.ones((2, 2), np.uint8)
        mask_cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find all contours
        contours, _ = cv2.findContours(mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        if not contours:
            return None
        
        # Step 3: Analyze line continuity for each contour
        valid_points = []
        
        for contour in contours:
            if cv2.contourArea(contour) < 20:  # Skip tiny noise
                continue
            
            # Extract contour points
            points = contour.reshape(-1, 2)
            
            # Check if this is a line (not a blob)
            # Calculate aspect ratio
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = max(w, h) / (min(w, h) + 1)
            
            # Only process elongated shapes (lines)
            if aspect_ratio > 2:
                # Analyze gaps in this contour
                sorted_pts = sorted(points, key=lambda p: p[0])
                
                # Calculate pixel-to-pixel distances
                gaps = []
                for i in range(len(sorted_pts) - 1):
                    dx = sorted_pts[i+1][0] - sorted_pts[i][0]
                    dy = sorted_pts[i+1][1] - sorted_pts[i][1]
                    dist = np.sqrt(dx**2 + dy**2)
                    gaps.append(dist)
                
                if not gaps:
                    continue
                
                avg_gap = np.mean(gaps)
                max_gap = np.max(gaps)
                
                # Classify based on gaps
                # Solid: continuous (small gaps)
                # Dotted/Dashed: has regular breaks
                has_breaks = max_gap > 5
                
                if has_breaks:  # Only include non-solid lines
                    for pt in points:
                        valid_points.append((int(pt[0]), int(pt[1])))
        
        if len(valid_points) < 30:
            return None
        
        # Remove duplicates and sort
        valid_points = sorted(set(valid_points), key=lambda p: p[0])
        
        # Sample if too many
        if len(valid_points) > 200:
            step = len(valid_points) // 200
            # Fix list slicing type error
            valid_points = [valid_points[i] for i in range(0, len(valid_points), step)]
        
        style = self._detect_line_style(valid_points)
        
        return {
            'label': label,
            'color': sample_color,
            'points': valid_points,
            'style': style,
            'count': len(valid_points)
        }
    
    def _extract_series_by_color_and_style(self, sample_color: Tuple[int, int, int], label: str, calibration_points: Optional[dict] = None) -> Optional[dict]:
        """Extract series by BOTH color and line style for precise matching"""
        # Calculate plot area if calibration provided
        plot_area = self._calculate_plot_area_from_calibration(calibration_points) if calibration_points else None
        
        # Step 1: Find a pixel matching the sample color (pseudo-click location)
        tolerance = 35  # Even tighter for initial search
        lower = np.array([max(0, c - tolerance) for c in sample_color])
        upper = np.array([min(255, c + tolerance) for c in sample_color])
        initial_mask = cv2.inRange(self.image, lower, upper)
        
        # Find first non-zero pixel as our "click" location
        coords = cv2.findNonZero(initial_mask)
        if coords is None or len(coords) == 0:
            return None
        
        # Use the first matching pixel as click location
        click_x, click_y = int(coords[0][0][0]), int(coords[0][0][1])
        
        # Step 2: Sample actual color AT that location
        actual_color = self._sample_color_at_click(click_x, click_y, radius=3)
        
        # Step 3: Create mask with actual sampled color (tighter tolerance)
        tolerance = 30
        lower = np.array([max(0, c - tolerance) for c in actual_color])
        upper = np.array([min(255, c + tolerance) for c in actual_color])
        mask = cv2.inRange(self.image, lower, upper)
        
       # Step 4: Extract ONLY connected component containing click location
        mask = self._extract_connected_component(mask, click_x, click_y)
        
        # Step 5: Sample pattern at click location
        expected_pattern = self._sample_pattern_at_click(mask, click_x, click_y, radius=15)
        
        # Step 6: Process contours with pattern matching
        kernel = np.ones((2, 2), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            return None
        
        all_points = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 50:  # Filter noise
                continue
            
            # Get bounding rect for aspect ratio check
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = max(w, h) / (min(w, h) + 1)
            
            # Must be elongated (line-like)
            if aspect_ratio < 2:
                continue
            
            # Extract points
            points_array = contour.reshape(-1, 2)
            points = [(int(pt[0]), int(pt[1])) for pt in points_array]
            
            # Check if this contour's pattern matches expected
            contour_pattern = self._detect_line_style(points)
            
            # Accept if pattern matches OR if it's solid (baseline)
            if contour_pattern == expected_pattern or expected_pattern == 'solid':
                all_points.extend(points)
        
        if len(all_points) < 30:
            return None
        
        # Remove duplicates and sort
        all_points = sorted(set(all_points), key=lambda p: p[0])
        
        # CRITICAL: Filter points to only include those inside plot area
        all_points = self._filter_points_in_plot_area(all_points, plot_area)
        
        if len(all_points) < 10:  # Re-check after filtering
            return None
        
        # Sample if too many
        if len(all_points) > 200:
            step = len(all_points) // 200
            # Fix list slicing type error
            all_points = [all_points[i] for i in range(0, len(all_points), step)]
        
        return {
            'label': label,
            'color': actual_color,
            'points': all_points,
            'style': expected_pattern,
            'count': len(all_points)
        }

import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        pass

    def auto_detect_gap(self, mask_img):
        """
        Tries different gap filling values and returns the best one.
        Best = Minimum number of connected components (ideally 1),
        with valid aspect ratio check if possible.
        """
        best_gap = 1
        min_components = float('inf')
        
        # Test range of gap sizes
        test_gaps = [1, 3, 5, 8, 12, 16]
        
        for gap in test_gaps:
            kernel_size = 2 * gap + 1
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
            closed = cv2.morphologyEx(mask_img, cv2.MORPH_CLOSE, kernel)
            
            # Count connected components
            num_labels, labels = cv2.connectedComponents(closed)
            # num_labels includes background (0), so actual components = num_labels - 1
            components = num_labels - 1
            
            if components < min_components:
                min_components = components
                best_gap = gap
            
            # Optimization: If we hit 1 component, that's likely best (closest to valid line)
            if components == 1:
                break
                
        print(f"DEBUG: Auto-detected gap fill: {best_gap} (components: {min_components})")
        return best_gap

    def process_images(self, original_cv_img, mask_cv_img, hsv_range=None, line_type='auto', gap_fill=None):
        """
        line_type: 'solid', 'manual', or 'auto' (default)
        gap_fill: integer (kernel size parameter) or None
        """
        # 1. Resize mask to match original if needed
        if original_cv_img.shape[:2] != mask_cv_img.shape[:2]:
            mask_cv_img = cv2.resize(mask_cv_img, (original_cv_img.shape[1], original_cv_img.shape[0]))

        # 2. Convert to Mask (Binary)
        if len(mask_cv_img.shape) == 3:
            mask_gray = cv2.cvtColor(mask_cv_img, cv2.COLOR_BGR2GRAY)
        else:
            mask_gray = mask_cv_img
            
        _, roi_mask = cv2.threshold(mask_gray, 10, 255, cv2.THRESH_BINARY)
        
        # 3. Apply Mask to Original
        masked_img = cv2.bitwise_and(original_cv_img, original_cv_img, mask=roi_mask)
        
        # 4. Color Segmentation
        hsv = cv2.cvtColor(masked_img, cv2.COLOR_BGR2HSV)
        
        if hsv_range:
            lower, upper = hsv_range
        else:
            # Default: Dark lines
            lower = np.array([0, 0, 0])
            upper = np.array([180, 255, 100]) 
        
        mask_color = cv2.inRange(hsv, lower, upper)
        
        # Combine with user ROI
        final_mask = cv2.bitwise_and(mask_color, roi_mask)
        
        # 5. Morphological Operations based on Line Type
        if line_type == 'solid':
            # Solid line: Opening to remove small noise
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            closed_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel, iterations=1)
            closed_mask = cv2.morphologyEx(closed_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
            
        else: 
            # Dotted/Dashed or Auto: Use Closing to connect gaps
            
            if line_type == 'auto':
                gap_val = self.auto_detect_gap(final_mask)
            else:
                # Manual
                gap_val = int(gap_fill) if gap_fill is not None else 3
            
            kernel_size = 2 * gap_val + 1
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
            closed_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, kernel)
        
        # 6. Skeletonization
        if hasattr(cv2, 'ximgproc'):
             skeleton = cv2.ximgproc.thinning(closed_mask)
        else:
            # Simple fallback thinning if ximgproc is missing
            skeleton = closed_mask # Fallback, not true thinning but acceptable for simple centers
            # Better fallback: erosion
            # skeleton = cv2.erode(closed_mask, kernel, iterations=1)
        
        # 7. Extract coordinates
        # Old approach: Average Y per X (Failed for vertical lines)
        # New approach: specific non-zero pixels sorted by X
        
        ys, xs = np.nonzero(skeleton)
        # Combine to (x, y) tuples
        raw_points = list(zip(xs, ys))
        
        # Sort by X primarily, then Y
        points = sorted(raw_points, key=lambda p: (p[0], p[1]))
        
        # Filter points to reduce density (remove clumps)
        # Simple distance-based filtering
        filtered_points = []
        if points:
            filtered_points.append(points[0])
            last_p = points[0]
            min_dist_sq = 2.0 * 2.0 # Minimum 2 pixels distance
            
            for p in points[1:]:
                # Euclidean distance squared check
                dist_sq = (p[0] - last_p[0])**2 + (p[1] - last_p[1])**2
                if dist_sq >= min_dist_sq:
                    filtered_points.append(p)
                    last_p = p
                    
        return filtered_points, skeleton

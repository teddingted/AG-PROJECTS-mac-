# Plot Area Detection Feature 🚀

## Overview
We've successfully implemented **Plot Area Detection** to solve the issue of detecting axis labels and legends as data points. The system now uses the calibration points to define a valid "Plot Area" and filters out any detected points outside this region.

## Key Changes

### 1. Calibration-Based Filtering
- **Backend (`auto_detector.py`)**: Added `_calculate_plot_area_from_calibration` to compute the bounding box of the graph from user clicks.
- **Filtering Logic**: Added `_filter_points_in_plot_area` to remove points outside the graph boundaries.
- **Integration**: Updated `_extract_series_by_color_and_style` and other extraction methods to apply this filter.

### 2. Frontend Integration
- **Frontend (`app.js`)**: Updated `runGuidedDetection` to send `calibration` data (pixel coordinates) to the backend during guided mode.
- **API (`app.py`)**: Updated `/detect_auto` endpoint to receive and pass `calibration` data to the `AutoDetector`.

### 3. Code Quality Improvements
- **Lint Fixes**: Resolved 60+ lint errors in `app.py` and `auto_detector.py` including:
    - Fixed list slicing type errors.
    - Improved `Optional` type hints.
    - Fixed `numpy` boolean masking optimization.
    - Fixed `int` casting for color arithmetic.

## How to Test
1. **Calibrate**: Click 4 points (X start/end, Y start/end) on the axes.
2. **Guided Mode**: Select "Guided Mode" and choose a detection method (e.g., "Both").
3. **Verify**: Click on a data series. You should see that:
    - The curve is detected.
    - **Axis numbers** (e.g., 2000, 2010) are **NOT** detected.
    - **Legends** and titles are **NOT** detected.

## Next Steps
- Verify the fix with user testing.
- The codebase is now cleaner and more robust for future feature additions.

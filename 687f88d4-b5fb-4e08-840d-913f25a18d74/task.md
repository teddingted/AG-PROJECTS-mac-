# Tasks: Auto Plot Digitizer (Python)

- [x] Plan and Design
    - [x] Analyze user sketch and requirements
    - [x] **Create Implementation Plan**
    - [x] Review and refine plan with user
- [x] Interface Implementation (Step 1)
    - [x] Set up Python environment and dependencies
    - [x] Create Main Window with Drag & Drop support
    - [x] Implement "Check multiple graphs" logic
- [x] Calibration Logic (Step 2)
    - [x] Implement Image Viewer
    - [x] Create Axis Calibration Tool (X-low, X-high, Y-low, Y-high)
    - [x] Develop pixel-to-value mapping logic
- [x] Data Extraction & Export (Step 3)
    - [x] Implement Data Point selection (manual Click)
    - [x] (Optional) Auto-trace logic (Skipped for first iteration)
    - [x] Create CSV Export function
- [x] Packaging
    - [x] Convert to Windows Executable (PyInstaller) - *Built Mac App, provided Windows instructions*

## Phase 2: Auto-Detection Features
- [x] Auto Calibration
    - [x] Implement axis detection using OpenCV
    - [x] Create auto-calibration workflow
- [x] Auto Data Extraction
    - [x] Implement line/curve detection
    - [x] Extract data points along detected curves
- [x] UI Integration
    - [x] Add "Auto Detect" button
    - [x] Show detection preview
    - [x] Allow manual correction of auto-detected values

## Phase 3: Complete Automation
- [x] OCR Integration (Removed - unreliable for graphs)
- [x] Multi-Series Detection
    - [x] Detect multiple curves by color
    - [x] Detect dashed vs solid lines
    - [x] Separate and label each series
    - [x] Export with series identifiers
    - [x] Improved filtering to exclude text/gridlines
- [x] Full Auto Mode
    - [x] Combine all features into one-click workflow
    - [x] Add "⚡ Full Auto" button
    - [x] Handle errors gracefully with fallback

## Phase 4: Polish
- [x] UI Enhancement
    - [x] Apply cyberpunk/modern styling
    - [x] Improve button aesthetics
    - [x] Add color scheme and gradients
- [x] Detection Improvements
    - [x] Increase dark threshold to exclude gridlines
    - [x] Add saturation check (>0.3) to filter gray pixels
    - [x] Increase minimum contour area to 50
    - [x] Increase minimum points per series to 20

## Phase 5: Guided Semi-Auto Mode ✅
- [x] Guided Mode Implementation
    - [x] Add "🎯 Guided Mode" button
    - [x] Click 4 axis points (X1, X2, Y1, Y2)
    - [x] Enter axis values
    - [x] Specify number of graphs
    - [x] Click start/end points for each graph
    - [x] Extract data only within specified boundaries
    - [x] Visual feedback with orange markers (G1-S, G1-E, etc.)
    - [x] **FIX**: Methods properly placed inside MainWindow class
    - [x] **OPTIMIZATION**: 2-3x faster on large images

## Phase 6: Performance & Bug Fixes ✅
- [x] Fix app crash (guided_mode outside class)
- [x] Performance optimization
    - [x] Auto-resize large images (>1200px)
    - [x] Pixel sampling for K-means (>5000 pixels)
    - [x] Reduce K-means iterations (n_init=3)
    - [x] Early exit on insufficient data
- [x] Final build and deployment

## Phase 7: Web Conversion & Stabilization (Completed)
- [x] Convert Desktop App to Web App
    - [x] Flask Backend Setup
    - [x] Frontend Implementation (HTML/JS/CSS)
    - [x] Port Auto-Detection Algorithms
- [x] Bug Fixes
    - [x] JSON Serialization (CustomJSONEncoder)
    - [x] Guided Mode Color Detection Fixes
    - [x] "0 Series Extracted" Fix (Tolerance Adjustment)
    - [x] Restore Advanced HSV logic (Fix tracking regression)
- [x] Enhancements
    - [x] Center-aligned Line Detection (Mean Y)
    - [x] Relaxed Color Tolerance (Faint Line Detection)
    - [x] Feature: Delete Graph Mode (Interactive Removal)
    - [x] Comprehensive Logging System

# Auto Plot Digitizer - Walkthrough

We have successfully built the Python-based Auto Plot Digitizer with **complete automation, multi-series detection, and cyberpunk UI**!

## Features Implemented

### 1. 🎨 Cyberpunk UI
- **Neon Green Theme**: Vibrant #00ff88 accents on dark background
- **Dark Gradients**: Smooth transitions from #0a0e27 to #16213e
- **Glowing Effects**: Buttons glow on hover with box-shadow
- **Modern Typography**: Monospace fonts for tech aesthetic
- **Immersive Experience**: Full cyberpunk color scheme throughout

### 2. Interface & Image Loading
- **Drag & Drop**: dragging a graph image onto the window loads it instantly.
- **Main Window**: Features a large interactive view area and a control sidebar.

### 3. Manual Calibration
- **Calibration Mode**: Click "Calibrate Axes" to set the reference points.
- **4-Point System**: Sequentially click X1, X2, Y1, Y2.
- **Precise Input**: A dialog asks for the real-world value of each point immediately after all 4 are selected.

### 4. 🤖 Semi-Auto Detection
- **Auto Detect Button**: Automatically detects axes and extracts a single curve
- **User Input**: Still requires axis value ranges
- **Single Series**: Extracts one curve at a time

  2. Extract axis endpoints automatically
  3. **OCR reads axis labels and suggests values**
  4. User confirms or manually enters axis ranges
  5. Detect all series by color clustering
  6. Extract data points for each series
  7. **Display color-coded preview with legend**
  8. Label each series (Series 1, Series 2, etc.)
- **Smart Filtering**: Excludes background and axis pixels
- **Technology**: K-means clustering, morphological operations, contour analysis, OCR

### 6. Digitization & Multiple Graphs
- **Point Extraction**: Click anywhere on the calibrated graph to add a data point (visualized as a blue dot).
- **Coordinate Mapping**: Pixels are automatically converted to graph values using linear interpolation.
- **Multiple Series**: Check "Multiple Graphs" to enable the Graph ID selector. Points added will be tagged with the selected Graph ID.

### 7. Export
- **CSV Output**: Click "Export to CSV" to save your work.
- **Format**: `Graph #, X, Y`
- **Multi-Series Support**: Each series gets its own Graph ID

## Workflows

### Quick Mode (Recommended for Multi-Series):
1. Drag & drop graph image
2. Click "⚡ Full Auto"
3. **Confirm OCR-detected axis values** (or enter manually)
4. Done! All series automatically extracted with color preview

### Semi-Auto Mode (For single series):
1. Drag & drop graph image
2. Click "🤖 Auto Detect"
3. Enter axis ranges
4. Single curve extracted

### Manual Mode (For complex/unusual graphs):
1. Drag & drop graph image
2. Click "Calibrate Axes" and manually select 4 points
3. Click on graph to add points manually
4. Export to CSV

## Technical Details
- **UI**: Cyberpunk theme with PyQt6 stylesheets, neon green/cyan colors
- **OCR**: EasyOCR (primary) or Tesseract (fallback) for axis label reading
- **Axis Detection**: Hough Line Transform finds longest horizontal/vertical lines
- **Multi-Series Detection**: 
  - K-means clustering (scikit-learn) for color separation
  - HSV color space filtering to exclude background
  - Morphological operations for noise reduction
- **Line Style Detection**: Gap pattern analysis for dashed vs solid
- **Curve Tracing**: Adaptive thresholding + contour detection
- **Libraries**: PyQt6, OpenCV, NumPy, scikit-learn, EasyOCR, pytesseract

## Installation & Build
- **Source**: run `python main.py`
- **Build**: A standalone Mac application `AutoPlotDigitizer.app` has been built in `dist/`.
- **Windows**: To build for Windows, copy the source to a Windows machine and run:
  ```bash
  pyinstaller --noconfirm --onefile --windowed --name "AutoPlotDigitizer" --add-data "gui;gui" --add-data "core;core" main.py
  ```

## Future Enhancements
- Improve OCR accuracy for rotated text
- Support for log-scale axes
- Zoom/Pan for better precision
- Batch processing multiple images
- Export to other formats (JSON, Excel)

## Features Implemented

### 1. Interface & Image Loading
- **Drag & Drop**: dragging a graph image onto the window loads it instantly.
- **Main Window**: Features a large interactive view area and a control sidebar.

### 2. Manual Calibration
- **Calibration Mode**: Click "Calibrate Axes" to set the reference points.
- **4-Point System**: Sequentially click X1, X2, Y1, Y2.
- **Precise Input**: A dialog asks for the real-world value of each point immediately after all 4 are selected.

### 3. 🤖 Semi-Auto Detection
- **Auto Detect Button**: Automatically detects axes and extracts a single curve
- **User Input**: Still requires axis value ranges
- **Single Series**: Extracts one curve at a time

### 5. ⚡ **Full Auto Mode**
- **Complete Automation**: Click "⚡ Full Auto" for one-click digitization
- **Manual Axis Input**: User enters axis value ranges (more reliable than OCR)
- **Multi-Series Detection**: Automatically detects and separates multiple graphs by:
  - **Color**: K-means clustering identifies different colored lines
  - **Style**: Distinguishes between solid and dashed lines
  - **Improved Filtering**: Excludes text, gridlines, and background noise
    - Dark threshold increased to 60 (filters more dark pixels)
    - Saturation check >0.3 (excludes gray/unsaturated pixels)
    - Minimum contour area 50 (removes small artifacts)
    - Minimum 20 points per series (ensures valid data)
- **Visual Preview**: After detection, each series is displayed in a different color with:
  - Color-coded points overlaid on the original image
  - Legend showing series names, point counts, and line styles
  - Easy visual verification of detection accuracy

### 6. 🎯 **NEW: Guided Mode** (Maximum Precision)
- **User-Controlled Semi-Auto**: Perfect balance of automation and precision
- **Workflow**:
  1. **Specify Graph Count**: Tell the app how many graphs to extract (1-10)
  2. **Click 4 Axis Points**: Define X-start, X-end, Y-start, Y-end
  3. **Enter Axis Values**: Input the actual values for each axis endpoint
  4. **Click Graph Boundaries**: For each graph, click START and END points
     - Orange markers (G1-S, G1-E, G2-S, G2-E, etc.) show your selections
     - Defines exact X-range for each graph
  5. **Auto-Extract**: App extracts data only within your specified boundaries
- **Benefits**:
  - **Precise Control**: You define exactly where each graph starts and ends
  - **No False Positives**: Only extracts data in the ranges you specify
  - **Perfect for Overlapping Graphs**: Manually separate graphs that overlap
  - **Visual Feedback**: Orange markers show exactly what you've selected
- **Automatic Workflow**:
  1. Detect X and Y axes using OpenCV Hough Line Transform
  2. Extract axis endpoints automatically
  3. Ask user for axis value ranges (X: 0-10, Y: 0-100)
  4. Detect all series by color clustering
  6. **Display color-coded preview with legend**
  7. Label each series (Series 1, Series 2, etc.)
- **Smart Filtering**: Excludes background and axis pixels
- **Technology**: K-means clustering, morphological operations, contour analysis

### 5. Digitization & Multiple Graphs
- **Point Extraction**: Click anywhere on the calibrated graph to add a data point (visualized as a blue dot).
- **Coordinate Mapping**: Pixels are automatically converted to graph values using linear interpolation.
- **Multiple Series**: Check "Multiple Graphs" to enable the Graph ID selector. Points added will be tagged with the selected Graph ID.

### 6. Export
- **CSV Output**: Click "Export to CSV" to save your work.
- **Format**: `Graph #, X, Y`
- **Multi-Series Support**: Each series gets its own Graph ID

## Workflows

### Quick Mode (Recommended for Multi-Series):
1. Drag & drop graph image
2. Click "⚡ Full Auto"
3. Enter axis ranges (4 values)
4. Done! All series automatically extracted

### Semi-Auto Mode (For single series):
1. Drag & drop graph image
2. Click "🤖 Auto Detect"
3. Enter axis ranges
4. Single curve extracted

### Manual Mode (For complex/unusual graphs):
1. Drag & drop graph image
2. Click "Calibrate Axes" and manually select 4 points
3. Click on graph to add points manually
4. Export to CSV

## Technical Details
- **Axis Detection**: Hough Line Transform finds longest horizontal/vertical lines
- **Multi-Series Detection**: 
  - K-means clustering (scikit-learn) for color separation
  - HSV color space filtering to exclude background
  - Morphological operations for noise reduction
- **Line Style Detection**: Gap pattern analysis for dashed vs solid
- **Curve Tracing**: Adaptive thresholding + contour detection
- **Libraries**: PyQt6, OpenCV, NumPy, scikit-learn

## Installation & Build
- **Source**: run `python main.py`
- **Build**: A standalone Mac application `AutoPlotDigitizer.app` has been built in `dist/`.
- **Windows**: To build for Windows, copy the source to a Windows machine and run:
  ```bash
  pyinstaller --noconfirm --onefile --windowed --name "AutoPlotDigitizer" --add-data "gui;gui" --add-data "core;core" main.py
  ```

## Future Enhancements
- Add OCR for automatic axis label reading (Tesseract/EasyOCR)
- Implement detection preview overlay
- Support for log-scale axes
- Zoom/Pan for better precision
- Batch processing multiple images

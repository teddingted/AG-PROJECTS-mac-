# AutoPlotDigitizer V2 - Development Task List

## Initialization
- [x] Create project directory `AutoPlotDigitizerV2`
- [x] Create virtual environment (if needed, or just install deps)
- [x] Create basic file structure (`main.py`, `gui/`, `core/`)
- [x] Create `requirements.txt`

## GUI Implementation (PySide6)
- [x] Implement `MainWindow` with menu and layout
- [x] Implement `ImageCanvas` (QGraphicsView subclass) for zooming/panning
- [x] Implement `CalibrationDialog` (X1, X2, Y1, Y2 input)
- [x] Implement "Pen Tool" for Guided Mode (drawing on a transparent layer)

## Core Logic (OpenCV & NumPy)
- [x] Implement `ImageProcessor` class
- [x] Implement Color Selection logic (HSV range)
- [x] Implement Coordinate Mapping (Pixel -> Data)
- [x] Implement "Guided Extraction" algorithm:
    - [x] Apply color filter
    - [x] Apply user-drawn mask
    - [x] Skeletonize and sort points
    - [x] Handle dashed lines (morphological closing)

## Integration & Refinement
- [x] Connect GUI signals to Core Logic
- [x] Display extracted data in a Table (QTableWidget)
- [x] Plot extracted points back onto the image for verification
- [x] Export to CSV functionality
- [x] Testing with sample plots

## Multi-Series Support
- [ ] Implement `SeriesManager` data structure
- [x] Update `MainWindow` to include Series List UI
- [x] Update `Extract` logic to append to Series List
- [x] Update `ImageCanvas` to draw multiple series with different colors
- [x] Update CSV Export to handle multiple columns (X1, Y1, X2, Y2)
- [x] Update `ImageProcessor`: Add `gap_fill` parameter and Auto-Detect logic
- [x] Update `MainWindow`: Add "Gap Fill" UI (Slider + Auto Checkbox)
- [x] Connect UI to `process_images`
- [ ] Verify with sparse dotted lines







## Packaging
- [x] Create a run script
- [x] Create Desktop Launcher (.command file)

## Windows Porting (V2)
- [x] Create `requirements.txt` for Windows
- [x] Create `AutoPlotDigitizer.spec` for PyInstaller
- [x] Create `BUILD_INSTRUCTIONS.md`
- [ ] Verify standalone executable (User)

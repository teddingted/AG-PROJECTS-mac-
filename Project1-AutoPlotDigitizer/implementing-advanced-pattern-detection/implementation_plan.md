# AutoPlotDigitizer V2 Implementation Plan

## Goal Description
Create a robust, standalone desktop application for digitizing data from plot images. The application will feature a "Guided Mode" allowing users to mask specific areas for extraction, solving previous issues with extracting specific series (e.g., "0 series") and handling noise/interferences. The platform will be Python-based (PySide6 for GUI, OpenCV for processing) to ensure maximum performance and library support.

## User Review Required
> [!IMPORTANT]
> This is a complete rewrite (V2) in a new directory `AutoPlotDigitizerV2`. It does not rely on previous code but implements the "Guided Mode" concept from scratch.

## Proposed Changes

### Core Architecture
The application will follow a Model-View-Controller (MVC) pattern:
- **Model**: `core/image_processing.py`, `core/calibration.py` (Handles data logic)
- **View**: `gui/main_window.py`, `gui/image_canvas.py` (Handles UI and User Interaction)
- **Controller**: `main.py` (Connects signals and slots)

### File Structure
#### [New] AutoPlotDigitizerV2/main.py
- Entry point. Sets up the `QApplication` and `MainWindow`.

#### [New] AutoPlotDigitizerV2/gui/main_window.py
- Main UI layout:
    - Left: Control Panel (Step-by-step wizard: Load -> Calibrate -> Mask -> Extract -> Export)
    - Center: `ImageCanvas` (Interactive view)
    - Bottom/Right: Data Table (Preview of extracted X,Y values)

#### [New] AutoPlotDigitizerV2/gui/image_canvas.py
- Subclass of `QGraphicsView`.
- Supports:
    - Pan/Zoom (Scroll wheel, Drag)
    - Click events for Calibration (4 points)
    - Drawing events for Masking (Pen tool with adjustable size)

#### [New] AutoPlotDigitizerV2/core/calibration.py
- Handles coordinate transformation.
- Methods: `set_calibration_points(screen_points, graph_values)`, `map_screen_to_graph(x, y)`

#### [New] AutoPlotDigitizerV2/core/processor.py
- OpenCV logic.
- Methods:
    - `filter_color(image, hsv_range)`
    - `apply_mask(binary_image, mask_layer)`
    - `extract_points(processed_image)` (Uses skeletonization and sorting)

## Advanced Pattern Matching (Updated)
To handle various line styles (Solid, Dotted, Dashed, Dot-Dash) and sparse data:

### UI Changes
*   **Pattern Selector**: Replace simple "Line Type" with:
    *   **Auto-Detect**: Tries to find the best gap-filling parameter.
    *   **Manual**: Enables a "Gap Fill" slider.
*   **Gap Fill Control**: A slider/spinbox (0px to 20px) to specify how large a gap to connect.

### Processor Logic (`process_images`)
*   **Morphological Closing**: The "Gap Fill" value directly controls the kernel size for morphological closing. `kernel_size = 2 * gap_fill + 1`.
*   **Auto-Detect Algorithm**:
    1.  Extract the masked ROI.
    2.  Iterate through a range of Gap Fill values (e.g., 1, 3, 5, 7, 10).
    3.  For each, compute the standard deviation of valid pixels (or count connected components).
    4.  Select the value that yields a single dominant component without blurring too much (or simply the smallest value that results in < N components).
*   **Solid Line Logic**: If "Solid" is detected/selected, use Morphological *Opening* to remove small noise instead of Closing.

### Key Features
1.  **Guided Mode**: User draws a "mask" (like a highlighter) over the line they want to extract.
2.  **Color Thresholding**: User clicks a pixel to auto-pick HSV range, fine-tune with sliders.
3.  **Dashed Line Handling**: Morphological Closing operation to connect dashes before skeletonizing.
4.  **Data Export**: Save to CSV.

## Verification Plan

### Automated Tests
I will create a script `verify_logic.py` to test the core processing without GUI:
1.  Load a generated test plot (sine wave).
2.  Apply a known calibration.
3.  Run extraction logic.
4.  Assert extracted Y values match $sin(X)$ within $1\%$ tolerance.

### Manual Verification
1.  **Launch**: Run `python main.py`.
2.  **Load**: Open `sample_plot.png`.
3.  **Calibrate**:
    - Click X1, X2, Y1, Y2 on the image axes.
    - Enter values (e.g., 0, 10, 0, 100).
4.  **Mask**:
    - Select "Pen Tool".
    - Draw over the blue line.
5.  **Extract**:
    - Click "Extract Data".
    - Verify red dots appear along the line.
    - Verify data table populates.
6.  **Export**:
    - Click "Save CSV".
    - Verify file content.

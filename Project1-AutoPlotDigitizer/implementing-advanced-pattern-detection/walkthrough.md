# AutoPlotDigitizer V2 - User Guide

This application allows you to digitize plot images by defining the axes and using a "Guided Mode" to select the data curve.

## Installation

1.  Ensure you have Python installed.
2.  Install dependencies:
    ```bash
    pip install PySide6 opencv-python numpy matplotlib
    ```
    (Or use the provided `run.sh` which activates the venv)

## How to Run

### Desktop Launcher (Easiest)
Double-click the **AutoPlotDigitizer** icon on your Desktop.

### Command Line
Execute the run script:
```bash
./run.sh
```
Or run with python directly:
```bash
python main.py
```

## Workflow

### 1. Load Image
Click **Load Image** to select your plot file (PNG, JPG, etc.).

### 2. Calibration
1.  Click **Set Calibration Points (0/4)**.
2.  Click 4 points on the graph axis in this exact order:
    -   **X1**: Start of X-axis
    -   **X2**: End of X-axis
    -   **Y1**: Start of Y-axis
    -   **Y2**: End of Y-axis
3.  Enter the corresponding *data values* in the input fields (e.g., if X goes from 0 to 10, enter 0 and 10).

### 3. Extraction Mask
1.  Click **Draw Mask (Pen)**.
2.  Draw roughly over the line you want to extract. This isolates the area of interest so other lines or text don't interfere.
3.  (Optional) Click **Pick Target Color** to select the line color. If not selected, it defaults to looking for dark lines.

### 4. Extract & Add Series
1.  **Series Name**: Enter a name for the current series (e.g., "blue_line").
2.  **Pattern Mode**:
    -   **Auto-Detect Pattern (Default)**: Automatically tries to find the best setting to connect dashed/dotted lines.
    -   **Manual Gap Fill**: Enables a slider to manually set the "Gap Fill" size (1-20px). Use higher values for sparser dots.
    -   **Solid Line**: optimized for solid lines (removes small noise).
3.  Click **Extract & Add Series**. The application will:
    -   Filter by color (if selected).
    -   Apply morphological operations based on Line Type.
    -   Apply your drawn mask.
    -   Extract points and add them to the **Extracted Series** list.
    -   Draw the points on the image (color-coded).
4.  **Repeat for other lines**:
    -   Click **Clear/Delete Mask** to remove the current mask.
    -   Draw a new mask for the next line.
    -   Pick a new target color if needed.
    -   Change the Series Name and Line Type.
    -   Click **Extract & Add Series** again.


### 5. Managing Series
-   **Delete**: Select a row in the series list and click **Delete Selected Series** to remove it. The image will redraw only the remaining series.
-   **Clear All**: Removes all series data.

### 6. Export
Click **Export All to CSV** to save all series into a single CSV file. The columns will be named `SeriesName_X`, `SeriesName_Y`.

## Tips
-   **Zooming**: Hold **Ctrl** and scroll the mouse wheel to zoom in for precise calibration.
-   **Panning**: Click and drag with the left mouse button (in View Mode) to pan.
-   **Masking**: You don't need to be perfect. Just ensure the yellow highlighter covers the line. The color filter will do the rest.

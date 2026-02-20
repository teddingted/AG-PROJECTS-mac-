# Implementation Plan - Auto Plot Digitizer (Python)

Based on the provided sketch, we will build a desktop application to digitize data from plot images.

## Goal
Create a Python-based GUI application that allows users to:
1.  **Import**: Drag and drop graph images.
2.  **Calibrate**: Define X and Y axes using 4 reference points.
3.  **Digitize**: Extract (x, y) coordinates from the graph.
4.  **Export**: Save the data as a CSV file.
5.  **Distribute**: Package as a Windows application.

## User Review Required
> [!IMPORTANT]
> **GUI Framework Decision**: I propose using **PyQt6** or **PySide6**. It provides a native look and feel on Windows, supports complex custom widgets (like the interactive graph viewer), and handles high-DPI displays better than Tkinter.
> **Confirm**: Does PyQt6 work for you?

## Tech Stack
-   **Language**: Python 3.10+
-   **GUI Framework**: PyQt6 (Creating the Window and Controls)
-   **Image Processing**: OpenCV (processing the image) & NumPy (math)
-   **Packaging**: PyInstaller (to create the .exe)

## Proposed Changes / Architecture

### 1. UI Layout (Step 1 of Sketch)
-   **Main Window**:
    -   Central Widget: `QGraphicsView` for displaying the image and handling interactions.
    -   **Drop Zone**: Overlay or initial state accepting file drag-and-drop.
    -   **Sidebar/Toolbar**:
        -   "Add Graph" Button.
        -   "Check Multiple Graphs" Checkbox (to manage multiple series/layers).

### 2. Calibration Mode (Step 2 of Sketch)
-   **Interaction**: User clicks 4 points in sequence or selects specific axis handlers.
    -   $X_{1}$ (X-low), $X_{2}$ (X-high)
    -   $Y_{1}$ (Y-low), $Y_{2}$ (Y-high)
-   **Input Dialogs**: Popup or sidebar fields to enter the *real-world values* for these pixel coordinates.
-   **Visuals**: Draw axis lines and endpoints on the canvas.

### 3. Digitization & Export (Step 3 of Sketch)
-   **Data Storage**: List of `(pixel_x, pixel_y)` mapped to `(data_x, data_y)`.
-   **Interaction**: Click to add points. Right-click to remove.
-   **Export**:
    -   Format: CSV/Excel.
    -   Columns: `Graph #`, `X`, `Y`.

## Verification Plan
### Automated Tests
-   Unit tests for the Coordinate Mapper (pixel -> value transformation).

### Manual Verification
-   **Flow Test**:
    1.  Drag in a sample plot image.
    2.  Set axes (0, 10 for X; 0, 100 for Y).
    3.  Click a point known to be at (5, 50).
    4.  Verify the exported CSV contains approx `5.0, 50.0`.

# AutoPlotDigitizer V2 - Phase 1 Refactoring Walkthrough

## Summary
I have successfully completed Phase 1 of the V2 refactor. The application architecture has been migrated to a **Model-View-Presenter (MVP)** style pattern, decoupling the core logic from the user interface.

## Changes Deployed

### 1. Unified Project Model
- **New `Project` Class**: Acts as the central source of truth. It manages the `Calibration` state, `Series` list, and `Image` path.
- **Observer Pattern**: The UI (`MainWindow`) now subscribes to the `Project` model. Changes to data (like adding a series) automatically trigger UI updates.

### 2. Enhanced Data Models
- **`Series` Class**: Encapsulates series data (name, color, raw pixels, mapped data points).
- **`Calibration` Class**: Updated to support **Logarithmic Scales** (Log-X and Log-Y).
- **`Calibrator`**: Now handles coordinate mapping logic internally, removing math from the GUI.

### 3. Canvas Improvements
- **`ImageCanvas`**: Added support for clearing specific extracted point items, improving performance and visual correctness when deleting series.

## Verification Results

I verified the changes using an updated test script `tests/verify_logic.py`.

### Automated Test: `verify_logic.py`
- **Linear Extraction**:
    - Synthetic Sine Wave generated.
    - **RMSE**: `0.009` (Pass < 0.05). Excellent accuracy.
- **Log Calibration**:
    - Tested mapping of pixel coordinates to Log-X space.
    - **Result**: Passed. `Px(200)` correctly mapped to `10.0` (Log midpoint of 1 and 100).

## Phase 2: Enhanced Features (Completed)
Implemented user-requested features for better usability:
1.  **Undo Stroke**: Added "Undo" button and logic to remove the last drawn mask path.
2.  **Log Scale UI**: Connected `Log Scale X/Y` checkboxes to calibration logic.

## Phase 3: Advanced Features (Completed)
Added professional-grade features:
1.  **Perspective Correction**:
    -   Implemented Homography transformation using `cv2.findHomography`.
    -   Added "Perspective Mode" to calibration (4-point corners TL/TR/BR/BL).
    -   Verified logic with `tests/verify_perspective.py` (Corners map correctly).
2.  **Project Persistence**:
    -   Implemented `Save Project` and `Open Project` (JSON format).
    -   Saves: Image Path, Calibration (Standard/Perspective/Log), Series Data.
    -   Allows resuming work seamlessly.

## Conclusion
The V2 Refactor is now feature-complete for the core requirements. The application supports:
-   Robust MVP Architecture.
-   Accurate Calibration (Linear, Log, Perspective).
-   Flexible Extraction (Masking, Color, Auto-Gap Fill).
-   Session Management (Save/Load).

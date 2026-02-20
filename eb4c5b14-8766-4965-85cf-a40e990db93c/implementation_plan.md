# AutoPlotDigitizer V2 - Architectural Review & Implementation Plan

## 1. V1 Implementation Review

### Current Status
The V1 codebase (`scratch/AutoPlotDigitizerV2`) is a functional prototype using **PySide6** and **OpenCV**. It successfully demonstrates the core workflow: Load -> Calibrate -> Mask -> Extract.

### Strengths
- **Simplicity**: Easy to understand code structure.
- **Core Functionality**: The "Guided Mode" with user-drawn masks is a powerful localized extraction method.
- **Visual Feedback**: Good use of `QGraphicsScene` to show masks and extracted points overlay.
- **Algorithm**: The morphological operations + skeletonization approach works well for standard lines.

### Weaknesses & Limitations
- **Architecture**:
    - **Tight Coupling**: `MainWindow` handles too much logic (Calibration state, Series storage, Color picking).
    - **State Management**: Application state is scattered across UI widgets and list variables.
    - **Hard to Test**: GUI and logic are intertwined, making unit testing difficult (evidenced by `verify_logic.py` effectively implementing a separate mini-pipeline to test).
- **Calibration**:
    - **Logic**: Uses simple linear interpolation (`(val_x2 - val_x1) / (px_x2 - px_x1)`).
    - **Limitation**: Cannot handle rotated plots (requires Perspective Transform) or Logarithmic scales.
- **Masking**:
    - **Raster-based**: The mask is drawn as a raster `QImage`. This is destructive; you cannot easily "move" a mask stroke or edit it later.
- **Data Model**:
    - **Series Data**: Stored as a list of dictionaries. No type safety or encapsulated logic for operations like "Export" or "Delete".

---

## 2. Proposed V2 Architecture

We will refactor the application to follow a **Model-View-Presenter (MVP)** or **MVVM-lite** pattern to decouple logic from the UI.

### Architectural Diagram

```mermaid
graph TD
    subgraph Core [Core Logic (Pure Python)]
        ProjectModel[Project Model] --> |Holds| SeriesList[List of Series]
        ProjectModel --> |Holds| Calibration[Calibration Model]
        Calibration --> |Implements| CoordTransform[Coordinate Transformer]
        Series[Series Class] --> |Contains| RawData[Raw Points]
        Series --> |Contains| Properties[Name, Color, Style]
        Processor[Image Processor] --> |Stateless| CVOps[OpenCV Operations]
    end

    subgraph GUI [UI Layer (PySide6)]
        MainWindow[Main Window] -- Observer --> ProjectModel
        Canvas[Image Canvas] -- Renders --> ProjectModel
        Controls[Left Panel] -- Edits --> ProjectModel
    end
    
    MainWindow --> |Calls| Processor
    Processor --> |Returns Data to| ProjectModel
```

### Key Components

#### 1. `core.model.Project`
The single source of truth for the application state.
- **Attributes**: `image_path` (str), `calibration` (Calibration object), `series` (List[Series]).
- **Methods**: `add_series()`, `remove_series()`, `clear()`, `to_dict()` (for saving).

#### 2. `core.model.Calibration` (Enhanced)
Handles the mapping between Pixel Space and Data Space.
- **Support for Log Scale**: X/Y axes can be set to Linear or Log.
- **Perspective Transform**: Algorithm upgrade to use 3 or 4 points to compute a Homography matrix if axes are not orthogonal, covering rotated scans.

#### 3. `core.model.Series`
Encapsulates a single extracted dataset.
- **Attributes**: `name`, `color`, `line_style`, `raw_pixels` (list), `data_points` (list).
- **Methods**: `export_to_csv()`.

#### 4. `core.processor.ImageProcessor` (Refined)
- **Path Following**: Add a "Trace" algorithm (e.g., A* or simple neighbor following) as an alternative to "Mask + Threshold" for cleaner lines.
- **Gap Infilling**: Optimize the auto-gap detection.

#### 5. `gui.canvas.VectorCanvas`
- **Vector Masks**: Store masks as `QGraphicsPathItem` objects that can be selected, moved, or deleted individually. This allows non-destructive editing of the ROI.

---

## 3. Implementation Plan

### Phase 1: Refactoring & Foundation (Immediate)
- [ ] **Create Data Models**: Implement `Project`, `Calibration`, `Series` classes in `core/`. 
- [ ] **Migrate Logic**: Move calibration math and CSV export logic from `MainWindow` to `core/`.
- [ ] **Decouple UI**: Update `MainWindow` to instantiate a `Project` model and bind UI events to model updates.

### Phase 2: Enhanced Features
- [ ] **Vector Masking**: Update `ImageCanvas` to manage a list of mask items (paths) explicitly, allowing "Undo" and "Delete specific mask".
- [ ] **Logarithmic Scale**: Add boolean flags `is_log_x`, `is_log_y` to `Calibration` and update the mapping formula.
- [ ] **Zoom/Pan**: Ensure smooth zooming with mouse wheel centered on cursor (current implementation is basic).

### Phase 3: Advanced Capabilities (Roadmap)
- [ ] **Perspective Correction**: UI to set 4 corners of the graph area to deskew rotated images.
- [ ] **Project Save/Load**: Save the entire state (image path, calibration, masks, series) to a JSON/Pickle file to resume work later.

## 4. Verification Plan

### Automated Tests
We will add `pytest` based unit tests for the Core modules:
- **Test Calibration**:
    - Input known pixel/data pairs.
    - Assert `map_to_data` returns expected values within tolerance (including Log scale).
- **Test Project Model**:
    - Verify adding/removing series updates the list.
    - Verify serialization (for save/load).

### Manual Verification
- **Load Workflow**: Load image, set calibration, ensure UI updates.
- **Extraction**:
    - Draw a mask.
    - Extract.
    - Verify points appear on canvas.
    - Verify CSV export matches extracted data.
- **Refactor Check**: Ensure no regression in existing functionality.


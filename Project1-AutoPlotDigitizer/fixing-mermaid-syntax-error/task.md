# AutoPlotDigitizer Enhancement

## Phase 0: Recovery (Completed)
- [x] Recover/Reconstruct `gui/main_window.py` [x]
    - [x] Re-implement `class MainWindow` and `__init__`
    - [x] Restore UI layout (Sidebar + Image Canvas)
    - [x] Integrate existing methods (`guided_mode`, etc.)

## Phase 1: Advanced Pattern Recognition (Desktop)
- [x] Analyze existing detection logic (solid lines) [x]
- [x] Design Pattern Recognition Architecture [x]
    - [x] Define `LinePattern` enum (Solid, Dashed, Dotted)
    - [x] Design gap-filling algorithm for non-solid lines
- [x] Implement Advanced Detection [x]
    - [x] Update `ImageProcessor` to handle morphological operations for bridging gaps
    - [x] Implement `detect_dashed` and `detect_dotted` logic
- [x] Update GUI [x]
    - [x] Add "Pattern Selector" dropdown in Main Window
    - [x] Connect UI signals to new backend logic
- [x] Verification [x]
    - [x] Create synthetic test images (dashed/dotted)
    - [x] Run `test_pattern_detection.py` to verify logic

## Phase 2: Web Version Alignment (In Progress)
- [x] Port new `auto_detector.py` logic to Web backend [x]
- [x] Update Web UI (HTML/JS) for Pattern Selector [x]
- [x] Port new `auto_detector.py` logic to Web backend [x]
- [x] Update Web UI (HTML/JS) for Pattern Selector [x]
- [x] Verify Web Version [x]
    - [x] Sync full `detect_multiple_series` logic from Desktop [x]
    - [x] Re-run `test_web_logic.py` [x]

# Project Wrap-up & Reporting (Completed)
- [x] Analyze AutoPlotDigitizer (Python) [x]
- [x] Generate Project Report [x]
- [x] Analyze AutoPlotDigitizer (Web)
- [x] Create & Refine Final Report (project_report.md)

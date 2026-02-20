# AutoPlotDigitizer Enhancement Plan - Phase 2 (Web)

## Goal
Port the Advanced Pattern Recognition (Dashed/Dotted lines) features from the Desktop version to the Web version, ensuring feature parity while maintaining the stability of the Desktop version in the library.

## Proposed Changes

### 1. Backend Logic
#### [MODIFY] [core/auto_detector.py](file:///Users/dm_chamber/.gemini/antigravity/scratch/AutoPlotDigitizerWeb/core/auto_detector.py)
- **Status**: Currently lacks `pattern` support.
- **Change**: Port the updated `detect_multiple_series` and `_extract_series_by_color` methods from the Desktop version.
    - Add `pattern` argument.
    - Implement adaptive morphological operations (kernel size adjustment) for dashed/dotted lines.

### 2. API Endpoint
#### [MODIFY] [app.py](file:///Users/dm_chamber/.gemini/antigravity/scratch/AutoPlotDigitizerWeb/app.py)
- **Change**: Update `/detect_auto` route.
    - Extract `pattern` parameter from request JSON (default: 'Auto-Detect').
    - Pass `pattern` to `AutoDetector`.

### 3. Frontend UI
#### [MODIFY] [web/templates/index.html](file:///Users/dm_chamber/.gemini/antigravity/scratch/AutoPlotDigitizerWeb/web/templates/index.html)
- Add "Pattern Selector" `<select>` element to the control panel.
    - Options: "Auto-Detect", "Solid Line", "Dashed Line", "Dotted Line".

#### [MODIFY] [web/static/js/app.js](file:///Users/dm_chamber/.gemini/antigravity/scratch/AutoPlotDigitizerWeb/web/static/js/app.js)
- Update `detectData()` function to read the selected pattern.
- Include `pattern` in the POST request body to `/detect_auto`.

## Verification Plan

### Manual Verification
1.  **Start Server**: Run `python app.py`.
2.  **Load Image**: Upload `test_patterns.png` (created in Phase 1).
3.  **Test Patterns**:
    - Select "Dashed Line" -> Verify Red Dashed line is detected.
    - Select "Dotted Line" -> Verify Green Dotted line is detected.
4.  **No Regression**: Verify "Solid Line" and "Auto-Detect" still work.

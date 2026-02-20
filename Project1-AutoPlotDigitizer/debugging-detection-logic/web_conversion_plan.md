# Web-Based AutoPlotDigitizer Implementation Plan

## Problem
PyInstaller .app crashes on M4 MacBook Air (macOS 26.2) due to packaging issues and Gatekeeper restrictions.

## Solution
Convert to **web-based application** that runs in browser:
- ✅ Works on Windows, Mac, Linux
- ✅ No packaging/signing issues
- ✅ Easy to distribute (just run Python script)
- ✅ Modern, responsive UI

---

## Architecture

### Backend: Flask (Python)
- Serve web interface
- Handle image uploads
- Run detection algorithms (existing code)
- Generate CSV downloads

### Frontend: HTML + JavaScript
- Drag & drop image upload
- Interactive canvas for clicking points
- Real-time preview
- Modern, responsive design

---

## Implementation Steps

### 1. Backend Setup (Flask)

#### `app.py` - Main Flask Server
```python
from flask import Flask, render_template, request, jsonify, send_file
from core.auto_detector import AutoDetector
import cv2
import numpy as np
import base64
```

**Endpoints:**
- `GET /` - Serve main page
- `POST /upload` - Handle image upload
- `POST /detect` - Run auto detection
- `POST /calibrate` - Store calibration data
- `POST /export` - Generate CSV download

### 2. Frontend Structure

```
web/
├── templates/
│   └── index.html       # Main page
├── static/
│   ├── css/
│   │   └── style.css    # Modern styling
│   ├── js/
│   │   └── app.js       # Interactive logic
│   └── images/
```

### 3. Features to Implement

#### Phase 1: Basic Functionality
- [x] Image upload (drag & drop)
- [x] Display image on canvas
- [x] Click to select calibration points
- [x] Manual data point selection
- [x] CSV export

#### Phase 2: Auto Detection
- [x] Full Auto mode
- [x] Guided Mode
- [x] Multi-series detection
- [x] Visual preview with colors

#### Phase 3: Polish
- [x] Modern UI (similar to current design)
- [x] Progress indicators
- [x] Error handling
- [x] Responsive design

---

## File Structure

```
AutoPlotDigitizerWeb/
├── app.py                 # Flask server
├── core/                  # Existing detection code (reuse)
│   └── auto_detector.py
├── web/
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── uploads/               # Temporary image storage
├── requirements.txt
└── README.md
```

---

## Running the App

### Development
```bash
python app.py
# Opens browser to http://localhost:5000
```

### Distribution
1. User downloads folder
2. Runs `python app.py`
3. Browser opens automatically
4. Works on any OS with Python

---

## Advantages

✅ **Cross-platform**: Windows, Mac, Linux
✅ **No packaging**: Just Python + browser
✅ **No security issues**: No code signing needed
✅ **Easy updates**: Just replace files
✅ **Modern UI**: Web technologies
✅ **Familiar**: Everyone has a browser

---

## Migration Strategy

1. **Reuse existing code**: `core/auto_detector.py` works as-is
2. **New interface**: Replace PyQt6 with HTML/JS
3. **Keep features**: All 3 modes (Full Auto, Guided, Manual)
4. **Test thoroughly**: Ensure all functionality works

---

## Timeline

- **Setup Flask + basic UI**: 30 min
- **Image upload + display**: 20 min
- **Calibration logic**: 30 min
- **Auto detection integration**: 40 min
- **Guided mode**: 40 min
- **Polish + testing**: 30 min

**Total**: ~3 hours

---

## Next Steps

1. Create `AutoPlotDigitizerWeb/` directory
2. Set up Flask server
3. Build HTML interface
4. Integrate existing detection code
5. Test all features
6. Create simple launch script

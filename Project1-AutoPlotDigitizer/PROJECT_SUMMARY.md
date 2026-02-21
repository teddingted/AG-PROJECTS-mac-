# Project 1: Auto Plot Digitizer
> *Comprehensive Portfolio Summary*

## 📌 Project Overview
**Auto Plot Digitizer** is a robust application designed to digitize plot images by allowing users to define axes and use "Guided Mode" to select and extract data curves. It translates visual data from graphs into numerical data points (CSV format) using computer vision algorithms and a user-friendly GUI.

## 🛠️ Tech Stack & Key Technologies
- **Language**: Python 3
- **GUI Framework**: PySide6 (Qt for Python)
- **Computer Vision**: OpenCV (`opencv-python`)
- **Data & Math**: NumPy, Matplotlib
- **Web Port**: HTML, CSS, JavaScript (Flask backend)
- **Packaging**: PyInstaller (for Windows `.exe` and macOS standalone builds)

## ✨ Performed Tasks & Features
1. **Core Detection Logic**: Implemented advanced pattern detection, color filtering, clustering, and skeletonization to accurately identify and isolate line artifacts from complex graphs.
2. **Axis Calibration**: Developed a 4-point calibration system (X start/end, Y start/end) to compute a valid "Plot Area" and filter out extraneous points like legends or axis labels.
3. **Advanced Pattern Control**: Introduced a UI for gap-filling dashed/dotted lines and solid line extraction modes.
4. **Project Persistence**: Added ability to save and load projects (images, calibration, and series data) using JSON serialization.
5. **Interactive UI**: Implemented features like zooming, panning, target color picking, and masking (drawing over lines to isolate areas of interest).

## 📁 Project Structure
- `AutoPlotDigitizerWeb/`: Web-based version of the digitizer using Flask and JavaScript.
- `AutoPlotDigitizerV1_Windows_Port/` & `AutoPlotDigitizerV2_Windows_Port/`: Packaged executable builds and source adaptations for Windows.
- Multiple tracking directories containing AI conversation logs, walkthroughs, experimental CV models (`experiment_models_v*.py`), and implementation plans.

## 📈 Project Outcomes & Achievements
- Solved the critical issue of distinguishing data curves from background noise and axes.
- Successfully built a highly accurate, deployable desktop tool for data extraction from legacy visual plots.
- Created cross-platform delivery methods (Desktop GUI, Web interface, and standalone packaged apps).
- Maintained a clean, well-documented, and extensible codebase following module-driven refactoring.

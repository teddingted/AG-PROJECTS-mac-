# AutoPlotDigitizer Web

🌐 **Cross-Platform Graph Data Extraction Tool**

Extract data from graph images using your web browser. Works on Windows, Mac, and Linux!

## ✨ Features

- 📤 **Drag & Drop Image Upload**
- 🎯 **Axis Calibration** - Click 4 points to calibrate
- ⚡ **Full Auto Mode** - Automatic detection of multiple series
- 🎯 **Guided Mode** - Semi-automatic with user-defined boundaries
- ✏️ **Manual Mode** - Click individual data points
- 📊 **CSV Export** - Download extracted data
- 🎨 **Modern UI** - Beautiful, responsive design

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
python app.py
```

The app will automatically open in your browser at `http://localhost:5000`

## 📖 How to Use

### Step 1: Upload Image
- Drag and drop a graph image, or click to browse

### Step 2: Calibrate Axes
1. Click "🎯 Calibrate Axes"
2. Click 4 points in order:
   - X-axis START (left)
   - X-axis END (right)
   - Y-axis START (bottom)
   - Y-axis END (top)
3. Enter the actual values for these points

### Step 3: Extract Data

Choose one of three modes:

#### ⚡ Full Auto Mode
- Automatically detects and extracts all graph series
- Best for clean, well-separated graphs

#### 🎯 Guided Mode
- You specify how many graphs to extract
- Click START and END points for each graph
- Best for overlapping or complex graphs

#### ✏️ Manual Mode
- Click individual data points
- Best for precise control or simple graphs

### Step 4: Export
- Click "📥 Export CSV" to download your data

## 🖥️ System Requirements

- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- 2GB RAM minimum

## 📁 Project Structure

```
AutoPlotDigitizerWeb/
├── app.py                 # Flask server
├── core/                  # Detection algorithms
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
└── requirements.txt
```

## 🌟 Advantages

✅ **Cross-Platform** - Works on Windows, Mac, Linux
✅ **No Installation** - Just Python + browser
✅ **No Security Issues** - No code signing needed
✅ **Easy to Share** - Send folder to anyone
✅ **Modern UI** - Beautiful, responsive design

## 🔧 Troubleshooting

### Port Already in Use
If port 5000 is busy, edit `app.py` and change:
```python
app.run(debug=True, port=5000)  # Change 5000 to another port
```

### Browser Doesn't Open
Manually navigate to: `http://localhost:5000`

## 📝 License

MIT License - Free to use and modify

## 🙏 Credits

Built with Flask, OpenCV, and scikit-learn

// Global state
let state = {
    image: null,
    imageData: null,
    canvas: null,
    ctx: null,
    mode: 'view', // view, calibrate, guided, manual
    calibrationPoints: [],
    calibrationValues: null,
    guidedBoundaries: [],
    guidedColors: [],  // NEW: for color-based guided mode
    guidedNumGraphs: 0,
    detectionMethod: 'color',  // NEW: 'color', 'style', or 'both'
    manualPoints: [],
    detectedData: []
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    setupEventListeners();
});

function initializeElements() {
    state.canvas = document.getElementById('image-canvas');
    state.ctx = state.canvas.getContext('2d');
}

function setupEventListeners() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');

    // Upload area click
    uploadArea.addEventListener('click', () => fileInput.click());

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            handleImageUpload(file);
        }
    });

    // File input change
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (file) {
            await handleImageUpload(file);
            fileInput.value = ''; // Reset to allow re-uploading same file
        }
    });

    // Canvas click
    state.canvas.addEventListener('click', handleCanvasClick);

    // Button clicks
    document.getElementById('calibrate-btn').addEventListener('click', startCalibration);
    document.getElementById('guided-btn').addEventListener('click', startGuidedMode);
    document.getElementById('manual-btn').addEventListener('click', startManualMode);
    document.getElementById('export-btn').addEventListener('click', exportCSV);
    document.getElementById('clear-btn').addEventListener('click', clearAll);

    // Line style sorting buttons
    document.getElementById('sort-color-btn').addEventListener('click', () => sortSeries('color'));
    document.getElementById('sort-style-btn').addEventListener('click', () => sortSeries('style'));
    document.getElementById('sort-both-btn').addEventListener('click', () => sortSeries('both'));

    // Modal buttons
    document.getElementById('cancel-cal-btn').addEventListener('click', () => {
        document.getElementById('calibration-modal').classList.remove('active');
        state.mode = 'view';
        updateModeDisplay();
    });

    document.getElementById('confirm-cal-btn').addEventListener('click', confirmCalibration);

    // Detection method modal buttons
    document.getElementById('method-color-btn').addEventListener('click', () => selectDetectionMethod('color'));
    document.getElementById('method-style-btn').addEventListener('click', () => selectDetectionMethod('style'));
    document.getElementById('method-both-btn').addEventListener('click', () => selectDetectionMethod('both'));
}

async function handleImageUpload(file) {
    showLoading(true);

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            state.imageData = data;
            loadImageToCanvas(data.image, data.width, data.height);

            // Show sections
            document.getElementById('canvas-section').style.display = 'block';
            document.getElementById('controls-section').style.display = 'block';

            // Update info
            document.getElementById('image-info').textContent =
                `Image: ${data.width} × ${data.height} px`;
        } else {
            alert('Upload failed: ' + data.error);
        }
    } catch (error) {
        alert('Upload error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function loadImageToCanvas(imageSrc, width, height) {
    const img = new Image();
    img.onload = () => {
        state.canvas.width = width;
        state.canvas.height = height;
        state.ctx.drawImage(img, 0, 0);
        state.image = img;
    };
    img.src = imageSrc;
}

function handleCanvasClick(e) {
    const rect = state.canvas.getBoundingClientRect();

    // Support CSS scaling (width: 100%)
    const scaleX = state.canvas.width / rect.width;
    const scaleY = state.canvas.height / rect.height;

    // Calculate accurate image coordinates
    const x = Math.floor((e.clientX - rect.left) * scaleX);
    const y = Math.floor((e.clientY - rect.top) * scaleY);

    if (state.mode === 'calibrate') {
        if (state.calibrationPoints.length < 4) {
            state.calibrationPoints.push([x, y]);
            drawMarker(x, y, state.calibrationPoints.length, '#FF6B6B');

            if (state.calibrationPoints.length === 4) {
                document.getElementById('calibration-modal').classList.add('active');
            }
        }
    } else if (state.mode === 'guided') {
        // Get pixel color at click position
        const imageData = state.ctx.getImageData(x, y, 1, 1);
        const [r, g, b] = imageData.data;
        const color = [b, g, r];  // Convert RGB to BGR for OpenCV

        state.guidedColors.push(color);
        console.log('Added color:', color, 'Total:', state.guidedColors.length);
        const graphNum = state.guidedColors.length;

        // Draw marker with the picked color
        drawMarker(x, y, `G${graphNum}`, `rgb(${r},${g},${b})`);

        // Show picked color info
        showColorInfo(x, y, r, g, b, graphNum);

        // Check if all colors collected
        if (state.guidedColors.length === state.guidedNumGraphs) {
            runGuidedDetection();
        }
    } else if (state.mode === 'manual') {
        state.manualPoints.push([x, y]);
        drawMarker(x, y, state.manualPoints.length, '#4ECDC4');
    }
}

function drawMarker(x, y, label, color) {
    state.ctx.fillStyle = color;
    state.ctx.beginPath();
    state.ctx.arc(x, y, 5, 0, 2 * Math.PI);
    state.ctx.fill();

    state.ctx.fillStyle = 'white';
    state.ctx.font = 'bold 12px Arial';
    state.ctx.fillText(label, x + 8, y - 8);
}

function startCalibration() {
    state.mode = 'calibrate';
    state.calibrationPoints = [];
    redrawCanvas();
    updateModeDisplay();
    alert(`Click 4 points:
1. X-axis START (left)
2. X-axis END (right)
3. Y-axis START (bottom)
4. Y-axis END (top)`);
}

async function confirmCalibration() {
    const x1Val = parseFloat(document.getElementById('x1-val').value);
    const x2Val = parseFloat(document.getElementById('x2-val').value);
    const y1Val = parseFloat(document.getElementById('y1-val').value);
    const y2Val = parseFloat(document.getElementById('y2-val').value);

    state.calibrationValues = [x1Val, x2Val, y1Val, y2Val];

    // Send to backend
    await fetch('/calibrate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            points: state.calibrationPoints,
            values: state.calibrationValues
        })
    });

    document.getElementById('calibration-modal').classList.remove('active');
    state.mode = 'view';
    updateModeDisplay();

    // Enable detection buttons (removed full-auto)
    document.getElementById('guided-btn').disabled = false;
    document.getElementById('manual-btn').disabled = false;

    alert('Calibration complete! You can now use detection modes.');
}



function startGuidedMode() {
    // Show detection method modal first
    document.getElementById('detection-method-modal').classList.add('active');
}

function selectDetectionMethod(method) {
    state.detectionMethod = method;
    document.getElementById('detection-method-modal').classList.remove('active');

    const numGraphs = prompt('How many graphs do you want to extract?', '2');
    if (!numGraphs) return;

    state.guidedNumGraphs = parseInt(numGraphs);
    state.guidedColors = [];  // Store picked colors
    state.mode = 'guided';
    redrawCanvas();
    updateModeDisplay();

    let methodText = method === 'color' ? 'color' : method === 'style' ? 'line style' : 'color + style';
    alert(`Detection method: ${methodText}\n\nClick on each graph to pick its ${method === 'style' ? 'line pattern' : 'color'}.\n\nClicks needed: ${numGraphs}`);
}

async function runGuidedDetection() {
    showLoading(true);

    // Validate state
    if (!state.guidedColors || state.guidedColors.length === 0) {
        alert('Error: No colors collected. Please try again.');
        showLoading(false);
        return;
    }

    console.log('Running Guided Detection with colors:', state.guidedColors);

    try {
        const response = await fetch('/detect_auto', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mode: 'guided',
                colors: state.guidedColors,
                n_series: state.guidedNumGraphs,
                detection_method: state.detectionMethod,  // NEW: pass detection method
                calibration: {
                    points: state.calibrationPoints,
                    values: state.calibrationValues
                }
            })
        });

        const data = await response.json();

        if (data.success) {
            // Detect line styles for each series
            data.series.forEach(series => {
                series.lineStyle = detectLineStyle(series.points);
            });

            visualizeSeries(data.series);
            prepareDataForExport(data.series);
            state.mode = 'view';
            updateModeDisplay();

            // Show line style options
            document.getElementById('line-style-options').style.display = 'block';

            // VISUALIZE ROI if present, else just log
            let roi_msg = "";
            if (data.series.length > 0) {
                if (data.series[0].debug_roi) {
                    // Draw Green ROI Box
                    state.ctx.strokeStyle = '#00FF00';
                    state.ctx.lineWidth = 2;
                    let roi = data.series[0].debug_roi;
                    state.ctx.strokeRect(roi.x_min, roi.y_min, roi.x_max - roi.x_min, roi.y_max - roi.y_min);
                    roi_msg = " [ROI: Active]";
                } else {
                    // No ROI returned - Use Robust Mode
                    roi_msg = " [Mode: Robust Full-Image]";
                }
            }

            alert(`Extracted ${data.series.length} series!${roi_msg}`);
        } else {
            alert('Detection failed: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        showLoading(false);
        alert('An error occurred during detection.');
    } finally {
        showLoading(false);
    }
}

// Debug Image Button Handler
document.getElementById('btn-debug-image').addEventListener('click', async () => {
    // Reuse guided detection but emphasize debug
    alert("Generating Debug Image on Desktop...\n(Check for 'debug_v7_components_*.png')");
    await runGuidedDetection();
});

function startManualMode() {
    state.mode = 'manual';
    state.manualPoints = [];
    redrawCanvas();
    updateModeDisplay();
    alert('Click on data points. Click "Export CSV" when done.');
}

function visualizeSeries(seriesList) {
    redrawCanvas();

    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'];

    seriesList.forEach((series, idx) => {
        const color = colors[idx % colors.length];
        state.ctx.fillStyle = color;

        series.points.forEach(([x, y]) => {
            state.ctx.beginPath();
            state.ctx.arc(x, y, 2, 0, 2 * Math.PI);
            state.ctx.fill();
        });
    });
}

function prepareDataForExport(seriesList) {
    state.detectedData = [];

    seriesList.forEach((series, graphId) => {
        series.points.forEach(([x, y]) => {
            state.detectedData.push({ x, y, graph_id: graphId + 1 });
        });
    });

    displayDataTable();
    document.getElementById('export-btn').disabled = false;
}

function displayDataTable() {
    const dataSection = document.getElementById('data-section');
    const statsDiv = document.getElementById('data-stats');
    const tableContainer = document.querySelector('.table-container');

    // Clear existing content
    tableContainer.innerHTML = '';

    // Group points by graph_id
    const groupedData = {};
    state.detectedData.forEach(point => {
        const gid = point.graph_id;
        if (!groupedData[gid]) groupedData[gid] = [];
        groupedData[gid].push(point);
    });

    // Create table for each graph
    Object.keys(groupedData).sort().forEach(graphId => {
        const points = groupedData[graphId];

        const graphSection = document.createElement('div');
        graphSection.className = 'graph-table-section';
        graphSection.innerHTML = `
            <h3>Graph ${graphId} (${points.length} points)</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Index</th>
                        <th>X (pixels)</th>
                        <th>Y (pixels)</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        `;

        const tbody = graphSection.querySelector('tbody');
        const displayPoints = points.slice(0, 50);  // Show first 50

        displayPoints.forEach((point, idx) => {
            const row = tbody.insertRow();
            row.insertCell(0).textContent = idx + 1;
            row.insertCell(1).textContent = point.x.toFixed(2);
            row.insertCell(2).textContent = point.y.toFixed(2);
        });

        if (points.length > 50) {
            const moreRow = tbody.insertRow();
            const cell = moreRow.insertCell(0);
            cell.colSpan = 3;
            cell.textContent = `... and ${points.length - 50} more points`;
            cell.style.textAlign = 'center';
            cell.style.fontStyle = 'italic';
            cell.style.color = '#666';
        }

        tableContainer.appendChild(graphSection);
    });

    statsDiv.textContent = `Total: ${state.detectedData.length} points across ${Object.keys(groupedData).length} graph(s)`;
    dataSection.style.display = 'block';
}

async function exportCSV() {
    if (state.detectedData.length === 0 && state.manualPoints.length === 0) {
        alert('No data to export!');
        return;
    }

    let points = state.detectedData;

    // If manual mode, use manual points
    if (state.manualPoints.length > 0) {
        points = state.manualPoints.map(([x, y]) => ({ x, y, graph_id: 1 }));
    }

    showLoading(true);

    try {
        const response = await fetch('/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ points })
        });

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'digitized_data.csv';
        a.click();

        alert('CSV exported successfully!');
    } catch (error) {
        alert('Export error: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function clearAll() {
    if (!confirm('Clear all data and start over?')) return;

    state.calibrationPoints = [];
    state.calibrationValues = null;
    state.guidedBoundaries = [];
    state.manualPoints = [];
    state.detectedData = [];
    state.mode = 'view';

    redrawCanvas();
    updateModeDisplay();

    document.getElementById('guided-btn').disabled = true;
    document.getElementById('manual-btn').disabled = true;
    document.getElementById('export-btn').disabled = true;
    document.getElementById('data-section').style.display = 'none';
    document.getElementById('line-style-options').style.display = 'none';
}

// Line style detection
function detectLineStyle(points) {
    if (!points || points.length < 10) return 'solid';

    // Sort points by x coordinate
    const sorted = [...points].sort((a, b) => a[0] - b[0]);

    // Calculate gaps between consecutive points
    const gaps = [];
    for (let i = 1; i < sorted.length; i++) {
        const dx = sorted[i][0] - sorted[i - 1][0];
        const dy = sorted[i][1] - sorted[i - 1][1];
        const gap = Math.sqrt(dx * dx + dy * dy);
        gaps.push(gap);
    }

    if (gaps.length === 0) return 'solid';

    const avgGap = gaps.reduce((a, b) => a + b, 0) / gaps.length;
    const maxGap = Math.max(...gaps);
    const largeGaps = gaps.filter(g => g > avgGap * 2).length;

    // Classification logic
    if (maxGap < 5) {
        return 'solid';
    } else if (largeGaps > gaps.length * 0.3) {
        // More than 30% large gaps
        if (avgGap < 10) {
            return 'dotted';
        } else {
            return 'dashed';
        }
    }

    return 'solid';
}

// Sort series by color, style, or both
function sortSeries(method) {
    if (!state.detectedData || state.detectedData.length === 0) {
        alert('No data to sort!');
        return;
    }

    // Group by graph_id to get series
    const groupedData = {};
    state.detectedData.forEach(point => {
        const gid = point.graph_id;
        if (!groupedData[gid]) groupedData[gid] = [];
        groupedData[gid].push(point);
    });

    // Get series info
    const series = Object.keys(groupedData).map(gid => ({
        id: parseInt(gid),
        points: groupedData[gid],
        color: state.guidedColors[parseInt(gid) - 1] || [0, 0, 0],
        lineStyle: detectLineStyle(groupedData[gid].map(p => [p.x, p.y]))
    }));

    // Sort based on method
    if (method === 'color') {
        // Sort by color brightness
        series.sort((a, b) => {
            const brightA = (a.color[0] + a.color[1] + a.color[2]) / 3;
            const brightB = (b.color[0] + b.color[1] + b.color[2]) / 3;
            return brightA - brightB;
        });
    } else if (method === 'style') {
        // Sort by line style: solid, dotted, dashed
        const styleOrder = { 'solid': 0, 'dotted': 1, 'dashed': 2 };
        series.sort((a, b) => styleOrder[a.lineStyle] - styleOrder[b.lineStyle]);
    } else if (method === 'both') {
        // First by style, then by color
        const styleOrder = { 'solid': 0, 'dotted': 1, 'dashed': 2 };
        series.sort((a, b) => {
            const styleDiff = styleOrder[a.lineStyle] - styleOrder[b.lineStyle];
            if (styleDiff !== 0) return styleDiff;

            const brightA = (a.color[0] + a.color[1] + a.color[2]) / 3;
            const brightB = (b.color[0] + b.color[1] + b.color[2]) / 3;
            return brightA - brightB;
        });
    }

    // Reassign graph IDs based on new order
    state.detectedData = [];
    series.forEach((s, newIdx) => {
        s.points.forEach(point => {
            state.detectedData.push({
                x: point.x,
                y: point.y,
                graph_id: newIdx + 1
            });
        });
    });

    // Update display
    displayDataTable();
    alert(`Series sorted by ${method}!`);
}

function redrawCanvas() {
    if (state.image) {
        state.ctx.clearRect(0, 0, state.canvas.width, state.canvas.height);
        state.ctx.drawImage(state.image, 0, 0);
    }
}

function updateModeDisplay() {
    document.getElementById('current-mode').textContent =
        state.mode.charAt(0).toUpperCase() + state.mode.slice(1);
}

function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.classList.add('active');
    } else {
        overlay.classList.remove('active');
    }
}

// Show color info popup
function showColorInfo(x, y, r, g, b, graphNum) {
    const info = document.createElement('div');
    info.className = 'color-info-popup';
    info.style.position = 'absolute';
    info.style.left = (x + 20) + 'px';
    info.style.top = (y - 40) + 'px';
    info.innerHTML = `
        <div class="color-swatch" style="background: rgb(${r},${g},${b})"></div>
        <div class="color-text">
            Graph ${graphNum}<br>
            RGB(${r}, ${g}, ${b})
        </div>
    `;

    const container = document.querySelector('.canvas-container');
    container.style.position = 'relative';
    container.appendChild(info);

    setTimeout(() => info.remove(), 2500);
}

// Add magnifier overlay for guided mode
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('image-canvas');
    if (!canvas) return; // Guard against missing canvas

    let magnifierCanvas = null;

    canvas.addEventListener('mousemove', (e) => {
        if (state.mode !== 'guided' || !state.ctx) {
            removeMagnifier();
            return;
        }

        const rect = canvas.getBoundingClientRect();
        const x = Math.floor(e.clientX - rect.left);
        const y = Math.floor(e.clientY - rect.top);

        // Check bounds
        if (x < 0 || y < 0 || x >= canvas.width || y >= canvas.height) {
            removeMagnifier();
            return;
        }

        try {
            // Create or update magnifier
            if (!magnifierCanvas) {
                magnifierCanvas = createMagnifier();
            }

            // Extract 20x20 region around cursor
            const regionSize = 20;
            const halfSize = Math.floor(regionSize / 2);

            const x1 = Math.max(0, x - halfSize);
            const y1 = Math.max(0, y - halfSize);
            const x2 = Math.min(canvas.width, x + halfSize);
            const y2 = Math.min(canvas.height, y + halfSize);

            const regionData = state.ctx.getImageData(x1, y1, x2 - x1, y2 - y1);

            // Get pixel color at exact cursor position
            const pixelData = state.ctx.getImageData(x, y, 1, 1).data;
            const [r, g, b] = pixelData;

            // Draw magnified region
            const magCtx = magnifierCanvas.getContext('2d');
            const zoomFactor = 6;

            // Clear previous
            magCtx.clearRect(0, 0, magnifierCanvas.width, magnifierCanvas.height);

            // Draw background
            magCtx.fillStyle = 'rgba(255, 255, 255, 0.95)';
            magCtx.fillRect(0, 0, 150, 180);
            magCtx.strokeStyle = '#000';
            magCtx.lineWidth = 2;
            magCtx.strokeRect(0, 0, 150, 180);

            // Create temp canvas for zooming
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = x2 - x1;
            tempCanvas.height = y2 - y1;
            const tempCtx = tempCanvas.getContext('2d');
            tempCtx.putImageData(regionData, 0, 0);

            // Draw zoomed region
            magCtx.drawImage(tempCanvas, 5, 5, 140, 140);

            // Draw crosshair at center
            magCtx.strokeStyle = '#ff0000';
            magCtx.lineWidth = 2;
            magCtx.beginPath();
            magCtx.moveTo(65, 75);
            magCtx.lineTo(85, 75);
            magCtx.stroke();
            magCtx.beginPath();
            magCtx.moveTo(75, 65);
            magCtx.lineTo(75, 85);
            magCtx.stroke();

            // Draw RGB text
            magCtx.fillStyle = '#000';
            magCtx.font = '12px Arial';
            const rgbText = `RGB(${r}, ${g}, ${b})`;
            magCtx.fillText(rgbText, 10, 165);

            // Position magnifier near cursor
            const offsetX = 20;
            const offsetY = -190;
            let magX = e.clientX + offsetX;
            let magY = e.clientY + offsetY;

            // Keep within window
            if (magX + 150 > window.innerWidth) magX = e.clientX - 170;
            if (magY < 10) magY = e.clientY + 20;

            magnifierCanvas.style.left = magX + 'px';
            magnifierCanvas.style.top = magY + 'px';

            // Also update cursor color indicator
            updateCursorColor(r, g, b);

        } catch (err) {
            // Ignore errors
            console.error(err);
        }
    });

    canvas.addEventListener('mouseleave', () => {
        removeMagnifier();
        // Also remove color indicator
        const indicator = document.getElementById('cursor-color-indicator');
        if (indicator) indicator.remove();
    });

    function createMagnifier() {
        const mag = document.createElement('canvas');
        mag.id = 'magnifier-canvas';
        mag.className = 'magnifier-overlay';
        mag.width = 150;
        mag.height = 180;
        document.body.appendChild(mag);
        return mag;
    }

    function removeMagnifier() {
        if (magnifierCanvas) {
            magnifierCanvas.remove();
            magnifierCanvas = null;
        }
    }
});

function updateCursorColor(r, g, b) {
    let indicator = document.getElementById('cursor-color-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'cursor-color-indicator';
        indicator.className = 'cursor-color-indicator';
        document.body.appendChild(indicator);
    }

    indicator.style.background = `rgb(${r},${g},${b})`;
    indicator.innerHTML = `<span>RGB(${r},${g},${b})</span>`;
}

# Printed Text Scanner (OCR Application)

A Python GUI application that captures video from your webcam and extracts printed text using Tesseract OCR. Simply draw a region of interest (ROI) on the video feed and run OCR to extract text.

## Features

- **Live Camera Feed** – Stream video from your webcam in real-time
- **ROI Selection** – Click and drag to select a region of interest for text extraction
- **OCR Processing** – Uses Tesseract OCR with image preprocessing (grayscale + binarization) for improved accuracy
- **Text Display** – Extracted text is displayed in a dedicated panel

## Requirements

- Python 3.7+
- Tesseract OCR
- Webcam

### Python Dependencies

```
opencv-python
pytesseract
Pillow
numpy
```

## Installation

### 1. Install Tesseract OCR

**macOS (Homebrew):**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt install tesseract-ocr
```

**Windows:**
Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH.

### 2. Install Python Dependencies

```bash
pip install opencv-python pytesseract Pillow numpy
```

### 3. Configure Tesseract Path (if needed)

Open `main.py` and update the tesseract path if it differs from your installation:

```python
# Find your tesseract path with: which tesseract (macOS/Linux) or where tesseract (Windows)
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
```

## Usage

1. **Run the application:**
   ```bash
   python main.py
   ```

2. **Start the camera** by clicking the "Start Camera" button

3. **Select a region** by clicking and dragging on the video feed to draw a red box around the text you want to extract

4. **Run OCR** by clicking the "Run OCR on ROI" button

5. The extracted text will appear in the right panel

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `camera failed to properly initialize` | Change `cv2.VideoCapture(0)` to a different index (0, 1, 2...) in `main.py` |
| `tesseract is not installed` | Verify tesseract path with `which tesseract` and update `main.py` |
| No text detected | Ensure good lighting and the text is in focus. Try adjusting the ROI selection |

## License

MIT


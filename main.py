import tkinter as tk
from tkinter import ttk, filedialog
import cv2
import pytesseract
from PIL import Image, ImageTk
import threading
import numpy as np
# --- CONFIGURATION ---
# IF YOU ARE ON WINDOWS, UNCOMMENT THE LINE BELOW AND CHECK THE PATH:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
class OCRScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Assignment 2: Printed Text Scanner")
        self.root.geometry("1000x700")
        # Variables
        self.cap = None
        self.is_camera_on = False
        self.roi_start = None
        self.roi_end = None
        self.extracted_text = "Select an area and click 'Scan ROI'"
        self.current_image = None # Holds the cv2 image
        # --- UI LAYOUT ---
        # Top Control Panel
        control_frame = ttk.Frame(root, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        self.btn_camera = ttk.Button(control_frame, text="Start Camera", command=self.toggle_camera)
        self.btn_camera.pack(side=tk.LEFT, padx=5)
        self.btn_ocr = ttk.Button(control_frame, text="Run OCR on ROI", command=self.run_ocr)
        self.btn_ocr.pack(side=tk.LEFT, padx=5)
        # Main Content Area (Split: Video Left, Text Right)
        content_frame = ttk.Frame(root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Canvas for Video/Image
        self.canvas = tk.Canvas(content_frame, bg="black", width=640, height=480)
        self.canvas.pack(side=tk.LEFT, padx=10)
        # Mouse Events for ROI Selection
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        # Text Output Area
        text_frame = ttk.Labelframe(content_frame, text="Extracted Text")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_display = tk.Text(text_frame, height=20, width=30, font=("Arial", 12))
        self.text_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # ROI Overlay ID
        self.rect_id = None
    def toggle_camera(self):
        if self.is_camera_on:
            self.is_camera_on = False
            if self.cap:
                self.cap.release()
            self.btn_camera.config(text="Start Camera")
        else:
            self.cap = cv2.VideoCapture(0)
            self.is_camera_on = True
            self.btn_camera.config(text="Stop Camera")
            self.update_frame()
    def update_frame(self):
        if self.is_camera_on and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_image = frame
                # Convert color for Tkinter
                cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2_image)
                imgtk = ImageTk.PhotoImage(image=img)
                # Update canvas
                self.canvas.create_image(0, 0, image=imgtk, anchor=tk.NW)
                self.canvas.image = imgtk # Keep reference
                # Redraw ROI box if it exists
                if self.roi_start and self.roi_end:
                    self.canvas.create_rectangle(
                        self.roi_start[0], self.roi_start[1],
                        self.roi_end[0], self.roi_end[1],
                        outline="red", width=2, tags="roi"
                    )
                    # Label above ROI
                    self.canvas.create_text(
                        self.roi_start[0], self.roi_start[1]-10,
                        text="ROI", fill="red", anchor=tk.SW, tags="roi"
                    )
            # Schedule next frame
            self.root.after(10, self.update_frame)
    # --- ROI MOUSE HANDLERS ---
    def on_mouse_down(self, event):
        self.roi_start = (event.x, event.y)
        self.roi_end = None
        self.canvas.delete("roi") # Clear old box
    def on_mouse_drag(self, event):
        self.roi_end = (event.x, event.y)
        # Visual feedback is handled in update_frame loop for live video
        # But if camera is off, we need to draw here:
        if not self.is_camera_on:
             self.canvas.delete("roi")
             self.canvas.create_rectangle(
                self.roi_start[0], self.roi_start[1],
                self.roi_end[0], self.roi_end[1],
                outline="red", width=2, tags="roi"
            )
    def on_mouse_up(self, event):
        self.roi_end = (event.x, event.y)
    # --- CORE OCR LOGIC ---
    def run_ocr(self):
        if self.current_image is None:
            self.update_text_display("No image loaded or camera off.")
            return
        if not self.roi_start or not self.roi_end:
            self.update_text_display("Please draw a box (ROI) on the video first.")
            return
        # Calculate crop coordinates ensuring x1 < x2 and y1 < y2
        x1, y1 = self.roi_start
        x2, y2 = self.roi_end
        x_start, x_end = sorted([x1, x2])
        y_start, y_end = sorted([y1, y2])
        # Crop the image (Numpy slicing)
        roi_crop = self.current_image[y_start:y_end, x_start:x_end]
        if roi_crop.size == 0:
            return
        # --- PREPROCESSING (AI Without ML part) ---
        # 1. Convert to Grayscale
        gray = cv2.cvtColor(roi_crop, cv2.COLOR_BGR2GRAY)
        # 2. Thresholding (Binarization) to separate text from background
        # Simple binary threshold or Adaptive threshold works well for printed text
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # Display the processed crop (Optional debug window)
        cv2.imshow("Processed ROI (Pre-OCR)", gray)
        # --- TESSERACT OCR ---
        try:
            # psm 6 assumes a single block of text
            text = pytesseract.image_to_string(gray, config='--psm 6')
            if not text.strip():
                text = "[No text detected or text too blurry]"
            self.update_text_display(text)
        except Exception as e:
            self.update_text_display(f"Error: {str(e)}")
    def update_text_display(self, text):
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert(tk.END, text)
# --- MAIN EXECUTION ---
if __name__ == "__main__":
    root = tk.Tk()
    app = OCRScannerApp(root)
    # Handle clean exit
    def on_closing():
        if app.cap:
            app.cap.release()
        root.destroy()
        cv2.destroyAllWindows()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

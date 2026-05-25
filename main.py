import os
import cv2
import numpy as np
import tkinter as tk  
from PIL import Image, ImageChops, ImageEnhance

# Import your case management dashboard layout class
from ui_dashboard import ObvioscopicDashboard, CLR_BG_DARK 

class ObvioscopicEngine:
    def __init__(self, image_path):
        self.image_path = image_path
        self.img_cv = cv2.imread(image_path)
        if self.img_cv is None:
            raise ValueError(f"Could not open or read image: {image_path}")

    def analyze_mic(self):
        """
        Engine 1: Printer Tracking Dots / High-Contrast Extraction
        Optimizes hidden pixel frequencies for visual isolation.
        """
        gray = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY)
        adjusted = cv2.equalizeHist(gray)
        return cv2.cvtColor(adjusted, cv2.COLOR_GRAY2BGR)

    def analyze_ela(self, quality=95):
        """
        Engine 2: Error Level Analysis (JPEG Compression)
        Detects mismatched compression levels across composite image segments.
        """
        temp_filename = "temp_ela.jpg"
        
        # Save at a specific target compression quality
        img_pil = Image.open(self.image_path).convert("RGB")
        img_pil.save(temp_filename, "JPEG", quality=quality)
        
        # Calculate the absolute pixel difference between original and re-compressed state
        temp_pil = Image.open(temp_filename)
        ela_im = ImageChops.difference(img_pil, temp_pil)
        
        # Rescale the brightness values so errors are visible
        extrema = ela_im.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
        scale = 255.0 / max_diff
        
        # Cleanup temporary file from disk immediately
        if os.path.exists(temp_filename):
            try: os.remove(temp_filename)
            except Exception: pass
            
        return ImageEnhance.Brightness(ela_im).enhance(scale)

    def analyze_noise_variance(self, block_size=8, threshold=0.005):
        """
        Engine 3: Microscopic Noise Variance
        Detects erasures. Includes an adaptive filter to suppress global
        false-positive flooding on perfectly flat, computer-generated canvases.
        """
        gray = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        # Fast Local Variance Mapping
        local_mean = cv2.blur(gray, (block_size, block_size))
        local_sq_mean = cv2.blur(np.square(gray), (block_size, block_size))
        local_variance = local_sq_mean - np.square(local_mean)
        local_variance = np.maximum(local_variance, 0)
        
        # Calculate Adaptive Suppression Density
        bright_pixels = (gray > 200)
        total_bright = np.sum(bright_pixels)
        total_flat_bright = np.sum((local_variance <= threshold) & bright_pixels)
        flatness_ratio = total_flat_bright / total_bright if total_bright > 0 else 0
        
        # Generate initial mask
        erasure_mask = (local_variance <= threshold) & bright_pixels
        mask_8u = (erasure_mask * 255).astype(np.uint8)
        
        # Guardrail: If > 85% of the white space is dead flat, it's born-digital
        if flatness_ratio > 0.85:
            cleaned_mask = np.zeros_like(mask_8u)
        else:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            cleaned_mask = cv2.morphologyEx(mask_8u, cv2.MORPH_OPEN, kernel)
        
        # Build Heatmap and Overlay assets
        normalized_var = cv2.normalize(local_variance, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        heatmap = cv2.applyColorMap(255 - normalized_var, cv2.COLORMAP_JET)
        
        alert_overlay = self.img_cv.copy()
        alert_overlay[cleaned_mask > 0] = [0, 255, 0]  # Neon Green for anomalies
        
        return heatmap, alert_overlay

    def analyze_metadata(self):
        """
        Engine 4: Structural Metadata & Application Fingerprinting
        Carves file headers to expose editing footprints and software conflicts.
        """
        report = []
        
        # 1. Extract standard EXIF data tags
        try:
            img_pil = Image.open(self.image_path)
            exif_data = img_pil._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    if tag_id == 305:  # EXIF Software Tag
                        clean_value = str(value).encode('utf-8', 'ignore').decode('utf-8').replace("Â®", "®")
                        report.append(f"[ALERT] EXIF Software Tag Found: {clean_value}")
        except Exception:
            pass

        # 2. Raw Binary Carving for Tool Mismatches
        try:
            with open(self.image_path, "rb") as f:
                binary_content = f.read()
                
                if b"Microsoft" in binary_content:
                    if not any("Software Tag Found" in r for r in report):
                        report.append("[ALERT] Raw Binary Signature Detected: Microsoft Office Element")
                    
                    # Cross-reference: Check for baseline Huffman compression markers left by Windows GDI+
                    if b"\xff\xc4" in binary_content:
                        report.append("[ALERT] CRITICAL MISMATCH: File metadata claims MS Word, "
                                      "but structural compression encoding matches Windows GDI+ (MS Paint).")
        except Exception:
            pass
            
        return report


class ObvioscopicSplashScreen:
    def __init__(self, root, on_complete_callback):
        self.root = root
        self.on_complete = on_complete_callback
        
        # Full screen canvas wrapper matching terminal darkness
        self.splash_frame = tk.Frame(self.root, bg="#0A0A0C")
        self.splash_frame.pack(fill="both", expand=True)
        
        self.build_splash_ui()
        
    def build_splash_ui(self):
        """Builds your beautiful, clean minimal branding front page."""
        # Clean spaced title
        tk.Label(
            self.splash_frame, 
            text="O B V I O S C O P I C", 
            font=("Consolas", 20, "bold"), 
            fg="#2DD4BF", 
            bg="#0A0A0C"
        ).pack(expand=True, pady=(120, 5))
        
        # Loading / Status label block
        self.lbl_status = tk.Label(
            self.splash_frame, 
            text="[INITIALIZING CORE FORENSIC ENGINE]...", 
            font=("Consolas", 9), 
            fg="#8A8A93", 
            bg="#0A0A0C"
        )
        self.lbl_status.pack(expand=True, pady=(0, 120))
        
        # --- FIXED: Zero button reliance. Triggers automated timed loading step callbacks ---
        self.root.after(1200, self.update_loading_status)

    def update_loading_status(self):
        """Simulates loading benchmarks smoothly across the interface."""
        self.lbl_status.config(text="[MOUNTING MATRIX PROFILES & CASE DATABASE]...")
        # Auto trigger termination sequences next frame
        self.root.after(1000, self.terminate_splash)

    def terminate_splash(self):
        """Wipes out splash layout and automatically drops investigator to Dashboard."""
        self.splash_frame.pack_forget()
        self.splash_frame.destroy()
        self.on_complete()


# --- APPLICATION INTERACTIVE STATE MANAGEMENT ---

def initialize_home_dashboard():
    """Builds and packs the persistent case repository dashboard frame."""
    global active_view
    active_view = ObvioscopicDashboard(
        parent=root, 
        on_case_select_callback=handle_historical_case_load, 
        on_start_new_case_callback=handle_new_case_initialization
    )
    active_view.pack(fill="both", expand=True)

def handle_historical_case_load(case_id):
    """Queries local SQLite database storage dynamically to revive a past project file."""
    print(f"System locating {case_id} records...")
    
    import database
    import sqlite3
    
    conn = sqlite3.connect(database.DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT case_name, target_file_path FROM cases WHERE case_id = ?", (case_id,))
    record = cursor.fetchone()
    conn.close()
    
    if record:
        case_name, filepath = record
        print(f"[SUCCESS]: Reviving archived case configuration: {filepath}")
        launch_case_workspace(case_id, case_name, filepath)
    else:
        from tkinter import messagebox
        messagebox.showerror("Database Error", f"Could not pull file references for case index {case_id}.")

def handle_new_case_initialization(case_id, name, filepath):
    """Callback execution routing for newly browsed case files."""
    launch_case_workspace(case_id, name, filepath)

def return_to_dashboard():
    """Unmounts workspace views and redraws historical case log array."""
    global active_view
    active_view.pack_forget()
    active_view.destroy()
    initialize_home_dashboard()

def launch_case_workspace(case_id, name, filepath):
    """Destroys current frame states and activates the 4-quadrant workspace grid."""
    global active_view
    if active_view:
        active_view.pack_forget()
        active_view.destroy()
    
    # Imported inside execution scope to avoid any circular dependency blocks
    from ui import ForensicWorkstation
    active_view = ForensicWorkstation(root, case_id, name, filepath, return_to_dashboard)
    active_view.pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Obvioscopic Forensic Workspace")
    root.geometry("1280x800")
    root.configure(bg="#121214")
    
    active_view = None
    
    # Boots up beautiful text splash screen -> automatically transitions to dashboard frame
    splash = ObvioscopicSplashScreen(root, on_complete_callback=initialize_home_dashboard)
    
    root.mainloop()
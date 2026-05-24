import cv2
import numpy as np
from PIL import Image, ImageChops

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
        from PIL import ImageEnhance  # Imported to scale up brightness values cleanly
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
        
        # FIX: Using ImageEnhance handles float scaling perfectly 
        # and cleanly accentuates the compression artifacts without crashing.
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

        # 2. Raw Binary Carving for Tool Mismatches (e.g., Paint hiding behind Word)
        try:
            with open(self.image_path, "rb") as f:
                binary_content = f.read()
                
                if b"Microsoft" in binary_content:
                    # Avoid duplication if already caught by EXIF parser
                    if not any("Software Tag Found" in r for r in report):
                        report.append("[ALERT] Raw Binary Signature Detected: Microsoft Office Element")
                    
                    # Cross-reference: Check for baseline Huffman compression markers left by MS Paint (GDI+)
                    if b"\xff\xc4" in binary_content:
                        report.append("[ALERT] CRITICAL MISMATCH: File metadata claims MS Word, "
                                      "but structural compression encoding matches Windows GDI+ (MS Paint).")
        except Exception:
            pass
            
        return report

if __name__ == "__main__":
    # Standard terminal fallback testing execution block
    import os
    test_target = "E:/Obvioscopic/Sample files/_sample.jpg"
    
    if os.path.exists(test_target):
        print("=" * 50)
        print("         OBVIOSCOPIC ENGINE CLI SYSTEM          ")
        print("=" * 50)
        scanner = ObvioscopicEngine(test_target)
        
        # Quick check on Metadata layer via CLI
        meta_reports = scanner.analyze_metadata()
        for alert in meta_reports:
            print(alert)
    else:
        print(f"[!] CLI Fallback target not found at default path: {test_target}")
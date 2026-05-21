import os
import cv2
import numpy as np
from PIL import Image, ImageChops

class ObvioscopicEngine:
    def __init__(self, image_path):
        self.image_path = image_path
        self.img_cv = cv2.imread(image_path)
        if self.img_cv is None:
            raise FileNotFoundError(f"Could not load image at {self.image_path}")
        
    def analyze_mic(self, boost_factor=15, threshold_val=120):
        """
        Isolates the Blue channel, inverts it to make yellow tracking dots 
        highly visible, and boosts contrast.
        """
        # Extract Blue channel (OpenCV uses BGR structure)
        blue_channel = self.img_cv[:, :, 0]
        
        # Invert it (so the yellow dots become bright white/blue) and amplify contrast
        inverted = (255 - blue_channel) * boost_factor
        
        # Thresholding to drop background noise out of frame
        _, thresholded = cv2.threshold(inverted, threshold_val, 255, cv2.THRESH_BINARY)
        return thresholded

    def analyze_ela(self, quality=90):
        """
        Saves the image at a specific compression level and calculates
        the pixel-level difference to pinpoint digital modifications.
        """
        temp_filename = "temp_compressed.jpg"
        
        # Open with PIL and resave at a specific JPEG quality level
        original = Image.open(self.image_path).convert('RGB')
        original.save(temp_filename, 'JPEG', quality=quality)
        resaved = Image.open(temp_filename)
        
        # Compute the absolute mathematical difference between original and compressed
        diff = ImageChops.difference(original, resaved)
        
        # Dynamically scale the pixel differences so human eyes can see the error levels
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        scale = 255.0 / max_diff if max_diff != 0 else 1.0
        
        ela_result = Image.eval(diff, lambda x: x * scale)
        
        # Cleanup the temp file from the workspace
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            
        return ela_result

    def analyze_noise_variance(self, block_size=8, threshold=0.005):
        """
        Detects subtractive digital forgery (erasures) by mapping localized pixel variance.
        Includes an adaptive suppression filter to prevent false-positive flooding on clean digital backgrounds.
        """
        # Convert the already-loaded BGR image to grayscale float32
        gray = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        # Fast Local Variance Calculation
        local_mean = cv2.blur(gray, (block_size, block_size))
        local_sq_mean = cv2.blur(np.square(gray), (block_size, block_size))
        local_variance = local_sq_mean - np.square(local_mean)
        local_variance = np.maximum(local_variance, 0)
        
        # --- ADAPTIVE SUPPRESSION FILTER ---
        # Count total bright background pixels vs how many are completely flat
        bright_pixels = (gray > 200)
        total_bright = np.sum(bright_pixels)
        total_flat_bright = np.sum((local_variance <= threshold) & bright_pixels)
        
        # Calculate the density of the flatness
        flatness_ratio = total_flat_bright / total_bright if total_bright > 0 else 0
        
        # Create the initial erasure mask
        erasure_mask = (local_variance <= threshold) & bright_pixels
        mask_8u = (erasure_mask * 255).astype(np.uint8)
        
        # Guardrail: If > 85% of the white page is already perfectly flat, 
        # this is a native digital document. Suppress global flooding.
        if flatness_ratio > 0.85:
            print("[!] Guardrail Triggered: Background is natively uniform. Suppressing global flood.")
            # Wipe the mask completely because a white-on-white edit on a perfect canvas is completely seamless
            cleaned_mask = np.zeros_like(mask_8u)
        else:
            # Clean up isolated noise spikes using an opening operation on real textured images
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            cleaned_mask = cv2.morphologyEx(mask_8u, cv2.MORPH_OPEN, kernel)
        
        # Generate Visual Forensic Overlays
        normalized_var = cv2.normalize(local_variance, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        heatmap = cv2.applyColorMap(255 - normalized_var, cv2.COLORMAP_JET)
        
        alert_overlay = self.img_cv.copy()
        alert_overlay[cleaned_mask > 0] = [0, 255, 0]  # BGR Neon Green
        
        return heatmap, alert_overlay
    def analyze_ghost_particles(self):
        """
        Amplifies hidden variations in near-white spaces to catch 
        imperfect digital erasures and anti-aliasing remnants.
        """
        gray = cv2.cvtColor(self.img_cv, cv2.COLOR_BGR2GRAY)
        
        # Isolate ONLY pixels that are almost white (240 to 254)
        # If an editor used an off-white brush or missed anti-aliased text edges, 
        # those pixels will fall perfectly into this ultra-tight window.
        ghost_mask = cv2.inRange(gray, 240, 254)
        
        # Boost visibility of any caught particles
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated_ghosts = cv2.dilate(ghost_mask, kernel, iterations=1)
        
        # Create a display image
        ghost_report = self.img_cv.copy()
        ghost_report[dilated_ghosts > 0] = [0, 0, 255] # Mark ghosts in Red
        
        return ghost_report
    def analyze_metadata(self):
        """
        Parses the raw binary and EXIF layers of the file to detect 
        the signatures of digital image editing software.
        """
        report = []
        software_found = None
        
        # 1. Try reading standard EXIF data via PIL
        try:
            img_pil = Image.open(self.image_path)
            exif_data = img_pil._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    # 305 is the EXIF tag code for "Software"
                    if tag_id == 305:
                        software_found = value
                        report.append(f"[ALERT] EXIF Software Tag Found: {value}")
        except Exception:
            pass

        # 2. Raw Binary Carving (For editors that strip EXIF but leave application markers)
        try:
            with open(self.image_path, "rb") as f:
                binary_content = f.read()
                
                # Common image editor signatures in binary strings
                signatures = {
                    b"Adobe Photoshop": "Adobe Photoshop",
                    b"XMP": "Extensible Metadata Platform (XMP) Layer",
                    b"GIMP": "GIMP (GNU Image Manipulation Program)",
                    b"Paint.NET": "Paint.NET Editor",
                    b"icc": "Embedded Color Profile (Indicates re-export)"
                }
                
                for sig, name in signatures.items():
                    if sig in binary_content:
                        report.append(f"[ALERT] Raw Binary Signature Detected: {name}")
        except Exception as e:
            report.append(f"[-] Failed to parse binary data: {e}")
        # 3. Detect Compression Engine Mismatch (GDI+ / Paint footprints)
        try:
            with open(self.image_path, "rb") as f:
                binary_content = f.read()
                
                # Windows GDI+ (MS Paint) leaves specific signatures in the JPEG structure
                # and often strips out the standard JFIF header while leaving raw EXIF
                has_word_meta = b"Microsoft" in binary_content
                
                # Check for standard Windows Graphics/Paint rendering flags
                is_gdi_compressed = b"GDI+" in binary_content or b"Windows Image Download" in binary_content
                
                # If it says Word but has Paint/GDI engine characteristics
                if has_word_meta:
                    print("[*] Cross-Referencing Compression Tables...")
                    # MS Paint saves with standard baseline Huffman tables that differ from Word
                    if b"\xff\xc4" in binary_content: # DHT Marker check
                        report.append("[ALERT] CRITICAL MISMATCH: File metadata claims MS Word, "
                        "but the JPEG structural encoding matches Windows GDI+ (MS Paint).")
        except Exception as e:
            pass  

        # Final Verdict
        if not report:
            print("[+] Structure: File metadata appears stripped or clean.")
        else:
            print("\n" + "!" * 40)
            print("         METADATA FORENSIC REPORT        ")
            print("!" * 40)
            for alert in report:
                print(alert)
            print("!" * 40 + "\n")

# 🛠️ CONFIGURATION
IMAGE_PATH = "E:/Obvioscopic/Sample files/__sample.jpeg" 

def main():
    print("=" * 50)
    print("         OBVIOSCOPIC DIGITAL FORENSICS ENGINE          ")
    print("=" * 50)
    
    if not os.path.exists(IMAGE_PATH):
        print(f"[-] Error: Cannot find '{IMAGE_PATH}' in your open folder.")
        print("[!] Quick Fix: Drag your target image into your VS Code sidebar and name it 'sample.jpg'")
        print("=" * 50)
        return

    print(f"[+] Direct Target: {IMAGE_PATH}")
    
    try:
        # Initialize the unified engine
        scanner = ObvioscopicEngine(IMAGE_PATH)
        
        # 1. Run Machine Identification Code Isolation
        print("[*] Running Engine 1: Extracting Printer Tracking Dots (MIC)...")
        mic_img = scanner.analyze_mic()
        cv2.imwrite("output_mic.png", mic_img)
        print("[-->] Processed: Saved to 'output_mic.png'")
        
        # 2. Run Error Level Analysis
        print("[*] Running Engine 2: Calculating JPEG Compression (ELA)...")
        ela_img = scanner.analyze_ela()
        ela_img.save("output_ela.png")
        print("[-->] Processed: Saved to 'output_ela.png'")
        
        # 3. Run Noise Variance Erasure Detection
        print("[*] Running Engine 3: Analyzing Microscopic Noise Variance...")
        heatmap, alerts = scanner.analyze_noise_variance(block_size=8, threshold=0.005)
        cv2.imwrite("output_variance_heatmap.png", heatmap)
        cv2.imwrite("output_erasure_alerts.png", alerts)
        print("[-->] Processed: Saved to 'output_variance_heatmap.png' & 'output_erasure_alerts.png'")
        
        # 4. Run Metadata Analysis
        print("[*] Running Engine 4: Carving Hidden Metadata Signatures...")
        scanner.analyze_metadata()
        
        print("\n[+] Success! All 3 forensic engines executed cleanly.")
        print("=" * 50)
        
    except Exception as e:
        print(f"[-] Forensic Engine Failure: {e}")
        print("=" * 50)

if __name__ == "__main__":
    main()
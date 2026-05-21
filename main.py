import os
import cv2
import numpy as np
from PIL import Image, ImageChops

class ObvioscopicEngine:
    def __init__(self, image_path):
        self.image_path = image_path
        self.img_cv = cv2.imread(image_path)
        
    def analyze_mic(self, boost_factor=15, threshold_val=120):
        """
        Isolates the Blue channel, inverts it to make yellow tracking dots 
        highly visible, and boosts contrast.
        """
        if self.img_cv is None:
            raise FileNotFoundError(f"Could not load image at {self.image_path}")
            
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

# 🛠️ CONFIGURATION: Change this name if your image has a different filename!
IMAGE_PATH = "sample.jpg" 

def main():
    print("=" * 50)
    print("          OBVIOSCOPIC DIGITAL FORENSICS ENGINE          ")
    print("=" * 50)
    
    # Check if the sample file is actually present in the folder
    if not os.path.exists(IMAGE_PATH):
        print(f"[-] Error: Cannot find '{IMAGE_PATH}' in your open folder.")
        print("[!] Quick Fix: Drag your target image into your VS Code sidebar and name it 'sample.jpg'")
        print("=" * 50)
        return

    print(f"[+] Direct Target: {IMAGE_PATH}")
    
    try:
        scanner = ObvioscopicEngine(IMAGE_PATH)
        
        # 1. Run Machine Identification Code Isolation
        print("[*] Extracting Yellow Printer Tracking Dots (MIC)...")
        mic_img = scanner.analyze_mic()
        cv2.imwrite("output_mic.png", mic_img)
        print("[-->] Processed: Saved output to 'output_mic.png'")
        
        # 2. Run Error Level Analysis
        print("[*] Calculating JPEG Error Level Analysis (ELA)...")
        ela_img = scanner.analyze_ela()
        ela_img.save("output_ela.png")
        print("[-->] Processed: Saved output to 'output_ela.png'")
        
        print("\n[+] Success! Open 'output_mic.png' or 'output_ela.png' in VS Code to see results.")
        print("=" * 50)
        
    except Exception as e:
        print(f"[-] Forensic Engine Failure: {e}")
        print("=" * 50)

if __name__ == "__main__":
    main()
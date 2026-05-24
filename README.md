# Obvioscopic 🔍

Obvioscopic is a digital document forensics and investigation toolkit built to identify document forgery, digital tampering, and printer source attribution. 

Unlike black-box machine learning models, this tool relies on transparent, deterministic image processing algorithms alongside density-mapped threshold filters to provide verifiable, reproducible forensic evidence.

---

## 🚀 Features

### 1. Error Level Analysis (ELA)
* **Purpose:** Detects digital manipulation (copy-paste modifications, digitally added text, spliced signatures).
* **How it works:** JPEG images compress pixels in 8x8 blocks at a uniform rate. When an image is modified and resaved, the edited section introduces a different level of compression error compared to the original background data. ELA resaves the image at a known quality level and calculates the absolute pixel difference to make edited regions glow.

### 2. Machine Identification Code (MIC) Isolation
* **Purpose:** Exposes printer tracking dots and contextual edge matrix anomalies.
* **How it works:** Modern color laser printers embed microscopic yellow dots across documents containing serial numbers and timestamps. This engine isolates the blue channel and boosts local contrast matrices to expose physical tracking data or reveal sharp, non-native edge boundaries where external visual assets were dropped onto the background canvas.

### 3. Noise Variance / Localized Delta Extraction
* **Purpose:** Isolates pixel noise anomalies and automatically flags clusters of high-frequency digital manipulation.
* **How it works:** Analyzes localized noise distribution across the document matrix. When manual brush strokes, digital scribbles, or sharp pixel injections break the document's original ambient noise signature, the system calculates a strict density-mapped bounding box to accurately flag the compromised coordinates without triggering false positives on natural image contours.

---

## 🛠️ Prerequisites & Installation

Make sure you have Python 3.x installed on your environment. You can install the core computational and forensic visualization dependencies directly via pip:

```bash
pip install opencv-python numpy Pillow
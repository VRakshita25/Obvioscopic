# Obvioscopic 🔍

Obvioscopic is a digital document forensics and investigation toolkit built to identify document forgery, digital tampering, and printer source attribution. 

Unlike black-box machine learning models, this tool relies on transparent, deterministic image processing algorithms to provide verifiable forensic evidence.

---

## 🚀 Features

### 1. Error Level Analysis (ELA)
* **Purpose:** Detects digital manipulation (copy-paste modifications, digitally added text, spliced signatures).
* **How it works:** JPEGs compress images in 8x8 pixel blocks at a uniform rate. When an image is modified and resaved, the edited section introduces a different level of compression error. ELA resaves the image at a known quality level (90%) and calculates the absolute pixel difference to make edited regions "glow."

### 2. Machine Identification Code (MIC) Isolation
* **Purpose:** Exposes printer tracking dots and contextual bounding boxes.
* **How it works:** Modern color laser printers embed microscopic yellow dots (serial numbers and timestamps) across documents. This engine isolates the blue channel and aggressively boosts contrast to expose physical tracking data or reveal sharp, non-native color boundaries where digital elements were dropped in.

---

## 🛠️ Prerequisites & Installation

Make sure you have Python 3 installed. Install the necessary forensic dependencies using your terminal:

```bash
pip install opencv-python numpy Pillow
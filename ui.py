import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2

# Import the engine from your main script
from main import ObvioscopicEngine

# Consistent palette styling across your frames
CLR_BG_DARK = "#121214"
CLR_BG_CARD = "#1A1A1E"
CLR_TERMINAL_BG = "#0A0A0C"
CLR_TEXT_MAIN = "#EAEAEA"
CLR_TEXT_MUTED = "#8A8A93"
CLR_ACCENT_BLUE = "#38BDF8"
CLR_ACCENT_TEAL = "#2DD4BF"
CLR_ALERT_RED = "#EF4444"

class ForensicWorkstation(tk.Frame):
    """
    The main 4-quadrant investigative layout. 
    This replaces what used to live globally in your Tk root window initialization.
    """
    def __init__(self, parent, case_id, case_name, file_path, on_back_to_dashboard_callback):
        super().__init__(parent, bg=CLR_BG_DARK)
        
        self.case_id = case_id
        self.case_name = case_name
        self.file_path = file_path
        self.on_back_to_dashboard = on_back_to_dashboard_callback
        
        # Image cache references preventing garbage collection dropouts
        self.image_cache = {}
        
        # Initialize the backend processing engine on this specific case file
        try:
            self.engine = ObvioscopicEngine(self.file_path)
        except Exception as e:
            messagebox.showerror("Engine Mount Failure", f"Failed to open case asset:\n{e}")
            self.on_back_to_dashboard()
            return

        self.build_workstation_ui()
        self.run_forensic_pipeline()

    def build_workstation_ui(self):
        """Builds the control frames, top info-bars, and 4-quadrant grid spaces."""
        # --- Top Status Header Ribbon ---
        header = tk.Frame(self, bg=CLR_BG_CARD, height=60, highlightthickness=1, highlightbackground="#2A2A30")
        header.pack(fill="x", side="top", padx=15, pady=(15, 5))
        header.pack_propagate(False)
        
        btn_back = tk.Button(
            header, text="← CASE INDEX", font=("Consolas", 9, "bold"), 
            bg="#2A2A30", fg=CLR_TEXT_MAIN, relief="flat", padx=10,
            command=self.on_back_to_dashboard
        )
        btn_back.pack(side="left", padx=15, fill="y", pady=10)
        
        case_info = f"ACTIVE INVESTIGATION: {self.case_name} // ID: {self.case_id}"
        tk.Label(header, text=case_info, font=("Consolas", 11, "bold"), fg=CLR_ACCENT_BLUE, bg=CLR_BG_CARD).pack(side="left", padx=10)
        
        # --- Lower Work Area: Split Panel Layout ---
        self.workspace_grid = tk.Frame(self, bg=CLR_BG_DARK)
        self.workspace_grid.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Configure a 2x2 responsive grid for your image quadrant displays
        self.workspace_grid.rowconfigure((0, 1), weight=1, uniform="equal")
        self.workspace_grid.columnconfigure((0, 1), weight=1, uniform="equal")

        # Set up quadrant frame wrappers
        self.quad_q1 = self.create_quadrant("Q1 // ORIGINAL SCAN / SOURCE DOCUMENT")
        self.quad_q1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.quad_q2 = self.create_quadrant("Q2 // ERROR LEVEL ANALYSIS (ELA)")
        self.quad_q2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.quad_q3 = self.create_quadrant("Q3 // NOISE VARIANCE SURFACE MAP")
        self.quad_q3.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.quad_q4 = self.create_quadrant("Q4 // LIVE FORENSIC LOG / HEADER CHECKS")
        self.quad_q4.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

    def create_quadrant(self, label_text):
        """Helper matrix builder ensuring consistent border highlights."""
        frame = tk.Frame(self.workspace_grid, bg=CLR_BG_CARD, highlightthickness=1, highlightbackground="#2A2A30")
        lbl = tk.Label(frame, text=label_text, font=("Consolas", 9, "bold"), fg=CLR_TEXT_MUTED, bg=CLR_BG_CARD, anchor="w")
        lbl.pack(fill="x", side="top", padx=10, pady=8)
        return frame

    def display_image_in_quadrant(self, parent_frame, pil_image):
        """Handles canvas rendering, aspect-ratio thumbnails, and cache bindings."""
        # Clean out any old elements (like text notices) before redrawing
        for widget in parent_frame.winfo_children()[1:]:
            widget.destroy()
            
        canvas = tk.Canvas(parent_frame, bg=CLR_TERMINAL_BG, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Calculate cross-platform bounding sizing constraints
        w, h = pil_image.size
        pil_image.thumbnail((550, 320), Image.Resampling.LANCZOS)
        
        tk_img = ImageTk.PhotoImage(pil_image)
        # Unique cache entry string bounded to memory tracking lifecycle
        self.image_cache[str(parent_frame)] = tk_img
        
        canvas.create_image(10, 10, anchor="nw", image=tk_img)

    def run_forensic_pipeline(self):
        """Invokes the backend computations and pumps raw data into the viewports."""
        # 1. Q1: Render original file view
        orig_pil = Image.open(self.file_path).convert("RGB")
        self.display_image_in_quadrant(self.quad_q1, orig_pil)
        
        # 2. Q2: Run Error Level Analysis calculations
        ela_pil = self.engine.analyze_ela(quality=95)
        self.display_image_in_quadrant(self.quad_q2, ela_pil)
        
        # 3. Q3: Run noise tracking matrices
        heatmap_cv, _ = self.engine.analyze_noise_variance()
        heatmap_rgb = cv2.cvtColor(heatmap_cv, cv2.COLOR_BGR2RGB)
        heatmap_pil = Image.fromarray(heatmap_rgb)
        self.display_image_in_quadrant(self.quad_q3, heatmap_pil)
        
        # 4. Q4: Run metadata parsing arrays and load into standard logs viewport listbox
        log_listbox = tk.Listbox(
            self.quad_q4, bg=CLR_TERMINAL_BG, fg=CLR_TEXT_MAIN, 
            font=("Consolas", 9), relief="flat", highlightthickness=0,
            selectbackground=CLR_ACCENT_BLUE
        )
        log_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        meta_alerts = self.engine.analyze_metadata()
        if meta_alerts:
            for alert in meta_alerts:
                log_listbox.insert(tk.END, alert)
        else:
            log_listbox.insert(tk.END, "[SYSTEM]: Structural verification clean.")
            log_listbox.insert(tk.END, "[SYSTEM]: No suspicious software tags or binary header mismatches found.")
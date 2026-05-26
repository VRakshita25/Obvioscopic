import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import os
import shutil
from pdf2image import convert_from_path

# ====================================================================
# ⚠️ UPDATE THIS PATH STRING TO YOUR EXACT POPPLER BIN LOCATION:
# ====================================================================
POPPLER_BIN_PATH = r"E:\poppler\Library\bin" 

class ForensicWorkstation(tk.Frame):
    def __init__(self, parent, case_id, case_name, file_path, on_back_to_dashboard_callback):
        super().__init__(parent, bg="#121214")
        
        self.case_id = case_id
        self.case_name = case_name
        self.file_path = file_path
        self.on_back_to_dashboard = on_back_to_dashboard_callback
        
        # UI State Variables
        self.sidebar_open = True
        self.image_cache = {}          # Holds active quadrant PhotoImages
        self.thumb_cache = {}          # Prevent garbage collection of thumbnails
        self.active_asset_path = None  # Currently selected image file
        
        # Setup local case asset storage directory
        self.case_dir = os.path.join("cases", f"case_{self.case_id}")
        os.makedirs(self.case_dir, exist_ok=True)
        
        from main import ObvioscopicEngine
        self.engine_class = ObvioscopicEngine  
        
        # Ingest files & build UI
        self.import_initial_asset()
        self.build_workstation_ui()
        
        # Auto-select the first available asset
        self.select_first_available_asset()

    def import_initial_asset(self):
        """Copies the primary file or extracts PDF pages into the local case folder."""
        if not os.path.exists(self.file_path):
            print(f"[ERROR]: Target file does not exist: {self.file_path}")
            return
            
        _, ext = os.path.splitext(self.file_path.lower())
        
        if ext == ".pdf":
            # Check if already extracted to avoid duplicate overhead
            existing_pages = [f for f in os.listdir(self.case_dir) if f.startswith("page_")]
            if not existing_pages:
                print(f"[SYSTEM]: Unrolling PDF layers into case workspace directory...")
                try:
                    # FIXED: Added manual poppler pathway routing here
                    pages = convert_from_path(self.file_path, poppler_path=POPPLER_BIN_PATH)
                    for idx, page in enumerate(pages):
                        page.save(os.path.join(self.case_dir, f"page_{idx+1:03d}.png"), "PNG")
                except Exception as e:
                    print(f"[ERROR]: PDF Extraction failed: {e}")
        else:
            # Copy standard images in safely
            dest = os.path.join(self.case_dir, os.path.basename(self.file_path))
            if not os.path.exists(dest):
                shutil.copy(self.file_path, dest)

    def build_workstation_ui(self):
        """Lays out the persistent header ribbon, collapsible panel drawer, and quadrants."""
        # --- TOP HEADER BANNER ---
        header = tk.Frame(self, bg="#1A1A1E", height=60, highlightthickness=1, highlightbackground="#2A2A30")
        header.pack(fill="x", side="top", padx=15, pady=(15, 5))
        header.pack_propagate(False)
        
        btn_back = tk.Button(
            header, text="← CASE INDEX", font=("Consolas", 9, "bold"), 
            bg="#2A2A30", fg="#EAEAEA", relief="flat", padx=12,
            command=self.on_back_to_dashboard
        )
        btn_back.pack(side="left", padx=15, fill="y", pady=10)
        
        # Toggle Sidebar Pane Drawer Button
        self.btn_toggle_sidebar = tk.Button(
            header, text="📁 PANEL: ON", font=("Consolas", 9, "bold"),
            bg="#26262B", fg="#2DD4BF", relief="flat", padx=12,
            command=self.toggle_sidebar_panel
        )
        self.btn_toggle_sidebar.pack(side="left", fill="y", pady=10)
        
        case_info = f"WORKSTATION: {self.case_name} // TARGET INDEX TRACKER"
        tk.Label(header, text=case_info, font=("Consolas", 11, "bold"), fg="#38BDF8", bg="#1A1A1E").pack(side="left", padx=20)
        
        # --- CORE CONTAINER WINDOW FRAME ---
        self.main_container = tk.Frame(self, bg="#121214")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=5)
        
        # 1. THE ASSET SIDEBAR DRAWER (Left Side)
        self.sidebar_frame = tk.Frame(self.main_container, bg="#1A1A1E", width=220, highlightthickness=1, highlightbackground="#2A2A30")
        self.sidebar_frame.pack(side="left", fill="y", padx=(0, 5), pady=5)
        self.sidebar_frame.pack_propagate(False)
        
        sidebar_title_bar = tk.Frame(self.sidebar_frame, bg="#1A1A1E")
        sidebar_title_bar.pack(fill="x", side="top", padx=10, pady=10)
        
        tk.Label(sidebar_title_bar, text="CASE ASSETS", font=("Consolas", 9, "bold"), fg="#8A8A93", bg="#1A1A1E").pack(side="left")
        
        btn_add_asset = tk.Button(
            sidebar_title_bar, text="➕ ADD FILE", font=("Consolas", 8, "bold"),
            bg="#26262B", fg="#2DD4BF", relief="flat", padx=6, command=self.import_additional_file_dialog
        )
        btn_add_asset.pack(side="right")
        
        # Scrollable area container for target thumbnail stacks
        self.thumb_canvas = tk.Canvas(self.sidebar_frame, bg="#1A1A1E", highlightthickness=0)
        self.thumb_scroll = tk.Scrollbar(self.sidebar_frame, orient="vertical", command=self.thumb_canvas.yview)
        self.thumb_list_frame = tk.Frame(self.thumb_canvas, bg="#1A1A1E")
        
        self.thumb_list_frame.bind(
            "<Configure>", lambda e: self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all"))
        )
        self.thumb_canvas.create_window((0, 0), window=self.thumb_list_frame, anchor="nw", width=200)
        self.thumb_canvas.configure(yscrollcommand=self.thumb_scroll.set)
        
        self.thumb_canvas.pack(side="left", fill="both", expand=True, padx=(5, 0))
        self.thumb_scroll.pack(side="right", fill="y")
        
        # 2. 4-QUADRANT VIEWPORT GRID (Right Side)
        self.workspace_grid = tk.Frame(self.main_container, bg="#121214")
        # FIXED: Removed bad spelling options - changed 'pading' to 'padx' and 'pady'
        self.workspace_grid.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        self.workspace_grid.rowconfigure((0, 1), weight=1, uniform="equal")
        self.workspace_grid.columnconfigure((0, 1), weight=1, uniform="equal")
        
        self.quad_q1 = self.create_quadrant("Q1 // TARGET IMAGE COMPONENT LAYER")
        self.quad_q1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.quad_q2 = self.create_quadrant("Q2 // ERROR LEVEL ANALYSIS (ELA)")
        self.quad_q2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.quad_q3 = self.create_quadrant("Q3 // NOISE VARIANCE SURFACE MAP")
        self.quad_q3.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.quad_q4 = self.create_quadrant("Q4 // LIVE FORENSIC LOG / ANALYTICAL ASSAYS")
        self.quad_q4.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

    def create_quadrant(self, label_text):
        frame = tk.Frame(self.workspace_grid, bg="#1A1A1E", highlightthickness=1, highlightbackground="#2A2A30")
        lbl = tk.Label(frame, text=label_text, font=("Consolas", 9, "bold"), fg="#8A8A93", bg="#1A1A1E", anchor="w")
        lbl.pack(fill="x", side="top", padx=10, pady=8)
        return frame

    def toggle_sidebar_panel(self):
        """Collapses or expands the left asset sidebar dynamically."""
        if self.sidebar_open:
            self.sidebar_frame.pack_forget()
            self.btn_toggle_sidebar.config(text="📁 PANEL: OFF", fg="#8A8A93")
            self.sidebar_open = False
        else:
            self.sidebar_frame.pack(side="left", fill="y", padx=(0, 5), pady=5)
            self.btn_toggle_sidebar.config(text="📁 PANEL: ON", fg="#2DD4BF")
            self.sidebar_open = True

    def populate_thumbnails(self):
        """Scans the case asset directory folder and updates thumbnail cards."""
        for widget in self.thumb_list_frame.winfo_children():
            widget.destroy()
            
        self.thumb_cache.clear()
        
        if not os.path.exists(self.case_dir):
            return
            
        all_files = sorted([f for f in os.listdir(self.case_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif'))])
        
        for index, file_name in enumerate(all_files):
            full_path = os.path.join(self.case_dir, file_name)
            
            # Active selection card styling highlight check
            is_active = (full_path == self.active_asset_path)
            border_clr = "#38BDF8" if is_active else "#2A2A30"
            bg_clr = "#26262B" if is_active else "#1A1A1E"
            
            thumb_card = tk.Frame(self.thumb_list_frame, bg=bg_clr, highlightthickness=1, highlightbackground=border_clr)
            thumb_card.pack(fill="x", pady=4, padx=5)
            
            try:
                # Generate miniature crop layouts for the sidebar item frame
                img = Image.open(full_path)
                img.thumbnail((45, 45), Image.Resampling.LANCZOS)
                tk_thumb = ImageTk.PhotoImage(img)
                self.thumb_cache[file_name] = tk_thumb
                
                lbl_img = tk.Label(thumb_card, image=tk_thumb, bg=bg_clr)
                lbl_img.pack(side="left", padx=5, pady=5)
                
                # Truncate labels so names fit elegantly
                clean_display_name = file_name if len(file_name) < 14 else f"{file_name[:11]}..."
                lbl_txt = tk.Label(thumb_card, text=clean_display_name, font=("Consolas", 8), fg="#EAEAEA", bg=bg_clr, anchor="w")
                lbl_txt.pack(side="left", fill="x", expand=True, padx=2)
                
                # Bind clicking mappings anywhere on the card row
                for w in (thumb_card, lbl_img, lbl_txt):
                    w.bind("<Button-1>", lambda event, path=full_path: self.switch_active_forensic_target(path))
            except Exception:
                pass

    def select_first_available_asset(self):
        if not os.path.exists(self.case_dir):
            return
        all_files = sorted([f for f in os.listdir(self.case_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif'))])
        if all_files:
            self.switch_active_forensic_target(os.path.join(self.case_dir, all_files[0]))
        else:
            self.populate_thumbnails()

    def import_additional_file_dialog(self):
        """Allows injecting new operational files directly into the loaded case layer canvas window."""
        selected_files = filedialog.askopenfilenames(filetypes=[("Asset Images", "*.jpg *.jpeg *.png *.tif *.pdf")])
        if not selected_files:
            return
            
        for path in selected_files:
            _, ext = os.path.splitext(path.lower())
            if ext == ".pdf":
                try:
                    # FIXED: Added manual poppler pathway routing here too
                    pages = convert_from_path(path, poppler_path=POPPLER_BIN_PATH)
                    base_name = os.path.splitext(os.path.basename(path))[0]
                    for idx, page in enumerate(pages):
                        page.save(os.path.join(self.case_dir, f"{base_name}_sheet_{idx+1:03d}.png"), "PNG")
                except Exception as e:
                    messagebox.showerror("Extraction Issue", f"Failed parsing document contents:\n{e}")
            else:
                dest = os.path.join(self.case_dir, os.path.basename(path))
                shutil.copy(path, dest)
                
        # Re-render side list stack frames
        self.populate_thumbnails()
        messagebox.showinfo("Workspace Synchronized", f"Successfully imported files into case repository storage.")

    def switch_active_forensic_target(self, target_path):
        """Routes focus window variables onto the clicked card row template asset."""
        self.active_asset_path = target_path
        self.populate_thumbnails()  # Highlights the active card border color
        self.execute_forensic_analysis_pipeline()

    def display_image_in_quadrant(self, parent_frame, pil_image):
        for widget in parent_frame.winfo_children()[1:]:
            widget.destroy()
            
        canvas = tk.Canvas(parent_frame, bg="#0A0A0C", highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        working_img = pil_image.copy()
        working_img.thumbnail((530, 310), Image.Resampling.LANCZOS)
        
        tk_img = ImageTk.PhotoImage(working_img)
        self.image_cache[str(parent_frame)] = tk_img
        canvas.create_image(10, 10, anchor="nw", image=tk_img)

    def execute_forensic_analysis_pipeline(self):
        """Fires current calculations using target file references."""
        if not self.active_asset_path or not os.path.exists(self.active_asset_path):
            return
            
        engine = self.engine_class(self.active_asset_path)
        
        # 1. Q1: Source Active Selection view
        source_pil = Image.open(self.active_asset_path).convert("RGB")
        self.display_image_in_quadrant(self.quad_q1, source_pil)
        
        # 2. Q2: Run ELA Compressions
        ela_pil = engine.analyze_ela(quality=94)
        self.display_image_in_quadrant(self.quad_q2, ela_pil)
        
        # 3. Q3: Run Microscopic Noise Surface Heatmaps
        heatmap_cv, _ = engine.analyze_noise_variance()
        heatmap_rgb = cv2.cvtColor(heatmap_cv, cv2.COLOR_BGR2RGB)
        heatmap_pil = Image.fromarray(heatmap_rgb)
        self.display_image_in_quadrant(self.quad_q3, heatmap_pil)
        
        # 4. Q4: Logs console updates
        for widget in self.quad_q4.winfo_children()[1:]:
            widget.destroy()
            
        log_listbox = tk.Listbox(
            self.quad_q4, bg="#0A0A0C", fg="#EAEAEA", 
            font=("Consolas", 9), relief="flat", highlightthickness=0,
            selectbackground="#38BDF8"
        )
        log_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        meta_alerts = engine.analyze_metadata()
        log_listbox.insert(tk.END, f"[TARGET]: Focused onto target stream payload matrix.")
        log_listbox.insert(tk.END, f"[FILE]: {os.path.basename(self.active_asset_path)}")
        
        if meta_alerts:
            for alert in meta_alerts:
                log_listbox.insert(tk.END, alert)
        else:
            log_listbox.insert(tk.END, "[SYSTEM]: Structural matrix signature profile nominal.")
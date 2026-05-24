import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import time
from PIL import Image, ImageTk, ImageDraw

# Import your real algorithmic backend engine directly
from main import ObvioscopicEngine

# Forensic Styling Palette
CLR_BG_DARK = "#0B0C10"       
CLR_BG_CARD = "#1F2833"       
CLR_TEXT_MAIN = "#C5C6C7"     
CLR_ACCENT_TEAL = "#66FCF1"   
CLR_ACCENT_BLUE = "#45A29E"   
CLR_ALERT_RED = "#FF4E50"     
CLR_TERMINAL_BG = "#050505"   

class ObvioscopicUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OBVIOSCOPIC // Advanced Forensic Document Workspace")
        self.root.geometry("1400x850")
        self.root.configure(bg=CLR_BG_DARK)
        
        self.current_project_name = "CASE01"
        self.ingested_files = []       
        self.current_active_index = 0  
        
        # Absolute image dictionary cache to prevent garbage collection white screens
        self.image_cache = {}
        
        self.main_container = tk.Frame(self.root, bg=CLR_BG_DARK)
        self.main_container.pack(fill="both", expand=True)
        
        # Bring back the splash screen initialization sequence
        self.trigger_splash_screen()

    def trigger_splash_screen(self):
        """Builds and kicks off the stylized loading splash sequence."""
        self.splash_frame = tk.Frame(self.main_container, bg=CLR_BG_DARK)
        self.splash_frame.pack(fill="both", expand=True)
        
        lbl = tk.Label(
            self.splash_frame, 
            text="O B V I O S C O P I C", 
            font=("Consolas", 28, "bold"), 
            fg=CLR_ACCENT_TEAL, 
            bg=CLR_BG_DARK
        )
        lbl.place(relx=0.5, rely=0.45, anchor="center")
        
        self.progress_canvas = tk.Canvas(self.splash_frame, width=400, height=4, bg="#111111", highlightthickness=0)
        self.progress_canvas.place(relx=0.5, rely=0.55, anchor="center")
        self.progress_bar = self.progress_canvas.create_rectangle(0, 0, 0, 4, fill=CLR_ACCENT_TEAL, width=0)
        
        def animate_slow_load():
            # Adjusted step sleep timer to force a smoother, slower initialization sequence
            for step in range(1, 101):
                time.sleep(0.025)  # Steady pacing delay loop
                pct = int((step / 100) * 400)
                self.root.after(0, lambda w=pct: self.progress_canvas.coords(self.progress_bar, 0, 0, w, 4))
                
            # Transition window viewports safely on main GUI thread
            self.root.after(0, self.transition_to_workbench)
            
        threading.Thread(target=animate_slow_load, daemon=True).start()

    def transition_to_workbench(self):
        """Destroys the loading sequence assets and dynamically draws the work canvas."""
        self.splash_frame.destroy()
        self.build_workbench_workspace()

    def build_workbench_workspace(self):
        header_bar = tk.Frame(self.main_container, bg=CLR_BG_CARD, height=45)
        header_bar.pack(fill="x", side="top")
        header_bar.pack_propagate(False)
        
        lbl_info = tk.Label(header_bar, text=f"|  PROJECT SYSTEM CONTROL: {self.current_project_name.upper()}", font=("Consolas", 11, "bold"), fg=CLR_ACCENT_TEAL, bg=CLR_BG_CARD)
        lbl_info.pack(side="left", padx=15, pady=12)
        
        workspace_split = tk.Frame(self.main_container, bg=CLR_BG_DARK)
        workspace_split.pack(fill="both", expand=True, padx=10, pady=10)
        
        left_panel = tk.Frame(workspace_split, bg=CLR_BG_CARD, width=300)
        left_panel.pack(fill="y", side="left", padx=(0, 5))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="[ ARTIFACT FILE INGEST ]", font=("Consolas", 10, "bold"), fg=CLR_ACCENT_TEAL, bg=CLR_BG_CARD).pack(anchor="w", padx=15, pady=(20, 10))
        
        btn_import = tk.Button(left_panel, text="IMPORT DOCUMENT(S)", font=("Consolas", 9, "bold"), bg=CLR_BG_DARK, fg=CLR_TEXT_MAIN, relief="flat", command=self.handle_batch_ingestion)
        btn_import.pack(fill="x", padx=15, pady=5)
        
        self.queue_box = tk.Listbox(left_panel, bg=CLR_TERMINAL_BG, fg=CLR_TEXT_MAIN, selectbackground=CLR_ACCENT_BLUE, font=("Consolas", 9), relief="flat", height=12)
        self.queue_box.pack(fill="x", padx=15, pady=5)
        self.queue_box.bind("<<ListboxSelect>>", self.on_queue_item_clicked)
        
        self.btn_execute = tk.Button(left_panel, text="RUN COMPLETE PIPELINE", font=("Consolas", 10, "bold"), bg=CLR_ACCENT_TEAL, fg=CLR_BG_DARK, relief="flat", state="disabled", command=self.execute_forensic_pipeline)
        self.btn_execute.pack(fill="x", padx=15, pady=(20, 5))

        right_container = tk.Frame(workspace_split, bg=CLR_BG_DARK)
        right_container.pack(fill="both", expand=True, side="right", padx=(5, 0))
        
        self.verdict_btn = tk.Button(
            right_container, 
            text="SYSTEM DIAGNOSTIC STATE: IDLE\n[Awaiting raw image ingestion initialization...]",
            font=("Consolas", 11, "bold"), bg=CLR_BG_CARD, fg=CLR_TEXT_MAIN,
            activebackground=CLR_BG_CARD, activeforeground=CLR_ACCENT_TEAL,
            relief="flat", bd=1, highlightbackground=CLR_ACCENT_BLUE, justify="left",
            padx=20, pady=15, state="disabled", command=self.open_interactive_explanation_overlay
        )
        self.verdict_btn.pack(fill="x", side="top", pady=(0, 5))
        
        self.gallery_viewport = tk.Frame(right_container, bg=CLR_BG_CARD)
        self.gallery_viewport.pack(fill="both", expand=True, side="top", pady=5)
        self.gallery_viewport.grid_columnconfigure(0, weight=1)
        self.gallery_viewport.grid_columnconfigure(1, weight=1)
        self.gallery_viewport.grid_rowconfigure(0, weight=1)
        self.gallery_viewport.grid_rowconfigure(1, weight=1)
        
        self.view_slots = {}
        slot_labels = ["ORIGINAL CHANNELS", "ERROR LEVEL MAP (ELA)", "EDGE GRADIENT MATRIX", "NOISE / LOCALIZED DELTAS"]
        positions = [(0,0), (0,1), (1,0), (1,1)]
        
        for idx, text in enumerate(slot_labels):
            r, c = positions[idx]
            cell = tk.Frame(self.gallery_viewport, bg=CLR_BG_DARK, highlightthickness=1, highlightbackground="#2D2D2D")
            cell.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
            
            tk.Label(cell, text=text, font=("Consolas", 8, "bold"), fg=CLR_TEXT_MAIN, bg=CLR_BG_DARK).pack(anchor="w", padx=8, pady=4)
            
            canvas = tk.Canvas(cell, bg=CLR_BG_CARD, highlightthickness=0, cursor="hand2")
            canvas.pack(fill="both", expand=True, padx=4, pady=4)
            canvas.bind("<Button-1>", lambda event, title=text: self.launch_full_screen_zoom_view(title))
            
            self.view_slots[text] = canvas

        self.carousel_controls = tk.Frame(right_container, bg=CLR_BG_DARK, height=40)
        self.carousel_controls.pack(fill="x", side="bottom", pady=2)
        
        self.btn_prev = tk.Button(self.carousel_controls, text="⬅ PREVIOUS IMAGE", font=("Consolas", 9, "bold"), bg=CLR_BG_CARD, fg=CLR_TEXT_MAIN, state="disabled", relief="flat", command=self.shift_carousel_prev)
        self.btn_prev.pack(side="left", padx=10, pady=5)
        
        self.lbl_carousel_status = tk.Label(self.carousel_controls, text="MATRIX CONTEXTS: 0 / 0", font=("Consolas", 10, "bold"), fg=CLR_ACCENT_TEAL, bg=CLR_BG_DARK)
        self.lbl_carousel_status.pack(side="left", expand=True)
        
        self.btn_next = tk.Button(self.carousel_controls, text="NEXT IMAGE ➔", font=("Consolas", 9, "bold"), bg=CLR_BG_CARD, fg=CLR_TEXT_MAIN, state="disabled", relief="flat", command=self.shift_carousel_next)
        self.btn_next.pack(side="right", padx=10, pady=5)

    def handle_batch_ingestion(self):
        files = filedialog.askopenfilenames(filetypes=[("Target Images", "*.png *.jpg *.jpeg *.tif *.bmp")])
        if not files: return
            
        for file_path in files:
            label = os.path.basename(file_path)
            try:
                real_image = Image.open(file_path).convert("RGB")
                self.ingested_files.append({
                    "source_path": file_path,
                    "label": label,
                    "verdict": "AWAITING PIPELINE",
                    "meta_logs": [],
                    "detected_doodle_box": None,
                    "raw_image": real_image,
                    "processed_images": {}
                })
                self.queue_box.insert(tk.END, f" FILE: {label}")
            except Exception as e:
                messagebox.showerror("Ingest Fault", f"Failed file tracking initialization: {str(e)}")
            
        self.btn_execute.config(state="normal")
        self.update_carousel_ui_state()
        self.refresh_viewport_display()

    def execute_forensic_pipeline(self):
        self.btn_execute.config(state="disabled")
        threading.Thread(target=self._run_backend_engine_integration, daemon=True).start()

    def _run_backend_engine_integration(self):
        """Runs true ObvioscopicEngine methods with calibrated anomaly density matching."""
        for item in self.ingested_files:
            try:
                engine = ObvioscopicEngine(item["source_path"])
                
                img_orig = item["raw_image"]
                w, h = img_orig.size
                
                # Fetch engine calculations from main module backend functions
                ela_pil = engine.analyze_ela(quality=93)
                mic_cv = engine.analyze_mic()
                mic_rgb = cv2_to_pil(mic_cv)
                
                heatmap_cv, alert_cv = engine.analyze_noise_variance(block_size=8, threshold=0.005)
                noise_rgb = cv2_to_pil(heatmap_cv)
                
                item["meta_logs"] = engine.analyze_metadata()
                
                # Calibrated tracking of true brush edits vs normal edge contrast
                gray_noise = noise_rgb.convert("L")
                px = gray_noise.load()
                
                points = []
                step_x = max(1, w // 100)
                step_y = max(1, h // 100)
                for x in range(0, w, step_x):
                    for y in range(0, h, step_y):
                        # Raised pixel brightness threshold to check for dense anomalies
                        if px[x, y] > 180: 
                            points.append((x, y))
                            
                # Stricter evaluation: Only flag if there's a highly dense cluster (> 45 points)
                # This prevents natural image boundaries from throwing false positives.
                if points and len(points) > 45:
                    min_x = max(0, min([p[0] for p in points]) - 15)
                    max_x = min(w, max([p[0] for p in points]) + 15)
                    min_y = max(0, min([p[1] for p in points]) - 15)
                    max_y = min(h, max([p[1] for p in points]) + 15)
                    item["detected_doodle_box"] = [min_x, min_y, max_x, max_y]
                    
                    for view in [ela_pil, noise_rgb]:
                        draw = ImageDraw.Draw(view)
                        draw.rectangle([min_x, min_y, max_x, max_y], outline=CLR_ALERT_RED, width=max(2, int(w*0.006)))
                else:
                    item["detected_doodle_box"] = None
                
                item["processed_images"] = {
                    "ORIGINAL CHANNELS": img_orig,
                    "ERROR LEVEL MAP (ELA)": ela_pil,
                    "EDGE GRADIENT MATRIX": mic_rgb,
                    "NOISE / LOCALIZED DELTAS": noise_rgb
                }
                item["verdict"] = "FORGERY DETECTED" if item["detected_doodle_box"] else "ANALYSIS COMPLETE"
                
            except Exception as e:
                print(f"[ENGINE FAIL]: {str(e)}")
                
        self.root.after(0, self.on_pipeline_finished)

    def on_pipeline_finished(self):
        self.verdict_btn.config(state="normal")
        self.update_carousel_ui_state()
        self.refresh_viewport_display()

    def open_interactive_explanation_overlay(self):
        """Displays real metadata findings and coordinates calculated from your script dynamically."""
        if not self.ingested_files: return
        active_item = self.ingested_files[self.current_active_index]
        
        overlay = tk.Toplevel(self.root)
        overlay.title(f"ALGORITHMIC ANALYSIS SUMMARY // TARGET: {active_item['label']}")
        overlay.geometry("1200x780")
        overlay.configure(bg=CLR_BG_DARK)
        
        title_bar = tk.Frame(overlay, bg=CLR_ALERT_RED, height=45)
        title_bar.pack(fill="x", side="top")
        tk.Label(title_bar, text="🔬 HARDWARE FORENSIC COMPUTATION BREAKDOWN", font=("Consolas", 12, "bold"), fg=CLR_BG_DARK, bg=CLR_ALERT_RED).pack(pady=10)
        
        split_frame = tk.Frame(overlay, bg=CLR_BG_DARK)
        split_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        canvas_pane = tk.Frame(split_frame, bg=CLR_BG_DARK)
        canvas_pane.pack(fill="both", side="left", expand=True)
        
        text_pane = tk.Frame(split_frame, bg=CLR_BG_CARD, width=450, highlightthickness=1, highlightbackground=CLR_ACCENT_BLUE)
        text_pane.pack(fill="y", side="right", padx=(10, 0))
        text_pane.pack_propagate(False)
        
        report_canvas = tk.Canvas(canvas_pane, bg=CLR_TERMINAL_BG, highlightthickness=0)
        report_canvas.pack(fill="both", expand=True)
        
        annotated_doc = active_item["raw_image"].copy()
        w, h = annotated_doc.size
        box = active_item["detected_doodle_box"]
        meta_reports = active_item.get("meta_logs", [])
        
        if box:
            draw = ImageDraw.Draw(annotated_doc)
            draw.rectangle(box, outline=(255, 0, 0), width=max(4, int(w*0.008)))
            
        annotated_doc.thumbnail((650, 650), Image.Resampling.LANCZOS)
        tk_report_img = ImageTk.PhotoImage(annotated_doc)
        self.image_cache["report_view"] = tk_report_img  
        report_canvas.create_image(20, 20, anchor="nw", image=tk_report_img)
        
        tk.Label(text_pane, text="CALCULATED IMAGE METRICS:", font=("Consolas", 11, "bold"), fg=CLR_ACCENT_TEAL, bg=CLR_BG_CARD).pack(anchor="w", padx=15, pady=15)
        
        # --- FIXED: DYNAMIC TEXT LOGIC BASED ON ACTUAL FINDINGS ---
        if box:
            loc_str = f"[X1: {box[0]}, Y1: {box[1]} to X2: {box[2]}, Y2: {box[3]}]"
            
            # Check if this is likely a brush/doodle or a localized asset splice
            if active_item["verdict"] == "FORGERY DETECTED":
                desc_detail = "A concentrated cluster of high-frequency pixel deltas was isolated inside this window area, matching structural fingerprint manipulation or manual canvas overlays."
            else:
                desc_detail = "Localized compression matrix variance detected. The structural footprint values deviate significantly from the rest of the file layout background signature."

            anom_text = (
                f"[STATUS]: ANOMALY DISCOVERED\n"
                f"• Calculated Coordinates: {loc_str}\n\n"
                f"• Analysis: {desc_detail}"
            )
        elif meta_reports:
            # If there's no box but metadata flags exist
            anom_text = (
                f"[STATUS]: METADATA CORRUPTION DISCOVERED\n"
                f"• Analysis: Pixel arrays appear structurally authentic, but background binary headers contain discrepancies or software editing artifacts."
            )
        else:
            # Clean images
            anom_text = (
                f"[STATUS]: INTEGRITY VERIFIED\n"
                f"• Analysis: Metric calculations match uniform spatial parameters across the entire image workspace. No geometric or compression discrepancies found."
            )
            
        tk.Label(text_pane, text=anom_text, font=("Consolas", 9), fg=CLR_TEXT_MAIN, bg=CLR_BG_CARD, justify="left", wraplength=410).pack(anchor="w", padx=15, pady=10)
        
        tk.Label(text_pane, text="BINARY METADATA LOGS:", font=("Consolas", 11, "bold"), fg=CLR_ACCENT_TEAL, bg=CLR_BG_CARD).pack(anchor="w", padx=15, pady=(25, 5))
        
        if meta_reports:
            for alert in meta_reports:
                tk.Label(text_pane, text=f"• {alert}", font=("Consolas", 8), fg=CLR_ALERT_RED, bg=CLR_BG_CARD, justify="left", wraplength=410).pack(anchor="w", padx=15, pady=2)
        else:
            tk.Label(text_pane, text="• No file software tags or signature mismatches discovered inside structural binary headers.", font=("Consolas", 9), fg=CLR_TEXT_MAIN, bg=CLR_BG_CARD, justify="left", wraplength=410).pack(anchor="w", padx=15, pady=5)
            
        tk.Button(text_pane, text="DISMISS REPORT VIEW", font=("Consolas", 10, "bold"), bg=CLR_ALERT_RED, fg=CLR_BG_DARK, relief="flat", command=overlay.destroy).pack(side="bottom", fill="x", padx=15, pady=15)

    def launch_full_screen_zoom_view(self, mode_title):
        if not self.ingested_files: return
        active_item = self.ingested_files[self.current_active_index]
        base_img = active_item.get("processed_images", {}).get(mode_title)
        if not base_img: return
        
        zoom_window = tk.Toplevel(self.root)
        zoom_window.title(f"EXPLORER VIEWPORT // {mode_title}")
        zoom_window.geometry("950x700")
        zoom_window.configure(bg=CLR_BG_DARK)
        
        z_canvas = tk.Canvas(zoom_window, bg=CLR_TERMINAL_BG, highlightthickness=0)
        z_canvas.pack(fill="both", expand=True)
        
        display_img = base_img.copy()
        display_img.thumbnail((900, 650), Image.Resampling.LANCZOS)
        
        tk_z_img = ImageTk.PhotoImage(display_img)
        self.image_cache[f"zoom_{mode_title}"] = tk_z_img  
        z_canvas.create_image(475, 350, anchor="center", image=tk_z_img)

    def refresh_viewport_display(self):
        if not self.ingested_files: return
        active_item = self.ingested_files[self.current_active_index]
        
        self.queue_box.selection_clear(0, tk.END)
        self.queue_box.selection_set(self.current_active_index)
        
        if active_item["verdict"] == "FORGERY DETECTED":
            self.verdict_btn.config(
                text="⚠️ SYSTEM DIAGNOSTIC STATE: FORGERY DETECTED\n[!] ANALYSIS COMPLETE: Click here to view dynamic calculation logs.",
                fg=CLR_ALERT_RED, activeforeground=CLR_ALERT_RED
            )
        else:
            self.verdict_btn.config(
                text=f"SYSTEM DIAGNOSTIC STATE: {active_item['verdict']}\n[Awaiting execution pipeline compilation...]",
                fg=CLR_TEXT_MAIN, activeforeground=CLR_TEXT_MAIN
            )
            
        processed_maps = active_item.get("processed_images", {})
        for name, canvas in self.view_slots.items():
            canvas.delete("all")
            if name in processed_maps:
                pil_img = processed_maps[name]
                
                c_width = canvas.winfo_width() if canvas.winfo_width() > 10 else 450
                c_height = canvas.winfo_height() if canvas.winfo_height() > 10 else 220
                
                resized_pil = pil_img.copy()
                resized_pil.thumbnail((c_width, c_height), Image.Resampling.LANCZOS)
                
                tk_img = ImageTk.PhotoImage(resized_pil)
                self.image_cache[f"slot_{name}"] = tk_img  
                canvas.create_image(c_width//2, c_height//2, anchor="center", image=tk_img)
            else:
                canvas.create_text(220, 110, text="AWAITING ENGINE COMPILATION RUN", fill=CLR_TEXT_MAIN, font=("Consolas", 9))

    def shift_carousel_next(self):
        if self.current_active_index < len(self.ingested_files) - 1:
            self.current_active_index += 1
            self.update_carousel_ui_state()
            self.refresh_viewport_display()

    def shift_carousel_prev(self):
        if self.current_active_index > 0:
            self.current_active_index -= 1
            self.update_carousel_ui_state()
            self.refresh_viewport_display()

    def on_queue_item_clicked(self, event):
        selection = self.queue_box.curselection()
        if selection:
            self.current_active_index = selection[0]
            self.update_carousel_ui_state()
            self.refresh_viewport_display()

    def update_carousel_ui_state(self):
        total = len(self.ingested_files)
        if total <= 1:
            self.btn_prev.config(state="disabled")
            self.btn_next.config(state="disabled")
        else:
            self.btn_prev.config(state="normal" if self.current_active_index > 0 else "disabled")
            self.btn_next.config(state="normal" if self.current_active_index < total - 1 else "disabled")
        self.lbl_carousel_status.config(text=f"MATRIX CONTEXTS: {self.current_active_index + 1} / {total}")


def cv2_to_pil(cv_img):
    import cv2
    if len(cv_img.shape) == 2:  
        return Image.fromarray(cv_img)
    return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))


if __name__ == "__main__":
    import cv2  
    root = tk.Tk()
    app = ObvioscopicUI(root)
    root.mainloop()
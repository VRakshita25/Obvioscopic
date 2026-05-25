import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database

# UI Color Palette matching your dark terminal aesthetic
CLR_BG_DARK = "#121214"
CLR_BG_CARD = "#1A1A1E"
CLR_TEXT_MAIN = "#EAEAEA"
CLR_TEXT_MUTED = "#8A8A93"
CLR_ACCENT_BLUE = "#38BDF8"
CLR_ACCENT_TEAL = "#2DD4BF"

class ObvioscopicDashboard(tk.Frame):
    def __init__(self, parent, on_case_select_callback, on_start_new_case_callback):
        super().__init__(parent, bg=CLR_BG_DARK)
        self.on_case_select = on_case_select_callback
        self.on_start_new_case = on_start_new_case_callback
        
        self.build_dashboard_layout()

    def build_dashboard_layout(self):
        """Constructs the forensic landing station frame layout."""
        # --- Top Action Bar ---
        top_bar = tk.Frame(self, bg=CLR_BG_DARK, height=80)
        top_bar.pack(fill="x", side="top", padx=30, pady=20)
        top_bar.pack_propagate(False)
        
        tk.Label(
            top_bar, 
            text="🗂️ FORENSIC CASE REPOSITORY", 
            font=("Consolas", 14, "bold"), 
            fg=CLR_TEXT_MAIN, 
            bg=CLR_BG_DARK
        ).pack(side="left", anchor="w")
        
        btn_new_case = tk.Button(
            top_bar,
            text="+ INITIALIZE NEW INVESTIGATION",
            font=("Consolas", 10, "bold"),
            bg=CLR_ACCENT_TEAL,
            fg=CLR_BG_DARK,
            activebackground=CLR_ACCENT_BLUE,
            relief="flat",
            padx=15,
            command=self.prompt_new_case_window
        )
        btn_new_case.pack(side="right", anchor="e")
        
        # --- Main History Panel ---
        self.history_frame = tk.Frame(self, bg=CLR_BG_DARK)
        self.history_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
        self.render_cases_grid()

    def render_cases_grid(self):
        """Clears and redraws the cards for historical cases from the SQLite DB."""
        for widget in self.history_frame.winfo_children():
            widget.destroy()
            
        past_cases = database.get_all_cases()
        
        if not past_cases:
            # Fallback display if database is pristine/empty
            empty_lbl = tk.Label(
                self.history_frame,
                text="[SYSTEM NOTICE]: No prior forensic cases discovered in local storage layout.\nClick the button above to begin your first digital document extraction.",
                font=("Consolas", 10),
                fg=CLR_TEXT_MUTED,
                bg=CLR_BG_DARK,
                justify="center"
            )
            empty_lbl.pack(expand=True)
            return

        # Grid configuration for cross-platform responsiveness
        self.history_frame.columnconfigure((0, 1, 2), weight=1, uniform="equal")
        
        for idx, (c_id, c_name, path, date_str, verdict) in enumerate(past_cases):
            row = idx // 3
            col = idx % 3
            
            # Card Wrapper Base Frame
            card = tk.Frame(self.history_frame, bg=CLR_BG_CARD, highlightthickness=1, highlightbackground="#2A2A30")
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Card Content Information
            tk.Label(card, text=c_id, font=("Consolas", 8, "bold"), fg=CLR_ACCENT_BLUE, bg=CLR_BG_CARD).pack(anchor="w", padx=15, pady=(15, 2))
            tk.Label(card, text=c_name, font=("Consolas", 11, "bold"), fg=CLR_TEXT_MAIN, bg=CLR_BG_CARD, anchor="w").pack(fill="x", padx=15, pady=2)
            
            truncated_path = f"...{path[-35:]}" if len(path) > 35 else path
            tk.Label(card, text=f"Target: {truncated_path}", font=("Consolas", 8), fg=CLR_TEXT_MUTED, bg=CLR_BG_CARD, anchor="w").pack(fill="x", padx=15, pady=2)
            tk.Label(card, text=f"Created: {date_str}", font=("Consolas", 8), fg=CLR_TEXT_MUTED, bg=CLR_BG_CARD, anchor="w").pack(fill="x", padx=15, pady=(2, 10))
            
            # Action Button inside Card to open the workbench
            btn_open = tk.Button(
                card,
                text="MOUNT CASE WORKSPACE →",
                font=("Consolas", 9, "bold"),
                bg="#26262B",
                fg=CLR_TEXT_MAIN,
                activebackground=CLR_ACCENT_BLUE,
                activeforeground=CLR_BG_DARK,
                relief="flat",
                command=lambda case_id=c_id: self.on_case_select(case_id)
            )
            btn_open.pack(fill="x", side="bottom", padx=15, pady=15)

    def prompt_new_case_window(self):
        """Spawns a clean configuration overlay modal to create a fresh case profile."""
        modal = tk.Toplevel(self)
        modal.title("INITIALIZE CORE INVESTIGATION")
        modal.geometry("500x280")
        modal.configure(bg=CLR_BG_CARD)
        modal.resizable(False, False)
        modal.transient(self)
        modal.grab_set()
        
        tk.Label(modal, text="INVESTIGATION TARGET PARAMETERS", font=("Consolas", 11, "bold"), fg=CLR_ACCENT_TEAL, bg=CLR_BG_CARD).pack(anchor="w", padx=20, pady=20)
        
        tk.Label(modal, text="Assign Case Assignment Name:", font=("Consolas", 9), fg=CLR_TEXT_MAIN, bg=CLR_BG_CARD).pack(anchor="w", padx=20)
        entry_name = tk.Entry(modal, font=("Consolas", 10), bg=CLR_BG_DARK, fg=CLR_TEXT_MAIN, insertbackground=CLR_TEXT_MAIN, relief="flat", highlightthickness=1, highlightbackground="#333")
        entry_name.pack(fill="x", padx=20, pady=(5, 15))
        entry_name.insert(0, "Untitled Verification Run")
        
        path_var = tk.StringVar(value="No file targeted.")
        tk.Label(modal, text="Target Document Image File Source:", font=("Consolas", 9), fg=CLR_TEXT_MAIN, bg=CLR_BG_CARD).pack(anchor="w", padx=20)
        
        path_frame = tk.Frame(modal, bg=CLR_BG_CARD)
        path_frame.pack(fill="x", padx=20, pady=5)
        
        lbl_path = tk.Label(path_frame, textvariable=path_var, font=("Consolas", 8), fg=CLR_TEXT_MUTED, bg=CLR_BG_DARK, anchor="w", height=2, highlightthickness=1, highlightbackground="#333")
        lbl_path.pack(fill="x", side="left", expand=True, padx=(0, 5))
        
        def browse_file():
            selected = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png *.tif")])
            if selected: path_var.set(selected)
            
        tk.Button(path_frame, text="BROWSE", font=("Consolas", 8, "bold"), bg="#333", fg=CLR_TEXT_MAIN, relief="flat", command=browse_file, padx=10).pack(side="right", fill="y")
        
        def save_and_launch():
            name = entry_name.get().strip()
            filepath = path_var.get()
            if not name or filepath == "No file targeted.":
                messagebox.showerror("Configuration Error", "Both Case Assignment Name and a verified Image File Target are required.")
                return
            
            # Save into SQLite database
            new_id = database.create_new_case(name, filepath)
            modal.destroy()
            
            # Force dashboard refresh and invoke callback to load workspace views
            self.render_cases_grid()
            self.on_start_new_case(new_id, name, filepath)

        tk.Button(modal, text="CONFIRM & MOUNT WORKSPACE", font=("Consolas", 10, "bold"), bg=CLR_ACCENT_TEAL, fg=CLR_BG_DARK, relief="flat", command=save_and_launch).pack(fill="x", side="bottom", padx=20, pady=20)
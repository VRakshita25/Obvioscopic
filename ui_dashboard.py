import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import os
import database

# Configuration Constants matching the dark terminal aesthetic
CLR_BG_DARK = "#121214"
CLR_PANEL = "#1A1A1E"
CLR_BORDER = "#2A2A30"
CLR_TEXT_PRIMARY = "#EAEAEA"
CLR_TEXT_MUTED = "#8A8A93"
CLR_ACCENT_TEAL = "#2DD4BF"
CLR_ACCENT_BLUE = "#38BDF8"
CLR_ALERT_RED = "#EF4444"

class ObvioscopicDashboard(tk.Frame):
    def __init__(self, parent, on_case_select_callback, on_start_new_case_callback):
        super().__init__(parent, bg=CLR_BG_DARK)
        
        self.on_case_select = on_case_select_callback
        self.on_start_new_case = on_start_new_case_callback
        
        # Build layout architecture
        self.build_dashboard_ui()
        self.refresh_case_repository_view()

    def build_dashboard_ui(self):
        """Draws the master repository panels, split columns, and action nodes."""
        # --- LEFT SIDEBAR PANEL: Create Case ---
        left_panel = tk.Frame(self, bg=CLR_PANEL, width=380, highlightthickness=1, highlightbackground=CLR_BORDER)
        left_panel.pack(side="left", fill="y", padx=(20, 10), pady=20)
        left_panel.pack_propagate(False)
        
        tk.Label(
            left_panel, text="⚡ INITIALIZE NEW CASE", 
            font=("Consolas", 12, "bold"), fg=CLR_ACCENT_TEAL, bg=CLR_PANEL
        ).pack(anchor="w", padx=20, pady=(25, 5))
        
        tk.Label(
            left_panel, text="Log and stage a new target vector file asset.", 
            font=("Consolas", 9), fg=CLR_TEXT_MUTED, bg=CLR_PANEL
        ).pack(anchor="w", padx=20, pady=(0, 25))
        
        # Form Controls
        tk.Label(left_panel, text="INVESTIGATION/CASE NAME", font=("Consolas", 9, "bold"), fg=CLR_TEXT_PRIMARY, bg=CLR_PANEL).pack(anchor="w", padx=20, pady=(5, 2))
        self.ent_name = tk.Entry(left_panel, font=("Consolas", 10), bg="#0A0A0C", fg=CLR_TEXT_PRIMARY, insertbackground=CLR_TEXT_PRIMARY, relief="flat", highlightthickness=1, highlightbackground=CLR_BORDER)
        self.ent_name.pack(fill="x", padx=20, pady=(0, 15), ipady=6)
        
        tk.Label(left_panel, text="FORENSIC TARGET FILE PATH", font=("Consolas", 9, "bold"), fg=CLR_TEXT_PRIMARY, bg=CLR_PANEL).pack(anchor="w", padx=20, pady=(5, 2))
        
        file_picker_frame = tk.Frame(left_panel, bg=CLR_PANEL)
        file_picker_frame.pack(fill="x", padx=20, pady=(0, 25))
        
        self.path_var = tk.StringVar()
        self.ent_path = tk.Entry(file_picker_frame, textvariable=self.path_var, font=("Consolas", 9), bg="#0A0A0C", fg=CLR_TEXT_MUTED, relief="flat", highlightthickness=1, highlightbackground=CLR_BORDER)
        self.ent_path.pack(side="left", fill="x", expand=True, ipady=6)
        
        btn_browse = tk.Button(
            file_picker_frame, text="BROWSE", font=("Consolas", 9, "bold"),
            bg="#26262B", fg=CLR_TEXT_PRIMARY, activebackground=CLR_ACCENT_BLUE,
            activeforeground="#121214", relief="flat", padx=12, command=self.execute_file_browser
        )
        btn_browse.pack(side="right", padx=(5, 0), fill="y")
        
        btn_submit = tk.Button(
            left_panel, text="MOUNT FORENSIC WORKSPACE", font=("Consolas", 10, "bold"),
            bg=CLR_ACCENT_TEAL, fg="#0A0A0C", activebackground=CLR_ACCENT_BLUE,
            activeforeground="#121214", relief="flat", command=self.submit_new_case
        )
        btn_submit.pack(fill="x", padx=20, ipady=12, side="bottom", pady=25)

        # --- RIGHT PANEL: Historical Log Array ---
        right_panel = tk.Frame(self, bg=CLR_BG_DARK)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=20)
        
        tk.Label(
            right_panel, text="📁 PERSISTENT ARCHIVE REPOSITORY", 
            font=("Consolas", 12, "bold"), fg=CLR_ACCENT_BLUE, bg=CLR_BG_DARK
        ).pack(anchor="w", pady=(5, 2))
        
        tk.Label(
            right_panel, text="Select an indexed file profile to restore workstation viewports.", 
            font=("Consolas", 9), fg=CLR_TEXT_MUTED, bg=CLR_BG_DARK
        ).pack(anchor="w", pady=(0, 15))
        
        # --- FIXED SCROLL ARCHITECTURE LAYERING ---
        scroll_container = tk.Frame(right_panel, bg=CLR_BG_DARK)
        scroll_container.pack(fill="both", expand=True)
        
        self.container_canvas = tk.Canvas(scroll_container, bg=CLR_BG_DARK, highlightthickness=0, borderwidth=0)
        self.scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=self.container_canvas.yview)
        
        self.scrollable_feed_frame = tk.Frame(self.container_canvas, bg=CLR_BG_DARK)
        
        # Track canvas configurations dynamically to scale rows perfectly
        self.scrollable_feed_frame.bind(
            "<Configure>", 
            lambda e: self.container_canvas.configure(scrollregion=self.container_canvas.bbox("all"))
        )
        
        # Anchor creation frame config mapping inside canvas space explicitly
        self.canvas_window = self.container_canvas.create_window((0, 0), window=self.scrollable_feed_frame, anchor="nw")
        
        # Force the scrollable inner feed width to expand to match the container layout width completely
        self.container_canvas.bind(
            "<Configure>",
            lambda e: self.container_canvas.itemconfig(self.canvas_window, width=e.width)
        )
        
        self.container_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.container_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def execute_file_browser(self):
        selected = filedialog.askopenfilename(filetypes=[("Forensic Targets", "*.jpg *.jpeg *.png *.tif *.pdf")])
        if selected:
            self.path_var.set(selected)

    def submit_new_case(self):
        name = self.ent_name.get().strip()
        filepath = self.path_var.get().strip()
        
        if not name or not filepath:
            messagebox.showwarning("Missing Parameter", "Please supply both an investigation label name and file asset path.")
            return
            
        if not os.path.exists(filepath):
            messagebox.showerror("IO File Error", "The targeted forensic file path does not exist on disk.")
            return

        # Write straight into local database context layer
        conn = sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO cases (case_name, target_file_path) VALUES (?, ?)", 
            (name, filepath)
        )
        conn.commit()
        generated_id = cursor.lastrowid
        conn.close()
        
        # Wipe input entry clean
        self.ent_name.delete(0, tk.END)
        self.path_var.set("")
        
        # Redraw local view list metrics, then execute callback launch sequences
        self.refresh_case_repository_view()
        self.on_start_new_case(generated_id, name, filepath)

    def refresh_case_repository_view(self):
        """Wipes out active repository rows and pulls live entries from database logs."""
        for widget in self.scrollable_feed_frame.winfo_children():
            widget.destroy()
            
        conn = sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT case_id, case_name, target_file_path, creation_timestamp FROM cases ORDER BY case_id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            tk.Label(
                self.scrollable_feed_frame, text="[NO RECORDED ENTRIES FOUND IN DATABASE INDEX]", 
                font=("Consolas", 10), fg=CLR_TEXT_MUTED, bg=CLR_BG_DARK
            ).pack(pady=40, anchor="w")
            return
            
        for case_id, name, path, timestamp in rows:
            card = tk.Frame(self.scrollable_feed_frame, bg=CLR_PANEL, highlightthickness=1, highlightbackground=CLR_BORDER)
            card.pack(fill="x", expand=True, pady=6, ipady=4)
            
            # Text information metrics block
            info_sub_block = tk.Frame(card, bg=CLR_PANEL)
            info_sub_block.pack(side="left", fill="both", expand=True, padx=15, pady=8)
            
            tk.Label(info_sub_block, text=f"CASE #{case_id} : {name}", font=("Consolas", 10, "bold"), fg=CLR_TEXT_PRIMARY, bg=CLR_PANEL).pack(anchor="w")
            
            truncated_path = path if len(path) < 65 else f"...{path[-62:]}"
            tk.Label(info_sub_block, text=f"Source: {truncated_path}", font=("Consolas", 9), fg=CLR_TEXT_MUTED, bg=CLR_PANEL).pack(anchor="w", pady=(2, 0))
            tk.Label(info_sub_block, text=f"Logged: {timestamp}", font=("Consolas", 8), fg="#6B7280", bg=CLR_PANEL).pack(anchor="w", pady=(2, 0))
            
            # --- ACTION PANEL: Open vs Delete Node Layout ---
            action_panel = tk.Frame(card, bg=CLR_PANEL)
            action_panel.pack(side="right", fill="y", padx=15)
            
            # ❌ NEW: Delete Case Action Node 
            btn_delete = tk.Button(
                action_panel, text="❌", font=("Consolas", 9),
                bg="#26262B", fg=CLR_ALERT_RED, activebackground=CLR_ALERT_RED,
                activeforeground="#FFFFFF", relief="flat", padx=8,
                command=lambda cid=case_id, lbl=name: self.delete_case_record(cid, lbl)
            )
            btn_delete.pack(side="right", padx=(5, 0), fill="y", pady=10)
            
            # Open Case Node
            btn_open = tk.Button(
                action_panel, text="MOUNT ENGINE 🔍", font=("Consolas", 9, "bold"),
                bg="#2A2A30", fg=CLR_TEXT_PRIMARY, activebackground=CLR_ACCENT_BLUE,
                activeforeground="#121214", relief="flat", padx=12,
                command=lambda cid=case_id: self.on_case_select(cid)
            )
            btn_open.pack(side="right", fill="y", pady=10)

    # --- NEW: Core Case Deletion Logic ---
    def delete_case_record(self, case_id, case_label):
        """Removes the record indexing completely from the SQLite database."""
        confirm = messagebox.askyesno(
            "Confirm Destructive Action", 
            f"Are you sure you want to permanently delete Case #{case_id} ({case_label})?\n\nThis will remove it from the persistent index log history."
        )
        if confirm:
            conn = sqlite3.connect(database.DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
            conn.commit()
            conn.close()
            
            print(f"[CLEANUP]: Purged Case #{case_id} indexing map metrics completely.")
            # Refresh view dynamically right away!
            self.refresh_case_repository_view()
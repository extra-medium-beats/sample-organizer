import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class SampleOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sample Organizer")
        self.source_path = ''
        self.dest_path = ''
        self.cancel_requested = False

        self.build_ui()

    def build_ui(self):
        # Folder selectors
        frm = tk.Frame(self.root)
        frm.pack(pady=10, padx=10, fill='x')

        tk.Button(frm, text="Select Source Folder", command=self.select_source).pack(fill='x')
        self.source_label = tk.Label(frm, text="No folder selected")
        self.source_label.pack(fill='x')

        tk.Button(frm, text="Select Destination Folder", command=self.select_destination).pack(fill='x')
        self.dest_label = tk.Label(frm, text="No folder selected")
        self.dest_label.pack(fill='x')

        # Progress bar
        self.progress = tk.DoubleVar()
        self.progress_bar = tk.ttk.Progressbar(frm, variable=self.progress, maximum=100)
        self.progress_bar.pack(fill='x', pady=10)

        # Buttons
        btn_frame = tk.Frame(frm)
        btn_frame.pack(fill='x', pady=5)
        tk.Button(btn_frame, text="Start Organizing Samples", command=self.start_organizing).pack(side='left', expand=True, fill='x')
        tk.Button(btn_frame, text="Cancel", command=self.request_cancel).pack(side='left', expand=True, fill='x')

        # Log area
        tk.Label(frm, text="Activity Log:").pack(anchor='w')
        self.log_area = scrolledtext.ScrolledText(frm, height=10, state='disabled')
        self.log_area.pack(fill='both', expand=True)

    def select_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_path = path
            self.source_label.config(text=path)

    def select_destination(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_path = path
            self.dest_label.config(text=path)

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert('end', message + '\n')
        self.log_area.see('end')
        self.log_area.configure(state='disabled')

    def start_organizing(self):
        if not self.source_path or not self.dest_path:
            messagebox.showerror("Error", "Please select both source and destination folders.")
            return
        self.cancel_requested = False
        threading.Thread(target=self.copy_sample_files, daemon=True).start()

    def request_cancel(self):
        if messagebox.askyesno("Confirm Cancel", "Are you sure you want to cancel the operation?"):
            self.cancel_requested = True
            self.log("Canceling operation...")

    def copy_sample_files(self):
        self.progress_bar.config(mode='indeterminate')
        self.progress_bar.start()
        self.log("Searching for .wav files...")

        wav_files = []
        for root_dir, _, files in os.walk(self.source_path):
            for file in files:
                if file.lower().endswith('.wav'):
                    wav_files.append(os.path.join(root_dir, file))

        total = len(wav_files)
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate')
        self.log(f"Found {total} sample file(s).")

        for idx, file_path in enumerate(wav_files):
            if self.cancel_requested:
                break
            try:
                relative_path = os.path.relpath(os.path.dirname(file_path), self.source_path)
                dest_folder = os.path.join(self.dest_path, relative_path)
                os.makedirs(dest_folder, exist_ok=True)
                shutil.copy2(file_path, dest_folder)
                self.log(f"Copied: {file_path} → {dest_folder}")
            except Exception as e:
                self.log(f"Error copying {file_path}: {e}")

            progress_percent = int(((idx + 1) / total) * 100)
            self.progress.set(progress_percent)

        if self.cancel_requested:
            self.log("Operation canceled by user.")
        else:
            self.log("All sample files copied successfully.")
        self.progress.set(0)

if __name__ == '__main__':
    import tkinter.ttk as ttk  # needed for Progressbar
    root = tk.Tk()
    app = SampleOrganizerApp(root)
    root.mainloop()
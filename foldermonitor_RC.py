import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileHandler(FileSystemEventHandler):
    def __init__(self):
        super(FileHandler, self).__init__()

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        print(f"New file created: {file_path}")
        self.run_batch()

    def run_batch(self):
        batch_cmd = [app.batch_file_var.get()]  # Use the latest batch file path
        subprocess.run(batch_cmd, shell=True)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Reality Capture Monitoring Folder App")

        self.path_var = tk.StringVar()
        self.path_var.set("Select a directory")

        tk.Label(root, text="Choose a directory:").pack(pady=10)
        tk.Button(root, text="Browse", command=self.browse_path).pack(pady=5)
        tk.Entry(root, textvariable=self.path_var, state="readonly", width=50).pack(pady=5)

        tk.Label(root, text="Choose a batch file:").pack(pady=5)
        tk.Button(root, text="Browse", command=self.browse_batch_file).pack(pady=5)
        
        self.batch_file_var = tk.StringVar()
        tk.Entry(root, textvariable=self.batch_file_var, state="readonly", width=50).pack(pady=5)

        tk.Button(root, text="Start Monitoring",bg="green", command=self.start_monitoring).pack(pady=10)

        self.event_handler = FileHandler()
        self.observer = Observer()

    def browse_path(self):
        directory = filedialog.askdirectory()
        self.path_var.set(directory)

    def browse_batch_file(self):
        batch_file = filedialog.askopenfilename(filetypes=[("Batch Files", "*.bat")])
        self.batch_file_var.set(batch_file)

    def start_monitoring(self):
        directory = self.path_var.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", "Please select a valid directory.")
            return

        batch_file = self.batch_file_var.get()
        if not os.path.isfile(batch_file):
            messagebox.showerror("Error", "Please select a valid batch file.")
            return

        messagebox.showinfo("Info", f"Monitoring directory: {directory}")
        self.event_handler.batch_file = batch_file  # Update the batch file path dynamically
        self.observer.schedule(self.event_handler, directory, recursive=False)
        self.observer.start()

    def stop_monitoring(self):
        self.observer.stop()
        self.observer.join()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_monitoring)
    root.mainloop()

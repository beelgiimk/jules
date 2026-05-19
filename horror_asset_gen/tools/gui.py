import tkinter as tk
from tkinter import ttk, messagebox
import threading
from generate_assets import generate_asset_logic

class HorrorAssetGenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Horror Asset Generator - Game Ready 3D")
        self.root.geometry("600x500")
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Horror Asset Generator", font=("Helvetica", 18, "bold")).pack(pady=10)

        # Asset Type
        ttk.Label(main_frame, text="Asset Type:").pack(anchor=tk.W)
        self.asset_type = ttk.Combobox(main_frame, values=["wall", "pipe", "plank", "barrel", "crate", "beam", "floor"], state="readonly")
        self.asset_type.set("wall")
        self.asset_type.pack(fill=tk.X, pady=5)

        # Texture Type
        ttk.Label(main_frame, text="Base Texture:").pack(anchor=tk.W)
        self.texture_type = ttk.Combobox(main_frame, values=["concrete", "metal", "wood", "brick", "tile"], state="readonly")
        self.texture_type.set("concrete")
        self.texture_type.pack(fill=tk.X, pady=5)

        # Horror Effect
        ttk.Label(main_frame, text="Horror Effect:").pack(anchor=tk.W)
        self.effect_type = ttk.Combobox(main_frame, values=["grime", "rust", "blood", "rot", "slime", "none"], state="readonly")
        self.effect_type.set("grime")
        self.effect_type.pack(fill=tk.X, pady=5)

        # Custom Name
        ttk.Label(main_frame, text="Asset Name (Optional):").pack(anchor=tk.W)
        self.asset_name = ttk.Entry(main_frame)
        self.asset_name.pack(fill=tk.X, pady=5)

        # Generate Button
        self.gen_btn = ttk.Button(main_frame, text="Generate Asset", command=self.start_generation)
        self.gen_btn.pack(pady=20)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var, font=("Helvetica", 10, "italic")).pack(pady=10)

        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)

    def start_generation(self):
        self.gen_btn.config(state=tk.DISABLED)
        self.status_var.set("Generating... Please wait.")
        self.progress.start()
        threading.Thread(target=self.generate).start()

    def generate(self):
        try:
            m, a, n = generate_asset_logic(
                self.asset_type.get(),
                self.texture_type.get(),
                self.effect_type.get(),
                self.asset_name.get()
            )
            self.root.after(0, lambda: self.finish_generation(f"Success! Saved to {m}"))
        except Exception as e:
            self.root.after(0, lambda: self.finish_generation(f"Error: {str(e)}", error=True))

    def finish_generation(self, message, error=False):
        self.progress.stop()
        self.gen_btn.config(state=tk.NORMAL)
        self.status_var.set(message)
        if error:
            messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Done", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = HorrorAssetGenGUI(root)
    root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from generate_assets import generate_asset_logic

class HorrorAssetGenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Horror Asset Generator PRO - High End 3D")
        self.root.geometry("600x550")
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Horror Asset Generator PRO", font=("Helvetica", 18, "bold")).pack(pady=10)
        ttk.Label(main_frame, text="Senior Designer Edition", font=("Helvetica", 10)).pack()

        # Asset Type
        ttk.Label(main_frame, text="Asset Type:").pack(anchor=tk.W, pady=(10, 0))
        self.asset_type = ttk.Combobox(main_frame, values=["wall", "pipe", "plank", "barrel", "crate", "beam", "floor", "locker", "table", "vent"], state="readonly")
        self.asset_type.set("wall")
        self.asset_type.pack(fill=tk.X, pady=5)

        # Texture Type
        ttk.Label(main_frame, text="Base Texture:").pack(anchor=tk.W, pady=(10, 0))
        self.texture_type = ttk.Combobox(main_frame, values=["concrete", "metal", "wood", "brick", "tile"], state="readonly")
        self.texture_type.set("concrete")
        self.texture_type.pack(fill=tk.X, pady=5)

        # Horror Effect
        ttk.Label(main_frame, text="Horror Effect:").pack(anchor=tk.W, pady=(10, 0))
        self.effect_type = ttk.Combobox(main_frame, values=["grime", "rust", "blood", "rot", "slime", "none"], state="readonly")
        self.effect_type.set("grime")
        self.effect_type.pack(fill=tk.X, pady=5)

        # Custom Name
        ttk.Label(main_frame, text="Asset Name:").pack(anchor=tk.W, pady=(10, 0))
        self.asset_name = ttk.Entry(main_frame)
        self.asset_name.pack(fill=tk.X, pady=5)

        # Seed
        ttk.Label(main_frame, text="Seed (Optional):").pack(anchor=tk.W, pady=(10, 0))
        self.asset_seed = ttk.Entry(main_frame)
        self.asset_seed.pack(fill=tk.X, pady=5)

        # PBR Info
        ttk.Label(main_frame, text="Generates: GLB, .tres, Albedo, Normal, Roughness, AO", font=("Helvetica", 9, "italic")).pack(pady=5)

        # Generate Button
        self.gen_btn = ttk.Button(main_frame, text="GENERATE HIGH-END ASSET", command=self.start_generation)
        self.gen_btn.pack(pady=20)

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Helvetica", 10, "italic"))
        self.status_label.pack(pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, mode='determinate', variable=self.progress_var)
        self.progress.pack(fill=tk.X, pady=5)

    def start_generation(self):
        self.gen_btn.config(state=tk.DISABLED)
        self.status_var.set("Initializing...")
        self.progress_var.set(0)
        threading.Thread(target=self.generate).start()

    def update_progress(self, message, value):
        self.root.after(0, lambda: self._update_progress_ui(message, value))

    def _update_progress_ui(self, message, value):
        self.status_var.set(message)
        self.progress_var.set(value)

    def generate(self):
        try:
            seed_val = self.asset_seed.get()
            seed_int = int(seed_val) if seed_val and seed_val.isdigit() else None

            # Fixed unpacking to match generate_asset_logic return (7 values)
            results = generate_asset_logic(
                self.asset_type.get(),
                self.texture_type.get(),
                self.effect_type.get(),
                self.asset_name.get(),
                seed=seed_int,
                progress_callback=self.update_progress
            )
            m, a, n, r, ao, s, mat = results
            self.root.after(0, lambda: self.finish_generation(f"Success! Seed: {s}"))
        except Exception as e:
            self.root.after(0, lambda: self.finish_generation(f"Error: {str(e)}", error=True))

    def finish_generation(self, message, error=False):
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

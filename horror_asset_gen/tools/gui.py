import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
from horror_asset_gen.tools.texture_gen import TextureGenerator, HorrorEffects
from horror_asset_gen.tools.model_gen import ModelGenerator

class HorrorAssetGenGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Horror Asset Generator - Game Ready 3D")
        self.root.geometry("600x500")

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("TButton", font=("Helvetica", 12))

        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Horror Asset Generator", font=("Helvetica", 18, "bold")).pack(pady=10)

        # Asset Type
        ttk.Label(main_frame, text="Asset Type:").pack(anchor=tk.W)
        self.asset_type = ttk.Combobox(main_frame, values=["wall", "pipe", "plank"], state="readonly")
        self.asset_type.set("wall")
        self.asset_type.pack(fill=tk.X, pady=5)

        # Texture Type
        ttk.Label(main_frame, text="Base Texture:").pack(anchor=tk.W)
        self.texture_type = ttk.Combobox(main_frame, values=["concrete", "metal"], state="readonly")
        self.texture_type.set("concrete")
        self.texture_type.pack(fill=tk.X, pady=5)

        # Horror Effect
        ttk.Label(main_frame, text="Horror Effect:").pack(anchor=tk.W)
        self.effect_type = ttk.Combobox(main_frame, values=["grime", "rust", "blood", "none"], state="readonly")
        self.effect_type.set("grime")
        self.effect_type.pack(fill=tk.X, pady=5)

        # Custom Name
        ttk.Label(main_frame, text="Asset Name (Optional):").pack(anchor=tk.W)
        self.asset_name = ttk.Entry(main_frame)
        self.asset_name.pack(fill=tk.X, pady=5)

        # Generate Button
        self.gen_btn = ttk.Button(main_frame, text="Generate Asset", command=self.start_generation)
        self.gen_btn.pack(pady=20)

        # Status
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Helvetica", 10, "italic"))
        self.status_label.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)

    def start_generation(self):
        self.gen_btn.config(state=tk.DISABLED)
        self.status_var.set("Generating... Please wait.")
        self.progress.start()

        # Run in thread to not freeze GUI
        thread = threading.Thread(target=self.generate)
        thread.start()

    def generate(self):
        try:
            asset = self.asset_type.get()
            texture = self.texture_type.get()
            effect = self.effect_type.get()
            name = self.asset_name.get() or f"{asset}_{texture}_{effect}"

            output_dir = "horror_asset_gen/output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Texture
            tg = TextureGenerator()
            if texture == "concrete":
                img = tg.generate_concrete()
            else:
                img = tg.generate_metal()

            if effect == "grime":
                img = HorrorEffects.apply_grime(img)
            elif effect == "rust":
                img = HorrorEffects.apply_rust(img)
            elif effect == "blood":
                img = HorrorEffects.apply_blood(img)

            albedo_path = os.path.join(output_dir, f"{name}_albedo.png")
            img.save(albedo_path)

            noise = tg.generate_noise()
            normal_map = tg.generate_normal_map(noise)
            normal_path = os.path.join(output_dir, f"{name}_normal.png")
            normal_map.save(normal_path)

            # Model
            mg = ModelGenerator()
            if asset == "wall":
                mesh = mg.create_wall()
            elif asset == "pipe":
                mesh = mg.create_pipe()
            else:
                mesh = mg.create_plank()

            mg.apply_simple_uv(mesh)
            mg.export(mesh, f"{name}.obj")

            self.root.after(0, lambda: self.finish_generation(f"Success! Asset saved as {name}"))

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

import os
from PIL import Image
import trimesh

def validate():
    output_dir = "horror_asset_gen/output"
    files = os.listdir(output_dir)

    # Check for expected files from samples
    expected_bases = ["wall_concrete_grime", "pipe_metal_rust"]

    for base in expected_bases:
        albedo = f"{base}_albedo.png"
        normal = f"{base}_normal.png"
        model = f"{base}.obj"

        # Validate Albedo
        albedo_path = os.path.join(output_dir, albedo)
        assert os.path.exists(albedo_path), f"Missing {albedo}"
        with Image.open(albedo_path) as img:
            assert img.size == (1024, 1024), f"{albedo} has wrong size: {img.size}"
            print(f"Validated {albedo}: {img.size}")

        # Validate Normal
        normal_path = os.path.join(output_dir, normal)
        assert os.path.exists(normal_path), f"Missing {normal}"
        with Image.open(normal_path) as img:
            assert img.size == (1024, 1024), f"{normal} has wrong size: {img.size}"
            print(f"Validated {normal}: {img.size}")

        # Validate Model
        model_path = os.path.join(output_dir, model)
        assert os.path.exists(model_path), f"Missing {model}"
        mesh = trimesh.load(model_path)
        assert len(mesh.vertices) > 0, f"{model} has no vertices"
        print(f"Validated {model}: {len(mesh.vertices)} vertices")

    print("\nAll assets validated successfully!")

if __name__ == "__main__":
    validate()

import os
from PIL import Image
import trimesh

def validate():
    output_dir = "horror_asset_gen/output"

    # Check for expected files from samples
    expected_bases = ["wall_concrete_grime", "pipe_metal_rust", "barrel_metal_slime", "crate_wood_rot"]

    # Generate the ones we need for validation
    for base in expected_bases:
        parts = base.split('_')
        asset, texture, effect = parts[0], parts[1], parts[2]
        print(f"Generating {base} for validation...")
        os.system(f"python generate_assets.py --asset {asset} --texture {texture} --effect {effect}")

    for base in expected_bases:
        maps = {
            'albedo': f"{base}_albedo.png",
            'normal': f"{base}_normal.png",
            'roughness': f"{base}_roughness.png",
            'ao': f"{base}_ao.png"
        }
        model = f"{base}.obj"

        for map_type, filename in maps.items():
            path = os.path.join(output_dir, filename)
            assert os.path.exists(path), f"Missing {map_type}: {filename}"
            with Image.open(path) as img:
                assert img.size == (1024, 1024), f"{filename} has wrong size: {img.size}"
                print(f"Validated {filename}: {img.size}")

        # Validate Model
        model_path = os.path.join(output_dir, model)
        assert os.path.exists(model_path), f"Missing {model}"
        mesh = trimesh.load(model_path)
        assert len(mesh.vertices) > 0, f"{model} has no vertices"
        # Check if high-res (more than basic 8 for box)
        if base in ["wall_concrete_grime", "crate_wood_rot"]:
            assert len(mesh.vertices) > 8, f"{model} should be high-res"

        print(f"Validated {model}: {len(mesh.vertices)} vertices")

    print("\nAll High-End PBR assets validated successfully!")

if __name__ == "__main__":
    validate()

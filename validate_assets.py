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

    # Generate a batch for testing
    print("Generating batch for validation...")
    os.system("python generate_assets.py --asset crate --texture wood --effect rot --batch 2 --name batch_test")

    all_to_check = expected_bases + ["batch_test_0", "batch_test_1"]

    for base in all_to_check:
        maps = {
            'albedo': f"{base}_albedo.png",
            'normal': f"{base}_normal.png",
            'roughness': f"{base}_roughness.png",
            'ao': f"{base}_ao.png"
        }
        model = f"{base}.glb"
        material = f"{base}.tres"
        scene = f"{base}.tscn"

        for map_type, filename in maps.items():
            path = os.path.join(output_dir, filename)
            assert os.path.exists(path), f"Missing {map_type}: {filename}"
            with Image.open(path) as img:
                assert img.size == (1024, 1024), f"{filename} has wrong size: {img.size}"
                print(f"Validated {filename}: {img.size}")

        # Validate Model (GLB)
        model_path = os.path.join(output_dir, model)
        assert os.path.exists(model_path), f"Missing {model}"
        mesh = trimesh.load(model_path)
        if isinstance(mesh, trimesh.Scene):
            vertices_count = sum(len(m.vertices) for m in mesh.geometry.values())
        else:
            vertices_count = len(mesh.vertices)
        assert vertices_count > 0, f"{model} has no vertices"
        print(f"Validated {model}: {vertices_count} vertices")

        # Validate Material (Godot .tres)
        mat_path = os.path.join(output_dir, material)
        assert os.path.exists(mat_path), f"Missing {material}"
        print(f"Validated {material}")

        # Validate Scene (Godot .tscn)
        scene_path = os.path.join(output_dir, scene)
        assert os.path.exists(scene_path), f"Missing {scene}"
        with open(scene_path, "r") as f:
            content = f.read()
            assert "StaticBody3D" in content
            assert "CollisionShape3D" in content
        print(f"Validated {scene}")

    print("\nAll Advanced High-End PBR assets and scenes validated successfully!")

if __name__ == "__main__":
    validate()

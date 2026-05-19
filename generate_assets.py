import argparse
import os
from horror_asset_gen.tools.texture_gen import TextureGenerator, HorrorEffects
from horror_asset_gen.tools.model_gen import ModelGenerator

def generate_asset_logic(asset_type, texture_type, effect_type, name=None, seed=None, progress_callback=None):
    name = name or f"{asset_type}_{texture_type}_{effect_type}"
    output_dir = "horror_asset_gen/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if progress_callback: progress_callback("Generating heightmap and albedo...", 10)

    # 1. Generate Texture
    tg = TextureGenerator(seed=seed)
    seed = tg.seed # Capture generated seed

    if texture_type == "concrete":
        img, noise = tg.generate_concrete()
    elif texture_type == "metal":
        img, noise = tg.generate_metal()
    elif texture_type == "wood":
        img, noise = tg.generate_wood()
    elif texture_type == "brick":
        img, noise = tg.generate_brick()
    elif texture_type == "tile":
        img, noise = tg.generate_tile()
    else:
        raise ValueError(f"Unknown texture: {texture_type}")

    if progress_callback: progress_callback("Applying horror effects...", 30)
    # Apply Horror Effects
    if effect_type == "grime":
        img = HorrorEffects.apply_grime(img, noise)
    elif effect_type == "rust":
        img = HorrorEffects.apply_rust(img, noise)
    elif effect_type == "blood":
        img = HorrorEffects.apply_blood(img, noise)
    elif effect_type == "rot":
        img = HorrorEffects.apply_rot(img, noise)
    elif effect_type == "slime":
        img = HorrorEffects.apply_slime(img, noise)

    # Save Albedo
    albedo_filename = f"{name}_albedo.png"
    albedo_path = os.path.join(output_dir, albedo_filename)
    img.save(albedo_path)

    if progress_callback: progress_callback("Generating PBR maps...", 50)
    # 2. Generate PBR Maps
    normal_filename = f"{name}_normal.png"
    normal_path = os.path.join(output_dir, normal_filename)
    tg.generate_normal_map(noise).save(normal_path)

    rough_filename = f"{name}_roughness.png"
    rough_path = os.path.join(output_dir, rough_filename)
    tg.generate_roughness_map(noise).save(rough_path)

    ao_filename = f"{name}_ao.png"
    ao_path = os.path.join(output_dir, ao_filename)
    tg.generate_ao_map(noise).save(ao_path)

    if progress_callback: progress_callback("Creating 3D mesh...", 70)
    # 3. Generate 3D Model
    mg = ModelGenerator()
    if asset_type == "wall":
        mesh = mg.create_wall()
    elif asset_type == "pipe":
        mesh = mg.create_pipe()
    elif asset_type == "plank":
        mesh = mg.create_plank()
    elif asset_type == "barrel":
        mesh = mg.create_barrel()
    elif asset_type == "crate":
        mesh = mg.create_crate()
    elif asset_type == "beam":
        mesh = mg.create_beam()
    elif asset_type == "floor":
        mesh = mg.create_floor()
    elif asset_type == "locker":
        mesh = mg.create_locker()
    elif asset_type == "table":
        mesh = mg.create_table()
    elif asset_type == "vent":
        mesh = mg.create_vent()
    else:
        raise ValueError(f"Unknown asset: {asset_type}")

    if progress_callback: progress_callback("Finalizing mesh and UVs...", 85)
    # Note: Vertex displacement is now integrated inside create_ methods where appropriate
    # but we can apply extra if needed.
    mg.apply_improved_uv(mesh)

    maps = {
        'albedo': albedo_filename,
        'normal': normal_filename,
        'roughness': rough_filename,
        'ao': ao_filename
    }

    if progress_callback: progress_callback("Exporting GLB and Material...", 95)
    model_path = mg.export(mesh, f"{name}.glb", maps=maps)
    material_path = mg.generate_godot_material(name, maps)

    if progress_callback: progress_callback("Done!", 100)
    return model_path, albedo_path, normal_path, rough_path, ao_path, seed, material_path

def main():
    parser = argparse.ArgumentParser(description="Professional Horror Asset Generator for Godot")
    parser.add_argument("--asset", choices=["wall", "pipe", "plank", "barrel", "crate", "beam", "floor", "locker", "table", "vent"], required=True)
    parser.add_argument("--texture", choices=["concrete", "metal", "wood", "brick", "tile"], required=True)
    parser.add_argument("--effect", choices=["grime", "rust", "blood", "rot", "slime", "none"], default="none")
    parser.add_argument("--name", help="Custom name")
    parser.add_argument("--seed", type=int, help="Seed")

    args = parser.parse_args()

    m, a, n, r, ao, s, mat = generate_asset_logic(args.asset, args.texture, args.effect, args.name, seed=args.seed)
    print(f"Success! Seed: {s}\nModel: {m}\nMaterial: {mat}")

if __name__ == "__main__":
    main()

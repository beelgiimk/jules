import argparse
import os
import numpy as np
from PIL import Image
from horror_asset_gen.tools.texture_gen import TextureGenerator, HorrorEffects
from horror_asset_gen.tools.model_gen import ModelGenerator

def generate_asset_logic(asset_type, texture_type, effect_type, name=None, seed=None, progress_callback=None):
    name = name or f"{asset_type}_{texture_type}_{effect_type}"
    output_dir = "horror_asset_gen/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if progress_callback: progress_callback(f"[{name}] Heightmap & Albedo...", 10)

    tg = TextureGenerator(seed=seed)
    seed = tg.seed

    if texture_type == "concrete": img, noise = tg.generate_concrete()
    elif texture_type == "metal": img, noise = tg.generate_metal()
    elif texture_type == "wood": img, noise = tg.generate_wood()
    elif texture_type == "brick": img, noise = tg.generate_brick()
    elif texture_type == "tile": img, noise = tg.generate_tile()
    else: raise ValueError(f"Unknown texture: {texture_type}")

    if progress_callback: progress_callback(f"[{name}] Horror Effects...", 30)
    rough_mod = np.zeros(tg.size)
    if effect_type == "grime": img, rough_mod = HorrorEffects.apply_grime(img, noise)
    elif effect_type == "rust": img, rough_mod = HorrorEffects.apply_rust(img, noise)
    elif effect_type == "blood": img, rough_mod = HorrorEffects.apply_blood(img, noise)
    elif effect_type == "rot": img, rough_mod = HorrorEffects.apply_rot(img, noise)
    elif effect_type == "slime": img, rough_mod = HorrorEffects.apply_slime(img, noise)

    albedo_filename = f"{name}_albedo.png"
    albedo_path = os.path.join(output_dir, albedo_filename)
    img.save(albedo_path)

    if progress_callback: progress_callback(f"[{name}] PBR Maps...", 50)
    normal_filename = f"{name}_normal.png"
    normal_path = os.path.join(output_dir, normal_filename)
    tg.generate_normal_map(noise).save(normal_path)

    rough_filename = f"{name}_roughness.png"
    rough_path = os.path.join(output_dir, rough_filename)
    base_rough = np.array(tg.generate_roughness_map(noise)).astype(float) / 255.0
    final_rough = np.clip(base_rough + rough_mod, 0, 1)
    Image.fromarray((final_rough * 255).astype(np.uint8)).save(rough_path)

    ao_filename = f"{name}_ao.png"
    ao_path = os.path.join(output_dir, ao_filename)
    tg.generate_ao_map(noise).save(ao_path)

    if progress_callback: progress_callback(f"[{name}] 3D Mesh...", 70)
    mg = ModelGenerator()
    if asset_type == "wall": mesh = mg.create_wall()
    elif asset_type == "pipe": mesh = mg.create_pipe()
    elif asset_type == "plank": mesh = mg.create_plank()
    elif asset_type == "barrel": mesh = mg.create_barrel()
    elif asset_type == "crate": mesh = mg.create_crate()
    elif asset_type == "beam": mesh = mg.create_beam()
    elif asset_type == "floor": mesh = mg.create_floor()
    elif asset_type == "locker": mesh = mg.create_locker()
    elif asset_type == "table": mesh = mg.create_table()
    elif asset_type == "vent": mesh = mg.create_vent()
    elif asset_type == "meathook": mesh = mg.create_meathook()
    elif asset_type == "cage": mesh = mg.create_cage()
    else: raise ValueError(f"Unknown asset: {asset_type}")

    if progress_callback: progress_callback(f"[{name}] Finalizing...", 85)
    mg.apply_improved_uv(mesh)

    maps = {'albedo': albedo_filename, 'normal': normal_filename, 'roughness': rough_filename, 'ao': ao_filename}

    model_path = mg.export(mesh, f"{name}.glb", maps=maps)
    material_path = mg.generate_godot_material(name, maps)
    scene_path = mg.generate_godot_scene(name, asset_type, f"{name}.glb", f"{name}.tres")

    if progress_callback: progress_callback(f"[{name}] Done!", 100)
    return model_path, albedo_path, normal_path, rough_path, ao_path, seed, material_path, scene_path

def main():
    parser = argparse.ArgumentParser(description="Professional Horror Asset Generator for Godot")
    parser.add_argument("--asset", choices=["wall", "pipe", "plank", "barrel", "crate", "beam", "floor", "locker", "table", "vent", "meathook", "cage"], required=True)
    parser.add_argument("--texture", choices=["concrete", "metal", "wood", "brick", "tile"], required=True)
    parser.add_argument("--effect", choices=["grime", "rust", "blood", "rot", "slime", "none"], default="none")
    parser.add_argument("--name", help="Custom name")
    parser.add_argument("--seed", type=int, help="Seed")
    parser.add_argument("--batch", type=int, default=1, help="Number of variants to generate")

    args = parser.parse_args()

    for i in range(args.batch):
        suffix = f"_{i}" if args.batch > 1 else ""
        current_name = (args.name or f"{args.asset}_{args.texture}_{args.effect}") + suffix
        # Randomize seed for subsequent batch items if no specific seed is given
        current_seed = args.seed if (i == 0 or args.seed is not None) else None

        print(f"Generating variant {i+1}/{args.batch}...")
        results = generate_asset_logic(args.asset, args.texture, args.effect, current_name, seed=current_seed)
        print(f"  Success! Seed: {results[5]}")

if __name__ == "__main__":
    main()

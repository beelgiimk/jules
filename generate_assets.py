import argparse
import os
from horror_asset_gen.tools.texture_gen import TextureGenerator, HorrorEffects
from horror_asset_gen.tools.model_gen import ModelGenerator

def generate_asset_logic(asset_type, texture_type, effect_type, name=None, progress_callback=None):
    name = name or f"{asset_type}_{texture_type}_{effect_type}"
    output_dir = "horror_asset_gen/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if progress_callback: progress_callback("Generating heightmap and albedo...", 10)

    # 1. Generate Texture
    tg = TextureGenerator()
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

    if progress_callback: progress_callback("Generating Normal, Roughness, and AO maps...", 50)
    # 2. Generate PBR Maps
    normal_map = tg.generate_normal_map(noise)
    normal_filename = f"{name}_normal.png"
    normal_path = os.path.join(output_dir, normal_filename)
    normal_map.save(normal_path)

    roughness_map = tg.generate_roughness_map(noise)
    rough_filename = f"{name}_roughness.png"
    rough_path = os.path.join(output_dir, rough_filename)
    roughness_map.save(rough_path)

    ao_map = tg.generate_ao_map(noise)
    ao_filename = f"{name}_ao.png"
    ao_path = os.path.join(output_dir, ao_filename)
    ao_map.save(ao_path)

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
    else:
        raise ValueError(f"Unknown asset: {asset_type}")

    if progress_callback: progress_callback("Applying vertex displacement and UVs...", 85)
    mg.apply_vertex_displacement(mesh)
    mg.apply_improved_uv(mesh)

    maps = {
        'albedo': albedo_filename,
        'normal': normal_filename,
        'roughness': rough_filename,
        'ao': ao_filename
    }

    if progress_callback: progress_callback("Exporting model...", 95)
    model_path = mg.export(mesh, f"{name}.obj", maps=maps)

    if progress_callback: progress_callback("Done!", 100)
    return model_path, albedo_path, normal_path, rough_path, ao_path

def main():
    parser = argparse.ArgumentParser(description="High-End Horror Asset Generator for Godot")
    parser.add_argument("--asset", choices=["wall", "pipe", "plank", "barrel", "crate", "beam", "floor"], required=True, help="Type of 3D asset to generate")
    parser.add_argument("--texture", choices=["concrete", "metal", "wood", "brick", "tile"], required=True, help="Base texture type")
    parser.add_argument("--effect", choices=["grime", "rust", "blood", "rot", "slime", "none"], default="none", help="Horror effect to apply")
    parser.add_argument("--name", help="Custom name for the generated asset")

    args = parser.parse_args()

    print(f"Generating high-end asset: {args.name or (args.asset + '_' + args.texture)}...")
    m, a, n, r, ao = generate_asset_logic(args.asset, args.texture, args.effect, args.name)
    print(f"Saved PBR set:\nModel: {m}\nAlbedo: {a}\nNormal: {n}\nRoughness: {r}\nAO: {ao}")
    print("Generation complete!")

if __name__ == "__main__":
    main()

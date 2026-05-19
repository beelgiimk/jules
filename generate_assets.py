import argparse
import os
from horror_asset_gen.tools.texture_gen import TextureGenerator, HorrorEffects
from horror_asset_gen.tools.model_gen import ModelGenerator

def generate_asset_logic(asset_type, texture_type, effect_type, name=None):
    name = name or f"{asset_type}_{texture_type}_{effect_type}"
    output_dir = "horror_asset_gen/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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

    # 2. Generate Normal Map (using SAME noise for alignment)
    normal_map = tg.generate_normal_map(noise)
    normal_path = os.path.join(output_dir, f"{name}_normal.png")
    normal_map.save(normal_path)

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

    mg.apply_simple_uv(mesh)
    model_path = mg.export(mesh, f"{name}.obj", albedo_name=albedo_filename)
    return model_path, albedo_path, normal_path

def main():
    parser = argparse.ArgumentParser(description="Horror Asset Generator for Godot")
    parser.add_argument("--asset", choices=["wall", "pipe", "plank", "barrel", "crate", "beam", "floor"], required=True, help="Type of 3D asset to generate")
    parser.add_argument("--texture", choices=["concrete", "metal", "wood", "brick", "tile"], required=True, help="Base texture type")
    parser.add_argument("--effect", choices=["grime", "rust", "blood", "rot", "slime", "none"], default="none", help="Horror effect to apply")
    parser.add_argument("--name", help="Custom name for the generated asset")

    args = parser.parse_args()

    print(f"Generating asset: {args.name or (args.asset + '_' + args.texture)}...")
    m, a, n = generate_asset_logic(args.asset, args.texture, args.effect, args.name)
    print(f"Saved: {m}, {a}, {n}")
    print("Generation complete!")

if __name__ == "__main__":
    main()

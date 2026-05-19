import argparse
import os
from horror_asset_gen.tools.texture_gen import TextureGenerator, HorrorEffects
from horror_asset_gen.tools.model_gen import ModelGenerator

def main():
    parser = argparse.ArgumentParser(description="Horror Asset Generator for Godot")
    parser.add_argument("--asset", choices=["wall", "pipe", "plank"], required=True, help="Type of 3D asset to generate")
    parser.add_argument("--texture", choices=["concrete", "metal"], required=True, help="Base texture type")
    parser.add_argument("--effect", choices=["grime", "rust", "blood", "none"], default="none", help="Horror effect to apply")
    parser.add_argument("--name", help="Custom name for the generated asset")

    args = parser.parse_args()

    name = args.name or f"{args.asset}_{args.texture}_{args.effect}"
    output_dir = "horror_asset_gen/output"

    print(f"Generating asset: {name}...")

    # 1. Generate Texture
    tg = TextureGenerator()
    if args.texture == "concrete":
        img = tg.generate_concrete()
    elif args.texture == "metal":
        img = tg.generate_metal()

    # Apply Horror Effects
    if args.effect == "grime":
        img = HorrorEffects.apply_grime(img)
    elif args.effect == "rust":
        img = HorrorEffects.apply_rust(img)
    elif args.effect == "blood":
        img = HorrorEffects.apply_blood(img)

    # Save Albedo
    albedo_path = os.path.join(output_dir, f"{name}_albedo.png")
    img.save(albedo_path)
    print(f"Saved albedo: {albedo_path}")

    # 2. Generate Normal Map (from noise, for simplicity we recreate some noise here or use a dummy)
    # Ideally TextureGenerator would return both or handle it.
    noise = tg.generate_noise()
    normal_map = tg.generate_normal_map(noise)
    normal_path = os.path.join(output_dir, f"{name}_normal.png")
    normal_map.save(normal_path)
    print(f"Saved normal map: {normal_path}")

    # 3. Generate 3D Model
    mg = ModelGenerator()
    if args.asset == "wall":
        mesh = mg.create_wall()
    elif args.asset == "pipe":
        mesh = mg.create_pipe()
    elif args.asset == "plank":
        mesh = mg.create_plank()

    mg.apply_simple_uv(mesh)
    model_path = mg.export(mesh, f"{name}.obj")
    print(f"Saved model: {model_path}")

    print("Generation complete! Ready to import into Godot.")

if __name__ == "__main__":
    main()

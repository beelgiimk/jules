# Horror Asset Generator

Detta verktyg genererar game-ready assets för Godot horror spel.

## GUI Applikation

För att starta applikationen med ett grafiskt gränssnitt, kör:
```bash
python run_app.py
```

## CLI Användning

Du kan också använda kommandoraden:
```bash
python generate_assets.py --asset [wall|pipe|plank|barrel|crate|beam|floor] --texture [concrete|metal|wood|brick|tile] --effect [grime|rust|blood|rot|slime|none]
```

Exempel:
```bash
python generate_assets.py --asset crate --texture wood --effect rot
```

## Godot Addon (In-Editor)

Du kan nu använda generatorn direkt inuti Godot!
1. Kopiera mappen `addons/horror_asset_gen` till din Godot-projekts `addons/`-mapp.
2. Gå till **Project Settings > Plugins** och aktivera "Horror Asset Generator".
3. En ny flik "Horror Generator" dyker upp i högra panelen.

## Utdata
Alla filer sparas i `horror_asset_gen/output/`.
- `*_albedo.png`: Bas-textur
- `*_normal.png`: Normal map
- `*_roughness.png`: Roughness map
- `*_ao.png`: Ambient Occlusion map
- `*.glb`: 3D modell (GLTF 2.0) med PBR-stöd
- `*.tres`: Godot StandardMaterial3D (färdiglänkat!)

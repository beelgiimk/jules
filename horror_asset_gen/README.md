# Horror Asset Generator

Detta verktyg genererar game-ready assets för Godot horror spel.

## Användning

```bash
python generate_assets.py --asset [wall|pipe|plank] --texture [concrete|metal] --effect [grime|rust|blood|none]
```

Exempel:
```bash
python generate_assets.py --asset wall --texture concrete --effect grime
```

## Utdata
Alla filer sparas i `horror_asset_gen/output/`.
- `*_albedo.png`: Bas-textur
- `*_normal.png`: Normal map
- `*.obj`: 3D modell med UV-mappning

@tool
extends Control

@onready var asset_type = $VBox/AssetType
@onready var texture_type = $VBox/TextureType
@onready var effect_type = $VBox/EffectType
@onready var asset_name = $VBox/AssetName
@onready var seed_edit = $VBox/Seed
@onready var batch_count = $VBox/BatchCount
@onready var gen_button = $VBox/Generate
@onready var status_label = $VBox/Status

func _ready():
	gen_button.pressed.connect(_on_generate_pressed)

func _on_generate_pressed():
	status_label.text = "Generating Batch... (Calling Python)"

	var a = asset_type.get_item_text(asset_type.selected)
	var t = texture_type.get_item_text(texture_type.selected)
	var e = effect_type.get_item_text(effect_type.selected)
	var n = asset_name.text
	var s = seed_edit.text
	var b = int(batch_count.value)

	var args = ["generate_assets.py", "--asset", a, "--texture", t, "--effect", e, "--batch", str(b)]
	if not n.is_empty():
		args.append("--name")
		args.append(n)
	if not s.is_empty():
		args.append("--seed")
		args.append(s)

	# Call Python
	var output = []
	var exit_code = OS.execute("python", args, output, true)

	if exit_code == 0:
		status_label.text = "Success! Batch generated. Remember to refresh file system (Rescan)."
		print(output[0])
	else:
		status_label.text = "Error! Check console output. Exit code: " + str(exit_code)
		printerr(output[0])

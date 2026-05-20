import trimesh
import numpy as np
import os
from PIL import Image

class ModelGenerator:
    def __init__(self, output_dir="horror_asset_gen/output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _create_high_res_box(self, extents):
        mesh = trimesh.creation.box(extents=extents)
        for _ in range(3):
            mesh = mesh.subdivide()
        return mesh

    def create_wall(self, width=2.0, height=2.0, thickness=0.1):
        mesh = self._create_high_res_box([width, height, thickness])
        self.apply_vertex_displacement(mesh, strength=0.015)
        return mesh

    def create_pipe(self, radius=0.05, height=2.0, sections=64):
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
        self.apply_vertex_displacement(mesh, strength=0.005)
        return mesh

    def create_plank(self, width=0.2, length=2.0, thickness=0.02):
        mesh = self._create_high_res_box([width, length, thickness])
        self.apply_vertex_displacement(mesh, strength=0.01)
        return mesh

    def create_barrel(self, radius=0.4, height=1.0, sections=64):
        body = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
        vertices = body.vertices
        center_y = np.mean(vertices[:, 1])
        dist_from_center = np.abs(vertices[:, 1] - center_y)
        bulge = 1.0 + (1.0 - (dist_from_center / (height / 2))) * 0.15
        vertices[:, 0] *= bulge
        vertices[:, 2] *= bulge
        body.vertices = vertices
        self.apply_vertex_displacement(body, strength=0.01)

        parts = [body]
        hoop_count = 2
        for i in range(hoop_count):
            y_off = (height / 4) * (1 if i == 0 else -1)
            b = 1.0 + (1.0 - (abs(y_off) / (height / 2))) * 0.15
            hoop = trimesh.creation.annulus(r_min=radius * b, r_max=radius * b + 0.02, height=0.05, sections=sections)
            hoop.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
            hoop.apply_translation([0, y_off, 0])
            parts.append(hoop)

        return trimesh.util.concatenate(parts)

    def create_crate(self, size=1.0):
        body = self._create_high_res_box([size * 0.95, size * 0.95, size * 0.95])
        self.apply_vertex_displacement(body, strength=0.02) # Wear only on panels

        frame_thickness = size * 0.1
        parts = [body]
        for off in [[1,1], [1,-1], [-1,1], [-1,-1]]:
            p = trimesh.creation.box(extents=[frame_thickness, size, frame_thickness])
            p.apply_translation([off[0]*(size/2-frame_thickness/2), 0, off[1]*(size/2-frame_thickness/2)])
            parts.append(p)
        for y in [1, -1]:
            for z in [1, -1]:
                h = trimesh.creation.box(extents=[size, frame_thickness, frame_thickness])
                h.apply_translation([0, y*(size/2-frame_thickness/2), z*(size/2-frame_thickness/2)])
                parts.append(h)
        return trimesh.util.concatenate(parts)

    def create_locker(self, width=0.6, height=1.8, depth=0.5):
        body = self._create_high_res_box([width, height, depth])
        self.apply_vertex_displacement(body, strength=0.01)

        door = trimesh.creation.box(extents=[width*0.9, height*0.95, 0.05])
        self.apply_vertex_displacement(door, strength=0.01)
        door.apply_translation([0, 0, depth/2])

        handle = trimesh.creation.box(extents=[0.05, 0.2, 0.05])
        handle.apply_translation([width/3, 0, depth/2 + 0.05])
        return trimesh.util.concatenate([body, door, handle])

    def create_table(self, width=1.5, height=0.8, depth=0.8):
        top = self._create_high_res_box([width, 0.1, depth])
        self.apply_vertex_displacement(top, strength=0.015)
        top.apply_translation([0, height/2, 0])

        parts = [top]
        leg_w = 0.1
        for off in [[1,1], [1,-1], [-1,1], [-1,-1]]:
            leg = trimesh.creation.box(extents=[leg_w, height, leg_w])
            leg.apply_translation([off[0]*(width/2-leg_w), 0, off[1]*(depth/2-leg_w)])
            parts.append(leg)
        return trimesh.util.concatenate(parts)

    def create_vent(self, size=0.8):
        frame = trimesh.creation.box(extents=[size, size, 0.1])
        parts = [frame]
        for i in range(5):
            slat = trimesh.creation.box(extents=[size*0.8, 0.05, 0.02])
            slat.apply_transform(trimesh.transformations.rotation_matrix(np.pi/4, [1, 0, 0]))
            slat.apply_translation([0, -size/3 + i*(size/6), 0.05])
            parts.append(slat)
        return trimesh.util.concatenate(parts)

    def create_meathook(self, size=0.5):
        # Create a curved meathook using a torus segment or a bent cylinder
        # For simplicity, we'll use a series of small cylinders to form a hook shape
        parts = []
        # Vertical shaft
        shaft = trimesh.creation.cylinder(radius=0.02, height=size)
        shaft.apply_translation([0, size/2, 0])
        parts.append(shaft)
        # Curve
        for i in range(8):
            angle = (i / 7.0) * np.pi
            segment = trimesh.creation.cylinder(radius=0.02, height=0.1)
            # Rotate and position
            segment.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 0, 1]))
            segment.apply_translation([0.1 * np.sin(angle), -0.1 * np.cos(angle), 0])
            parts.append(segment)
        # Pointy end
        tip = trimesh.creation.cone(radius=0.02, height=0.1)
        tip.apply_translation([0.1, 0.1, 0])
        parts.append(tip)
        return trimesh.util.concatenate(parts)

    def create_cage(self, size=1.0):
        # Create a barred cage
        parts = []
        frame_thickness = 0.04
        # Corner pillars
        for x in [-1, 1]:
            for z in [-1, 1]:
                pillar = trimesh.creation.cylinder(radius=frame_thickness/2, height=size)
                pillar.apply_translation([x*(size/2), 0, z*(size/2)])
                parts.append(pillar)
        # Bars
        bar_count = 5
        for i in range(bar_count):
            offset = -size/2 + (i+1)*(size/(bar_count+1))
            for face in ['back', 'left', 'right']:
                bar = trimesh.creation.cylinder(radius=0.01, height=size)
                if face == 'back': bar.apply_translation([offset, 0, -size/2])
                elif face == 'left':
                    bar.apply_translation([-size/2, 0, offset])
                elif face == 'right':
                    bar.apply_translation([size/2, 0, offset])
                parts.append(bar)
        # Top and bottom frames
        for y in [-size/2, size/2]:
            for angle in [0, np.pi/2]:
                h_bar = trimesh.creation.box(extents=[size, frame_thickness, frame_thickness])
                h_bar.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 1, 0]))
                h_bar.apply_translation([0, y, 0])
                parts.append(h_bar)
        return trimesh.util.concatenate(parts)

    def apply_vertex_displacement(self, mesh, strength=0.01):
        if len(mesh.vertices) == 0: return mesh
        normals = mesh.vertex_normals
        noise = (np.random.rand(len(mesh.vertices), 1) - 0.5) * strength
        mesh.vertices += normals * noise
        return mesh

    def apply_improved_uv(self, mesh):
        bounds = mesh.bounds
        size = np.where((bounds[1]-bounds[0]) == 0, 1, bounds[1]-bounds[0])
        vertices, normals = mesh.vertices, mesh.vertex_normals
        uvs = np.zeros((len(vertices), 2))
        for i, n in enumerate(normals):
            if abs(n[0]) > abs(n[1]) and abs(n[0]) > abs(n[2]):
                uvs[i] = [(vertices[i, 1] - bounds[0][1]) / size[1], (vertices[i, 2] - bounds[0][2]) / size[2]]
            elif abs(n[1]) > abs(n[0]) and abs(n[1]) > abs(n[2]):
                uvs[i] = [(vertices[i, 0] - bounds[0][0]) / size[0], (vertices[i, 2] - bounds[0][2]) / size[2]]
            else:
                uvs[i] = [(vertices[i, 0] - bounds[0][0]) / size[0], (vertices[i, 1] - bounds[0][1]) / size[1]]
        mesh.visual = trimesh.visual.TextureVisuals(uv=uvs)
        return mesh

    def export(self, mesh, filename, maps=None):
        if not filename.endswith('.glb'): filename = os.path.splitext(filename)[0] + '.glb'
        filepath = os.path.join(self.output_dir, filename)
        if maps:
            try:
                albedo = Image.open(os.path.join(self.output_dir, maps['albedo']))
                normal = Image.open(os.path.join(self.output_dir, maps['normal']))
                rough = Image.open(os.path.join(self.output_dir, maps['roughness']))
                ao = Image.open(os.path.join(self.output_dir, maps['ao']))
                material = trimesh.visual.material.PBRMaterial(
                    baseColorTexture=albedo,
                    normalTexture=normal,
                    occlusionTexture=ao,
                    roughnessTexture=rough,
                    metallicFactor=0.0
                )
                mesh.visual.material = material
            except Exception as e: print(f"PBR embed error: {e}")
        mesh.export(filepath)
        return filepath

    def generate_godot_material(self, name, maps):
        tres_path = os.path.join(self.output_dir, f"{name}.tres")
        # Use paths relative to project root (assuming output is in horror_asset_gen/output)
        base_path = "res://horror_asset_gen/output/"
        tres_content = f"""[gd_resource type="StandardMaterial3D" load_steps=5 format=3]
[ext_resource type="Texture2D" path="{base_path}{maps['albedo']}" id="1"]
[ext_resource type="Texture2D" path="{base_path}{maps['normal']}" id="2"]
[ext_resource type="Texture2D" path="{base_path}{maps['roughness']}" id="3"]
[ext_resource type="Texture2D" path="{base_path}{maps['ao']}" id="4"]
[resource]
albedo_texture = ExtResource("1")
roughness_texture = ExtResource("3")
normal_enabled = true
normal_texture = ExtResource("2")
ao_enabled = true
ao_texture = ExtResource("4")"""
        with open(tres_path, "w") as f: f.write(tres_content)
        return tres_path

    def generate_godot_scene(self, name, asset_type, model_filename, material_filename):
        tscn_path = os.path.join(self.output_dir, f"{name}.tscn")
        base_path = "res://horror_asset_gen/output/"

        # Heuristic for collision shape
        shape_type = "BoxShape3D"
        shape_extents = "1, 1, 1"

        if asset_type in ["pipe", "barrel", "meathook"]:
            shape_type = "CylinderShape3D"
            if asset_type == "pipe": shape_extents = "height = 2.0\nradius = 0.05"
            elif asset_type == "barrel": shape_extents = "height = 1.0\nradius = 0.45"
            else: shape_extents = "height = 0.6\nradius = 0.1"
        elif asset_type == "wall": shape_extents = "size = Vector3(2, 2, 0.1)"
        elif asset_type == "crate": shape_extents = "size = Vector3(1, 1, 1)"
        elif asset_type == "floor": shape_extents = "size = Vector3(4, 0.05, 4)"
        elif asset_type == "table": shape_extents = "size = Vector3(1.5, 0.8, 0.8)"
        else: shape_extents = "size = Vector3(1, 1, 1)"

        tscn_content = f"""[gd_scene load_steps=4 format=3]

[ext_resource type="PackedScene" path="{base_path}{model_filename}" id="1"]
[ext_resource type="Material" path="{base_path}{material_filename}" id="2"]

[sub_resource type="{shape_type}" id="1"]
{shape_extents}

[node name="{name}" type="StaticBody3D"]

[node name="Mesh" parent="." instance=ExtResource("1")]
surface_material_override/0 = ExtResource("2")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("1")
"""
        with open(tscn_path, "w") as f:
            f.write(tscn_content)
        return tscn_path

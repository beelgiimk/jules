import trimesh
import numpy as np
import os

class ModelGenerator:
    def __init__(self, output_dir="horror_asset_gen/output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def create_wall(self, width=2.0, height=2.0, thickness=0.1):
        mesh = trimesh.creation.box(extents=[width, height, thickness])
        return mesh

    def create_pipe(self, radius=0.05, height=2.0, sections=16):
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
        return mesh

    def create_plank(self, width=0.2, length=2.0, thickness=0.02):
        mesh = trimesh.creation.box(extents=[width, length, thickness])
        return mesh

    def create_barrel(self, radius=0.4, height=1.0, sections=16):
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
        return mesh

    def create_crate(self, size=1.0):
        mesh = trimesh.creation.box(extents=[size, size, size])
        return mesh

    def create_beam(self, width=0.15, length=3.0, thickness=0.15):
        mesh = trimesh.creation.box(extents=[width, length, thickness])
        return mesh

    def create_floor(self, width=4.0, length=4.0, thickness=0.05):
        mesh = trimesh.creation.box(extents=[width, length, thickness])
        return mesh

    def apply_simple_uv(self, mesh):
        # Improved UV mapping for cylinder and box
        if hasattr(mesh, 'metadata') and mesh.metadata.get('primitive') == 'cylinder':
            # Cylinder UVs: theta around, height up
            # This is complex to do perfectly with trimesh.creation,
            # let's use a simpler heuristic for now.
            pass

        # Default: Project along major axes
        bounds = mesh.bounds
        size = bounds[1] - bounds[0]
        vertices = mesh.vertices
        uvs = np.zeros((len(vertices), 2))

        # Use simple projection but try to avoid extreme stretching by using the largest dimensions
        uvs[:, 0] = (vertices[:, 0] - bounds[0][0]) / size[0] if size[0] > 0 else 0
        uvs[:, 1] = (vertices[:, 1] - bounds[0][1]) / size[1] if size[1] > 0 else 0

        mesh.visual = trimesh.visual.TextureVisuals(uv=uvs)
        return mesh

    def export(self, mesh, filename, albedo_name=None):
        filepath = os.path.join(self.output_dir, filename)

        # Link the material if albedo_name is provided
        if albedo_name:
            material = trimesh.visual.material.SimpleMaterial(image=albedo_name)
            mesh.visual.material = material

        mesh.export(filepath)
        return filepath

import trimesh
import numpy as np
import os

class ModelGenerator:
    def __init__(self, output_dir="horror_asset_gen/output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _create_high_res_box(self, extents):
        mesh = trimesh.creation.box(extents=extents)
        # Subdivide to get more vertices for displacement/detail
        for _ in range(3):
            mesh = mesh.subdivide()
        return mesh

    def create_wall(self, width=2.0, height=2.0, thickness=0.1):
        return self._create_high_res_box([width, height, thickness])

    def create_pipe(self, radius=0.05, height=2.0, sections=64):
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
        return mesh

    def create_plank(self, width=0.2, length=2.0, thickness=0.02):
        return self._create_high_res_box([width, length, thickness])

    def create_barrel(self, radius=0.4, height=1.0, sections=64):
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
        vertices = mesh.vertices
        center_y = np.mean(vertices[:, 1])
        dist_from_center = np.abs(vertices[:, 1] - center_y)
        bulge = 1.0 + (1.0 - (dist_from_center / (height / 2))) * 0.15
        vertices[:, 0] *= bulge
        vertices[:, 2] *= bulge
        mesh.vertices = vertices
        return mesh

    def create_crate(self, size=1.0):
        return self._create_high_res_box([size, size, size])

    def create_beam(self, width=0.15, length=3.0, thickness=0.15):
        return self._create_high_res_box([width, length, thickness])

    def create_floor(self, width=4.0, length=4.0, thickness=0.05):
        return self._create_high_res_box([width, length, thickness])

    def apply_vertex_displacement(self, mesh, strength=0.015):
        # Displacement along normals for a more natural organic look
        normals = mesh.vertex_normals
        noise = np.random.normal(0, strength, (len(mesh.vertices), 1))
        mesh.vertices += normals * noise
        return mesh

    def apply_improved_uv(self, mesh):
        bounds = mesh.bounds
        size = bounds[1] - bounds[0]
        # Avoid division by zero
        size = np.where(size == 0, 1, size)

        vertices = mesh.vertices
        uvs = np.zeros((len(vertices), 2))

        normals = mesh.vertex_normals
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
        filepath = os.path.join(self.output_dir, filename)
        if maps:
            material = trimesh.visual.material.SimpleMaterial(
                image=maps.get('albedo'),
                normal_map=maps.get('normal')
            )
            mesh.visual.material = material
        mesh.export(filepath)
        return filepath

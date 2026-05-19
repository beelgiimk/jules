import trimesh
import numpy as np
import os

class ModelGenerator:
    def __init__(self, output_dir="horror_asset_gen/output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def create_wall(self, width=2.0, height=2.0, thickness=0.1):
        # Create a simple box mesh
        mesh = trimesh.creation.box(extents=[width, height, thickness])
        return mesh

    def create_pipe(self, radius=0.05, height=2.0, sections=16):
        # Create a cylinder mesh
        mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
        return mesh

    def create_plank(self, width=0.2, length=2.0, thickness=0.02):
        # Create a long thin box
        mesh = trimesh.creation.box(extents=[width, length, thickness])
        return mesh

    def apply_simple_uv(self, mesh):
        # Simple projection UV mapping for basic shapes
        # Trimesh has some built-in UV generation
        # For a box/cylinder, we can use simple projections
        bounds = mesh.bounds
        size = bounds[1] - bounds[0]

        # Simple planar projection based on the largest faces
        # In a real tool we'd want better unwrapping, but for "game-ready" basic assets
        # this is a starting point.
        vertices = mesh.vertices
        uvs = np.zeros((len(vertices), 2))

        # Just use X and Y coordinates scaled to [0, 1]
        uvs[:, 0] = (vertices[:, 0] - bounds[0][0]) / size[0] if size[0] > 0 else 0
        uvs[:, 1] = (vertices[:, 1] - bounds[0][1]) / size[1] if size[1] > 0 else 0

        mesh.visual = trimesh.visual.TextureVisuals(uv=uvs)
        return mesh

    def export(self, mesh, filename):
        filepath = os.path.join(self.output_dir, filename)
        mesh.export(filepath)
        return filepath

import numpy as np
from PIL import Image
import opensimplex
import os

class TextureGenerator:
    def __init__(self, size=(1024, 1024)):
        self.size = size
        opensimplex.seed(np.random.randint(0, 1000000))

    def generate_noise(self, scale=10.0, octaves=4, persistence=0.5, lacunarity=2.0):
        width, height = self.size
        noise_map = np.zeros(self.size)

        for i in range(octaves):
            freq = scale * (lacunarity ** i)
            amp = persistence ** i

            # Create a grid for noise sampling
            x = np.linspace(0, freq, width)
            y = np.linspace(0, freq, height)
            xv, yv = np.meshgrid(x, y)

            # Vectorized noise generation if possible, but opensimplex might need loops or map
            # We'll use a simpler approach for now to ensure it works
            for r in range(height):
                for c in range(width):
                    noise_map[r, c] += opensimplex.noise2(xv[r, c], yv[r, c]) * amp

        # Normalize to 0-1
        noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
        return noise_map

    def apply_color_gradient(self, noise_map, color1, color2):
        # color1 and color2 are (R, G, B) tuples
        res = np.zeros((self.size[0], self.size[1], 3), dtype=np.uint8)
        for i in range(3):
            res[:, :, i] = (noise_map * color1[i] + (1 - noise_map) * color2[i]).astype(np.uint8)
        return Image.fromarray(res)

    def generate_concrete(self):
        noise = self.generate_noise(scale=20.0, octaves=6)
        # Concrete is usually gray with variations
        return self.apply_color_gradient(noise, (120, 120, 120), (80, 80, 80))

    def generate_metal(self):
        noise = self.generate_noise(scale=5.0, octaves=3)
        # Darker metallic look
        return self.apply_color_gradient(noise, (60, 60, 65), (40, 40, 42))

    def generate_normal_map(self, noise_map, strength=1.0):
        # Calculate gradients
        dy, dx = np.gradient(noise_map)

        # Standardize and apply strength
        dx = dx * strength
        dy = dy * strength

        # Calculate normal vector (dx, dy, 1) and normalize
        mag = np.sqrt(dx**2 + dy**2 + 1)
        nx = dx / mag
        ny = dy / mag
        nz = 1 / mag

        # Map from [-1, 1] to [0, 255]
        res = np.zeros((self.size[0], self.size[1], 3), dtype=np.uint8)
        res[:, :, 0] = ((nx + 1) * 127.5).astype(np.uint8)
        res[:, :, 1] = ((ny + 1) * 127.5).astype(np.uint8)
        res[:, :, 2] = ((nz + 1) * 127.5).astype(np.uint8)

        return Image.fromarray(res)

class HorrorEffects:
    @staticmethod
    def apply_grime(image, seed=None):
        if seed: np.random.seed(seed)
        width, height = image.size
        # Simple grime: darken random patches
        overlay = Image.new('L', image.size, 0)
        gen = TextureGenerator(size=image.size)
        noise = gen.generate_noise(scale=15.0, octaves=4)

        img_arr = np.array(image).astype(float)
        # Darken where noise is high
        for i in range(3):
            img_arr[:, :, i] *= (1.0 - 0.5 * noise)

        return Image.fromarray(img_arr.astype(np.uint8))

    @staticmethod
    def apply_rust(image, seed=None):
        if seed: np.random.seed(seed)
        gen = TextureGenerator(size=image.size)
        noise = gen.generate_noise(scale=10.0, octaves=5)

        img_arr = np.array(image).astype(float)
        rust_color = np.array([139, 69, 19]) # Saddle Brown

        # Blend rust color where noise > 0.6
        mask = np.clip((noise - 0.6) * 5, 0, 1)
        for i in range(3):
            img_arr[:, :, i] = img_arr[:, :, i] * (1 - mask) + rust_color[i] * mask

        return Image.fromarray(img_arr.astype(np.uint8))

    @staticmethod
    def apply_blood(image, seed=None):
        if seed: np.random.seed(seed)
        gen = TextureGenerator(size=image.size)
        noise = gen.generate_noise(scale=30.0, octaves=2)

        img_arr = np.array(image).astype(float)
        blood_color = np.array([138, 3, 3]) # Blood Red

        # Blood splatters
        mask = np.clip((noise - 0.8) * 10, 0, 1)
        for i in range(3):
            img_arr[:, :, i] = img_arr[:, :, i] * (1 - mask) + blood_color[i] * mask

        return Image.fromarray(img_arr.astype(np.uint8))

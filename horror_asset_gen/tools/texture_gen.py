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

        # Optimized: Use vectorized operations where possible
        # However opensimplex doesn't support vectorization directly.
        # We'll use a faster way to sample if possible or just accept it's a bit slow but correct.
        for i in range(octaves):
            freq = scale * (lacunarity ** i)
            amp = persistence ** i

            # Create a grid for noise sampling
            x = np.linspace(0, freq, width)
            y = np.linspace(0, freq, height)
            xv, yv = np.meshgrid(x, y)

            # Sample noise - still needs a way to be faster.
            # Vectorized opensimplex is not easy without external C++ libs.
            # But let's at least make sure albedo and normal use the SAME noise.
            for r in range(height):
                for c in range(width):
                    noise_map[r, c] += opensimplex.noise2(xv[r, c], yv[r, c]) * amp

        # Normalize to 0-1
        noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
        return noise_map

    def apply_color_gradient(self, noise_map, color1, color2):
        res = np.zeros((self.size[0], self.size[1], 3), dtype=np.uint8)
        for i in range(3):
            res[:, :, i] = (noise_map * color1[i] + (1 - noise_map) * color2[i]).astype(np.uint8)
        return Image.fromarray(res)

    def generate_concrete(self):
        noise = self.generate_noise(scale=20.0, octaves=6)
        return self.apply_color_gradient(noise, (120, 120, 120), (80, 80, 80)), noise

    def generate_metal(self):
        noise = self.generate_noise(scale=5.0, octaves=3)
        return self.apply_color_gradient(noise, (60, 60, 65), (40, 40, 42)), noise

    def generate_wood(self):
        noise = self.generate_noise(scale=10.0, octaves=4)
        return self.apply_color_gradient(noise, (101, 67, 33), (60, 40, 20)), noise

    def generate_brick(self):
        img = np.full((self.size[0], self.size[1], 3), (150, 75, 75), dtype=np.uint8)
        brick_w, brick_h = 128, 64
        mortar_w = 4
        for r in range(0, self.size[0], brick_h):
            offset = (brick_w // 2) if (r // brick_h) % 2 == 0 else 0
            for c in range(-offset, self.size[1], brick_w):
                img[r:r+mortar_w, :, :] = (100, 100, 100)
                img[:, max(0, c):min(self.size[1], c+mortar_w), :] = (100, 100, 100)
        # For bricks, heightmap is roughly inverse of mortar
        heightmap = np.mean(img, axis=2) / 255.0
        return Image.fromarray(img), heightmap

    def generate_tile(self):
        img = np.full((self.size[0], self.size[1], 3), (200, 200, 200), dtype=np.uint8)
        tile_size = 128
        mortar_w = 4
        for i in range(0, self.size[0], tile_size):
            img[i:i+mortar_w, :, :] = (50, 50, 50)
            img[:, i:i+mortar_w, :] = (50, 50, 50)
        heightmap = np.mean(img, axis=2) / 255.0
        return Image.fromarray(img), heightmap

    def generate_normal_map(self, noise_map, strength=1.0):
        dy, dx = np.gradient(noise_map)
        dx = dx * strength
        dy = dy * strength
        mag = np.sqrt(dx**2 + dy**2 + 1)
        nx = dx / mag
        ny = dy / mag
        nz = 1 / mag
        res = np.zeros((self.size[0], self.size[1], 3), dtype=np.uint8)
        res[:, :, 0] = ((nx + 1) * 127.5).astype(np.uint8)
        res[:, :, 1] = ((ny + 1) * 127.5).astype(np.uint8)
        res[:, :, 2] = ((nz + 1) * 127.5).astype(np.uint8)
        return Image.fromarray(res)

class HorrorEffects:
    @staticmethod
    def apply_grime(image, noise_map=None):
        img_arr = np.array(image).astype(float)
        if noise_map is None:
            gen = TextureGenerator(size=image.size)
            noise_map = gen.generate_noise(scale=15.0, octaves=4)
        for i in range(3):
            img_arr[:, :, i] *= (1.0 - 0.5 * noise_map)
        return Image.fromarray(img_arr.astype(np.uint8))

    @staticmethod
    def apply_rust(image, noise_map=None):
        img_arr = np.array(image).astype(float)
        rust_color = np.array([139, 69, 19])
        if noise_map is None:
            gen = TextureGenerator(size=image.size)
            noise_map = gen.generate_noise(scale=10.0, octaves=5)
        mask = np.clip((noise_map - 0.6) * 5, 0, 1)
        for i in range(3):
            img_arr[:, :, i] = img_arr[:, :, i] * (1 - mask) + rust_color[i] * mask
        return Image.fromarray(img_arr.astype(np.uint8))

    @staticmethod
    def apply_blood(image, noise_map=None):
        img_arr = np.array(image).astype(float)
        blood_color = np.array([138, 3, 3])
        if noise_map is None:
            gen = TextureGenerator(size=image.size)
            noise_map = gen.generate_noise(scale=30.0, octaves=2)
        mask = np.clip((noise_map - 0.8) * 10, 0, 1)
        for i in range(3):
            img_arr[:, :, i] = img_arr[:, :, i] * (1 - mask) + blood_color[i] * mask
        return Image.fromarray(img_arr.astype(np.uint8))

    @staticmethod
    def apply_rot(image, noise_map=None):
        img_arr = np.array(image).astype(float)
        rot_color = np.array([40, 50, 20])
        if noise_map is None:
            gen = TextureGenerator(size=image.size)
            noise_map = gen.generate_noise(scale=8.0, octaves=3)
        mask = np.clip((noise_map - 0.5) * 4, 0, 1)
        for i in range(3):
            img_arr[:, :, i] = img_arr[:, :, i] * (1 - mask) + rot_color[i] * mask
        return Image.fromarray(img_arr.astype(np.uint8))

    @staticmethod
    def apply_slime(image, noise_map=None):
        img_arr = np.array(image).astype(float)
        slime_color = np.array([50, 200, 50])
        if noise_map is None:
            gen = TextureGenerator(size=image.size)
            noise_map = gen.generate_noise(scale=12.0, octaves=4)
        mask = np.clip((noise_map - 0.7) * 8, 0, 1)
        for i in range(3):
            img_arr[:, :, i] = img_arr[:, :, i] * (1 - mask) + slime_color[i] * mask
        return Image.fromarray(img_arr.astype(np.uint8))

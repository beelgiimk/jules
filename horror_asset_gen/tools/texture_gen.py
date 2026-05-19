import numpy as np
from PIL import Image
import opensimplex
import os

class TextureGenerator:
    def __init__(self, size=(1024, 1024), seed=None):
        self.size = size
        self.seed = seed if seed is not None else np.random.randint(0, 1000000)
        opensimplex.seed(self.seed)
        np.random.seed(self.seed)

    def generate_noise(self, scale=10.0, octaves=4, persistence=0.5, lacunarity=2.0):
        width, height = self.size
        noise_map = np.zeros(self.size)
        x = np.linspace(0, 1, width)
        y = np.linspace(0, 1, height)
        xv, yv = np.meshgrid(x, y)
        for i in range(octaves):
            freq = scale * (lacunarity ** i)
            amp = persistence ** i
            for r in range(height):
                for c in range(width):
                    noise_map[r, c] += opensimplex.noise2(xv[r, c] * freq, yv[r, c] * freq) * amp
        noise_min, noise_max = noise_map.min(), noise_map.max()
        if noise_max > noise_min:
            noise_map = (noise_map - noise_min) / (noise_max - noise_min)
        return noise_map

    def generate_voronoi(self, points_count=20):
        width, height = self.size
        points = np.random.rand(points_count, 2) * [width, height]
        y, x = np.ogrid[:height, :width]
        dist = np.sqrt((x - points[:, 0, np.newaxis, np.newaxis])**2 +
                       (y - points[:, 1, np.newaxis, np.newaxis])**2)
        noise_map = np.min(dist, axis=0)
        noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
        return noise_map

    def apply_color_gradient(self, noise_map, color1, color2):
        res = np.zeros((self.size[0], self.size[1], 3), dtype=np.uint8)
        for i in range(3):
            res[:, :, i] = (noise_map * color1[i] + (1 - noise_map) * color2[i]).astype(np.uint8)
        return Image.fromarray(res)

    def generate_roughness_map(self, noise_map, invert=False):
        roughness = noise_map.copy()
        if invert: roughness = 1.0 - roughness
        roughness = np.clip(roughness * 0.8 + 0.1, 0, 1)
        return Image.fromarray((roughness * 255).astype(np.uint8))

    def generate_ao_map(self, noise_map):
        ao = np.clip(noise_map * 0.5 + 0.5, 0, 1)
        return Image.fromarray((ao * 255).astype(np.uint8))

    def generate_concrete(self):
        base_noise = self.generate_noise(scale=5.0, octaves=4)
        detail_noise = self.generate_noise(scale=50.0, octaves=2)
        combined = base_noise * 0.7 + detail_noise * 0.3
        img = self.apply_color_gradient(combined, (140, 140, 140), (80, 80, 80))
        return img, combined

    def generate_metal(self):
        base_noise = self.generate_noise(scale=3.0, octaves=3)
        scratches = self.generate_noise(scale=100.0, octaves=1)
        combined = base_noise * 0.9 + scratches * 0.1
        img = self.apply_color_gradient(combined, (80, 80, 85), (40, 40, 45))
        return img, combined

    def generate_wood(self):
        width, height = self.size
        noise_map = np.zeros(self.size)
        scale_x, scale_y = 5.0, 50.0
        x = np.linspace(0, scale_x, width)
        y = np.linspace(0, scale_y, height)
        xv, yv = np.meshgrid(x, y)
        for r in range(height):
            for c in range(width):
                noise_map[r, c] = opensimplex.noise2(xv[r, c], yv[r, c])
        noise_map = (noise_map - noise_map.min()) / (noise_map.max() - noise_map.min())
        img = self.apply_color_gradient(noise_map, (100, 60, 30), (50, 30, 15))
        return img, noise_map

    def generate_brick(self):
        img_arr = np.full((self.size[0], self.size[1], 3), (150, 70, 60), dtype=np.uint8)
        height_map = np.ones(self.size)
        brick_w, brick_h = 128, 64
        mortar_w = 6
        for r in range(0, self.size[0], brick_h):
            offset = (brick_w // 2) if (r // brick_h) % 2 == 0 else 0
            img_arr[r:r+mortar_w, :, :] = (80, 80, 80)
            height_map[r:r+mortar_w, :] = 0.2
            for c in range(-offset, self.size[1] + brick_w, brick_w):
                c_start = max(0, c)
                c_end = min(self.size[1], c + mortar_w)
                img_arr[r:r+brick_h, c_start:c_end, :] = (80, 80, 80)
                height_map[r:r+brick_h, c_start:c_end] = 0.2
                if c_start < self.size[1] and r < self.size[0]:
                    var = np.random.randint(-20, 20)
                    r_end = min(self.size[0], r + brick_h)
                    c_b_end = min(self.size[1], c + brick_w)
                    img_arr[r+mortar_w:r_end, c_start+mortar_w:c_b_end] += var
        noise = self.generate_noise(scale=40.0, octaves=2)
        height_map = height_map * (0.8 + 0.2 * noise)
        return Image.fromarray(img_arr), height_map

    def generate_tile(self):
        img_arr = np.full((self.size[0], self.size[1], 3), (210, 210, 220), dtype=np.uint8)
        height_map = np.ones(self.size)
        tile_size = 128
        mortar_w = 4
        for i in range(0, self.size[0], tile_size):
            img_arr[i:i+mortar_w, :, :] = (40, 40, 45)
            img_arr[:, i:i+mortar_w, :] = (40, 40, 45)
            height_map[i:i+mortar_w, :] = 0.1
            height_map[:, i:i+mortar_w] = 0.1
        noise = self.generate_noise(scale=100.0, octaves=1)
        height_map = height_map * (0.95 + 0.05 * noise)
        return Image.fromarray(img_arr), height_map

    def generate_normal_map(self, noise_map, strength=2.0):
        dy, dx = np.gradient(noise_map)
        dx, dy = dx * strength, dy * strength
        mag = np.sqrt(dx**2 + dy**2 + 1)
        nx, ny, nz = dx / mag, dy / mag, 1 / mag
        res = np.zeros((self.size[0], self.size[1], 3), dtype=np.uint8)
        res[:, :, 0] = ((nx + 1) * 127.5).astype(np.uint8)
        res[:, :, 1] = ((ny + 1) * 127.5).astype(np.uint8)
        res[:, :, 2] = ((nz + 1) * 127.5).astype(np.uint8)
        return Image.fromarray(res)

class HorrorEffects:
    @staticmethod
    def apply_grime(image, noise_map):
        img_arr = np.array(image).astype(float)
        mask = np.clip((noise_map - 0.4) * 2, 0, 1)
        for i in range(3): img_arr[:, :, i] *= (1.0 - 0.6 * mask)
        return Image.fromarray(img_arr.astype(np.uint8))

    @staticmethod
    def apply_rust(image, noise_map):
        img_arr = np.array(image).astype(float)
        rust_color = np.array([120, 50, 20])
        mask = np.clip((noise_map - 0.5) * 3, 0, 1)
        for i in range(3): img_arr[:, :, i] = img_arr[:, :, i] * (1 - mask) + rust_color[i] * mask
        return Image.fromarray(img_arr.astype(np.uint8))

    @staticmethod
    def apply_blood(image, noise_map):
        img_arr = np.array(image).astype(float)
        blood_color = np.array([100, 5, 5])
        mask = np.clip((noise_map - 0.7) * 5, 0, 1)
        for i in range(3): img_arr[:, :, i] = img_arr[:, :, i] * (1 - mask) + blood_color[i] * mask
        return Image.fromarray(img_arr.astype(np.uint8))

    @staticmethod
    def apply_rot(image, noise_map):
        img_arr = np.array(image).astype(float)
        rot_color = np.array([30, 40, 15])
        mask = np.clip((noise_map - 0.4) * 2, 0, 1)
        for i in range(3): img_arr[:, :, i] = img_arr[:, :, i] * (1 - mask) + rot_color[i] * mask
        return Image.fromarray(img_arr.astype(np.uint8))

    @staticmethod
    def apply_slime(image, noise_map):
        img_arr = np.array(image).astype(float)
        slime_color = np.array([40, 150, 40])
        mask = np.clip((noise_map - 0.6) * 4, 0, 1)
        for i in range(3): img_arr[:, :, i] = img_arr[:, :, i] * (1 - mask) + slime_color[i] * mask
        return Image.fromarray(img_arr.astype(np.uint8))

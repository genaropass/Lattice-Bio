"""
Generador de imágenes de muestra para pruebas inmediatas en MorphoEngine.
"""

import os
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

os.makedirs("data/muestras", exist_ok=True)

# 1. Simulación Muestra 1: Hueso Trabecular Denso y Sano
np.random.seed(101)
grid1 = np.random.randn(512, 512)
smooth1 = gaussian_filter(grid1, sigma=4.0)
norm1 = (smooth1 - smooth1.min()) / (smooth1.max() - smooth1.min())
img_sano = (norm1 * 255).astype(np.uint8)
Image.fromarray(img_sano).save("data/muestras/01_hueso_sano_referencia.png")

# 2. Simulación Muestra 2: Hueso con Pérdida Ósea / Porosidad Avanzada
np.random.seed(202)
grid2 = np.random.randn(512, 512)
smooth2 = gaussian_filter(grid2, sigma=7.0)
norm2 = (smooth2 - smooth2.min()) / (smooth2.max() - smooth2.min())
# Añadir zonas de reabsorción ósea (zonas oscuras más grandes)
holes = gaussian_filter(np.random.randn(512, 512), sigma=20.0) > 0.6
norm2[holes] = norm2[holes] * 0.3
img_osteo = (norm2 * 255).astype(np.uint8)
Image.fromarray(img_osteo).save("data/muestras/02_hueso_periodontitis_simulada.png")

print("Muestras creadas en data/muestras/")

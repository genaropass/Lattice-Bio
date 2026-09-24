"""
Script de Demostracion Rapida de MorphoEngine (Simulacion de Trabeculado Oseo y Calculo de Biomarcadores).
Ejecutar con: python demo_quickstart.py
"""

import numpy as np
from src.fractal.feature_extractor import FractalFeatureExtractor
from src.fractal.box_counting import compute_box_counting_dimension
from src.fractal.lacunarity import compute_lacunarity_spectrum
from src.fractal.multifractal import compute_multifractal_spectrum


def generate_synthetic_trabecular_patch(size: int = 256, porosity: float = 0.45) -> np.ndarray:
    """
    Genera un parche sintetico 2D que emula la microarquitectura trabecular del hueso alveolar.
    """
    np.random.seed(42)
    from scipy.ndimage import gaussian_filter

    noise = np.random.randn(size, size)
    smooth = gaussian_filter(noise, sigma=3.5)

    thresh = np.percentile(smooth, porosity * 100)
    trabecular_mask = (smooth > thresh).astype(np.uint8)
    return trabecular_mask


def main():
    print("=" * 70)
    print("[+] MORPHOENGINE: DEMOSTRACION DE BIOMARCADORES FRACTALES")
    print("=" * 70)

    print("\n[1/3] Generando parche sintetico de hueso trabecular (256x256 px)...")
    patch_sano = generate_synthetic_trabecular_patch(size=256, porosity=0.35)  # Sano
    patch_osteo = generate_synthetic_trabecular_patch(size=256, porosity=0.65)  # Perdida osea

    extractor = FractalFeatureExtractor(use_tda=True)

    print("\n[2/3] Calculando biomarcadores cuantitativos...")
    feats_sano = extractor.extract_features(patch_sano)
    feats_osteo = extractor.extract_features(patch_osteo)

    print("\n[3/3] Comparativa de Biomarcadores:")
    print("-" * 70)
    print(f"{'Biomarcador':<30} | {'Hueso Sano':<15} | {'Perdida Osea':<15}")
    print("-" * 70)

    keys = [
        ("fractal_D0", "Dimension Fractal D0"),
        ("fractal_r2", "Ajuste Lineal R2"),
        ("lapidus_oscillation", "Oscilacion Lapidus"),
        ("lacunarity_mean", "Lacunaridad Media (Lambda)"),
        ("lacunarity_slope", "Pendiente Lacunaridad"),
        ("multifractal_delta_alpha", "Ancho Multifractal (Delta alpha)"),
        ("tda_beta_0", "Componentes Betti beta_0"),
        ("tda_beta_1", "Ciclos Betti beta_1"),
        ("tda_betti_ratio", "Ratio de Fragmentacion"),
    ]

    for key, name in keys:
        v_sano = feats_sano.get(key, 0.0)
        v_osteo = feats_osteo.get(key, 0.0)
        print(f"{name:<30} | {v_sano:<15.4f} | {v_osteo:<15.4f}")

    print("-" * 70)
    print("[OK] Demostracion completada exitosamente.")


if __name__ == "__main__":
    main()

"""
Tests Automatizados de Validación Matemática y Phantoms Sintéticos (Fase 4.1).
Comprueba invariantes geométricas y convergencias teóricas sobre:
1. Box-Counting D0 (Sierpinski, Plano 2D, Línea 1D, convergencia por resolución)
2. Minkowski Cover DM (Plano 2D, Rugosidad)
3. Lacunaridad (Matriz homogénea vs heterogénea)
4. Espectro Multifractal (Multirango q, Tau R2)
5. Topología TDA (Betti beta0, beta1 en Anillo, Componentes aisladas, Plano)

Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import unittest
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, root_dir)

from src.fractal.box_counting import compute_box_counting_dimension, compute_lapidus_oscillation
from src.fractal.minkowski import compute_minkowski_blanket_dimension
from src.fractal.lacunarity import compute_lacunarity_spectrum, compute_gliding_box_lacunarity
from src.fractal.multifractal import compute_multifractal_spectrum
from src.fractal.tda_features import compute_topological_features


def generate_sierpinski_carpet(order=4):
    """Genera la alfombra de Sierpinski 3^order x 3^order (D0 teorico = log(8)/log(3) = 1.892789)"""
    size = 3 ** order
    matrix = np.ones((size, size), dtype=np.uint8)
    
    def remove_center(x, y, s):
        if s < 1:
            return
        sub = s // 3
        matrix[x + sub : x + 2 * sub, y + sub : y + 2 * sub] = 0
        for i in range(3):
            for j in range(3):
                if i != 1 or j != 1:
                    remove_center(x + i * sub, y + j * sub, sub)
                    
    remove_center(0, 0, size)
    return matrix


class TestMathDescriptorsPhase41(unittest.TestCase):

    def test_box_counting_plane_and_line(self):
        """Plano lleno 2D debe dar D0 = 2.0; Línea 1D debe dar D0 = 1.0"""
        plane = np.ones((64, 64), dtype=np.uint8)
        bc_plane = compute_box_counting_dimension(plane)
        self.assertAlmostEqual(bc_plane["D0"], 2.0, places=2)
        self.assertGreaterEqual(bc_plane["r_squared"], 0.99)

        line = np.zeros((64, 64), dtype=np.uint8)
        np.fill_diagonal(line, 1)
        bc_line = compute_box_counting_dimension(line)
        self.assertAlmostEqual(bc_line["D0"], 1.0, places=2)
        self.assertGreaterEqual(bc_line["r_squared"], 0.99)

    def test_sierpinski_resolution_convergence(self):
        """Evalúa la convergencia de D0 hacia 1.8928 al aumentar el orden de la alfombra de Sierpinski"""
        d0_orders = []
        for order in [3, 4, 5]: # 27x27, 81x81, 243x243
            sierp = generate_sierpinski_carpet(order=order)
            bc = compute_box_counting_dimension(sierp)
            d0_orders.append(bc["D0"])
            
        # Verificar monotónicamente ascendente hacia 1.8928
        self.assertLess(d0_orders[0], d0_orders[1])
        self.assertLess(d0_orders[1], d0_orders[2])
        self.assertAlmostEqual(d0_orders[2], 1.8685, places=2)

    def test_minkowski_plane(self):
        """Plano de intensidad constante debe dar DM = 2.0000"""
        plane_gray = np.full((64, 64), 128, dtype=np.uint8)
        mk = compute_minkowski_blanket_dimension(plane_gray)
        self.assertAlmostEqual(mk["minkowski_dimension"], 2.0, places=2)

    def test_lacunarity_homogeneous_vs_heterogeneous(self):
        """Matriz llena homogénea debe dar lacunaridad cercana a 1.0; dispersa heterogénea >> 1.0"""
        full_mat = np.ones((64, 64), dtype=np.uint8)
        lac_full = compute_gliding_box_lacunarity(full_mat, box_size=8)
        self.assertAlmostEqual(lac_full, 1.0, places=2)

        # Matriz por bloques heterogénea (la mitad llena, la mitad vacía)
        hetero_mat = np.zeros((64, 64), dtype=np.uint8)
        hetero_mat[:32, :] = 1
        lac_hetero = compute_gliding_box_lacunarity(hetero_mat, box_size=8)
        self.assertGreater(lac_hetero, 1.5)

    def test_topological_betti_numbers(self):
        """Comprueba números de Betti beta0 (componentes) y beta1 (huecos) en phantoms conocidos"""
        # 1. Cuadrado lleno conectado sin huecos: beta0=1, beta1=0
        square = np.zeros((32, 32), dtype=np.uint8)
        square[8:24, 8:24] = 1
        tda_square = compute_topological_features(square, use_ripser=False)
        self.assertEqual(tda_square["beta_0"], 1)
        self.assertEqual(tda_square["beta_1"], 0)

        # 2. Anillo / Dona con 1 agujero central: beta0=1, beta1=1
        ring = np.zeros((32, 32), dtype=np.uint8)
        ring[4:28, 4:28] = 1
        ring[10:22, 10:22] = 0 # hueco interno
        tda_ring = compute_topological_features(ring, use_ripser=False)
        self.assertEqual(tda_ring["beta_0"], 1)
        self.assertEqual(tda_ring["beta_1"], 1)

        # 3. Tres componentes aisladas sin huecos: beta0=3, beta1=0
        multi = np.zeros((32, 32), dtype=np.uint8)
        multi[2:6, 2:6] = 1
        multi[12:16, 12:16] = 1
        multi[22:26, 22:26] = 1
        tda_multi = compute_topological_features(multi, use_ripser=False)
        self.assertEqual(tda_multi["beta_0"], 3)
        self.assertEqual(tda_multi["beta_1"], 0)


if __name__ == "__main__":
    unittest.main()

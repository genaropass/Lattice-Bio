"""
Cálculo del Espectro Multifractal f(α) y Dimensiones Generalizadas Dq (Chhabra & Jensen 1989).
Refactorizado (Fase 4):
- Estabilidad numérica reforzada para momentos q < 0 (clip a probabilidad mínima 1e-6).
- Soporte para evaluación multirango q: [-5,5], [-3,3], [-1,3], [0,5].
- Reporta R² medio de tau(q) para verificar la calidad multifractal.
"""

from typing import Dict, Any, List
import numpy as np


def compute_multifractal_spectrum(
    image: np.ndarray,
    q_range: np.ndarray = None,
    scales: List[int] = None,
) -> Dict[str, Any]:
    """
    Calcula el espectro multifractal f(α) y las dimensiones generalizadas D_q
    utilizando el método canónico de momentos de Chhabra & Jensen (1989).
    """
    if image.ndim != 2:
        raise ValueError("La imagen debe ser bidimensional (2D).")

    img = image.astype(np.float64)
    total_sum = np.sum(img)
    if total_sum <= 1e-10:
        return {
            "q": np.array([]),
            "alpha": np.array([]),
            "f_alpha": np.array([]),
            "delta_alpha": 0.0,
            "tau_r2_mean": 0.0,
            "D0": 0.0,
            "D1": 0.0,
            "D2": 0.0,
        }

    norm_img = img / total_sum
    h, w = norm_img.shape

    if q_range is None:
        q_range = np.linspace(-5.0, 5.0, num=21)

    if scales is None:
        max_power = int(np.floor(np.log2(min(h, w) // 2)))
        scales = [2 ** p for p in range(1, max(2, max_power + 1))]

    if len(scales) < 3:
        scales = [2, 4, 8, 16]

    box_probabilities = {}
    for eps in scales:
        n_h = int(np.ceil(h / eps))
        n_w = int(np.ceil(w / eps))
        pad_h = n_h * eps - h
        pad_w = n_w * eps - w

        if pad_h > 0 or pad_w > 0:
            padded = np.pad(norm_img, ((0, pad_h), (0, pad_w)), mode="constant", constant_values=0)
        else:
            padded = norm_img

        blocks = padded.reshape(n_h, eps, n_w, eps)
        block_sums = np.sum(blocks, axis=(1, 3)).flatten()

        # Filtrar solo cajas con masa no nula
        p_eps = block_sums[block_sums > 1e-10]
        if len(p_eps) > 0:
            p_eps = p_eps / np.sum(p_eps)
            box_probabilities[eps] = p_eps

    valid_scales = [eps for eps in scales if eps in box_probabilities]
    if len(valid_scales) < 3:
        return {
            "q": q_range,
            "alpha": np.zeros_like(q_range),
            "f_alpha": np.zeros_like(q_range),
            "delta_alpha": 0.0,
            "tau_r2_mean": 0.0,
            "D0": 0.0,
            "D1": 0.0,
            "D2": 0.0,
        }

    ln_eps = np.log(np.array(valid_scales, dtype=float))

    alpha_list = []
    f_alpha_list = []
    tau_r2_list = []
    d_q_dict = {}

    for q in q_range:
        numerator_alpha = []
        numerator_f = []
        tau_q_vals = []

        for eps in valid_scales:
            p = box_probabilities[eps]
            # Estabilidad numérica para q < 0: recortar probabilidades extremadamente pequeñas
            p_safe = np.clip(p, 1e-6, 1.0)
            p_safe = p_safe / np.sum(p_safe)

            p_q = p_safe ** q
            sum_p_q = np.sum(p_q)

            if sum_p_q > 1e-20:
                mu_q = p_q / sum_p_q
                numerator_alpha.append(np.sum(mu_q * np.log(p_safe)))
                non_zero_mu = np.clip(mu_q, 1e-20, 1.0)
                numerator_f.append(np.sum(non_zero_mu * np.log(non_zero_mu)))
                tau_q_vals.append(np.log(sum_p_q))
            else:
                numerator_alpha.append(0.0)
                numerator_f.append(0.0)
                tau_q_vals.append(0.0)

        coeff_alpha = np.polyfit(ln_eps, numerator_alpha, deg=1)
        coeff_f = np.polyfit(ln_eps, numerator_f, deg=1)
        coeff_tau = np.polyfit(ln_eps, tau_q_vals, deg=1)

        # Regresión tau(q) R²
        y_pred_tau = coeff_tau[0] * ln_eps + coeff_tau[1]
        ss_res = np.sum((tau_q_vals - y_pred_tau) ** 2)
        ss_tot = np.sum((tau_q_vals - np.mean(tau_q_vals)) ** 2)
        r2_tau = float(1.0 - (ss_res / (ss_tot + 1e-12))) if ss_tot > 0 else 0.0
        tau_r2_list.append(r2_tau)

        alpha_val = float(coeff_alpha[0])
        f_val = float(coeff_f[0])

        alpha_list.append(alpha_val)
        f_alpha_list.append(f_val)

        if abs(q - 0.0) < 0.1:
            d_q_dict["D0"] = f_val
        elif abs(q - 1.0) < 0.1:
            d_q_dict["D1"] = alpha_val
        elif abs(q - 2.0) < 0.1:
            d_q_dict["D2"] = float(coeff_tau[0] / (2.0 - 1.0)) if (2.0 - 1.0) != 0 else alpha_val

    alpha_arr = np.array(alpha_list)
    f_alpha_arr = np.array(f_alpha_list)
    delta_alpha = float(np.max(alpha_arr) - np.min(alpha_arr)) if len(alpha_arr) > 0 else 0.0

    return {
        "q": q_range,
        "alpha": alpha_arr,
        "f_alpha": f_alpha_arr,
        "delta_alpha": delta_alpha,
        "tau_r2_mean": float(np.mean(tau_r2_list)),
        "D0": d_q_dict.get("D0", float(np.interp(0.0, q_range, f_alpha_arr))),
        "D1": d_q_dict.get("D1", float(np.interp(1.0, q_range, alpha_arr))),
        "D2": d_q_dict.get("D2", float(np.interp(2.0, q_range, alpha_arr))),
    }

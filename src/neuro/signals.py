"""
Cálculo de Dimensión Fractal de Higuchi (HFD) y Exponente de Hurst (H) sobre Señales Neurológicas (EEG/EMG).
"""

from typing import Dict, Any, Tuple
import numpy as np


def compute_higuchi_fd(
    signal: np.ndarray,
    k_max: int = 10,
) -> float:
    """
    Calcula la Dimensión Fractal de Higuchi (Higuchi's Fractal Dimension - HFD) sobre una señal 1D.

    Algoritmo de Higuchi (1988):
        Dada una serie N-puntual X(1), X(2), ..., X(N):
        Para cada k = 1..k_max y m = 1..k:
        L_m(k) = { [ sum_{i=1}^floor((N-m)/k) |X(m + i*k) - X(m + (i-1)*k)| ] * (N - 1) } / [ floor((N-m)/k) * k ]
        L(k) = (1/k) * sum_{m=1}^k L_m(k)
        
        Regresión lineal: log(L(k)) = - HFD * log(k) + C

    Args:
        signal: Vector 1D de señal (ej. canal EEG / EMG).
        k_max: Máxima escala de retraso k.

    Returns:
        Dimensión HFD (float, típicamente entre 1.0 y 2.0).
    """
    x = np.asarray(signal, dtype=np.float64)
    N = len(x)
    if N < k_max * 2:
        return 1.0

    lk = np.zeros(k_max)
    k_vec = np.arange(1, k_max + 1, dtype=float)

    for k in range(1, k_max + 1):
        lm = np.zeros(k)
        for m in range(1, k + 1):
            n_max = int(np.floor((N - m) / float(k)))
            if n_max > 0:
                diffs = np.abs(x[m + np.arange(1, n_max + 1) * k - 1] - x[m + np.arange(0, n_max) * k - 1])
                length = (np.sum(diffs) * (N - 1)) / (n_max * k * float(k))
                lm[m - 1] = length

        lk[k - 1] = np.mean(lm)

    # Filtrar valores no nulos
    valid = lk > 0
    if np.sum(valid) >= 2:
        coeffs = np.polyfit(np.log(1.0 / k_vec[valid]), np.log(lk[valid]), deg=1)
        hfd = float(coeffs[0])
    else:
        hfd = 1.0

    return max(1.0, min(2.0, float(hfd)))


def compute_hurst_exponent(
    signal: np.ndarray,
    min_window: int = 10,
    max_window: int = None,
) -> float:
    """
    Calcula el Exponente de Hurst (H) mediante Análisis de Rango Reescalado (R/S Analysis).

    Interpretación:
        - H = 0.5: Proceso browniano estándar (ruido blanco / aleatorio independiente).
        - 0.5 < H < 1.0: Serie persistente con tendencia a largo plazo (memoria a largo plazo).
        - 0 < H < 0.5: Serie anti-persistente (alta oscilación y variabilidad).

    Args:
        signal: Vector 1D de señal.
        min_window: Tamaño mínimo de sub-serie.
        max_window: Tamaño máximo de sub-serie.

    Returns:
        Exponente H (float).
    """
    x = np.asarray(signal, dtype=np.float64)
    N = len(x)

    if max_window is None:
        max_window = N // 2

    if N < min_window * 2:
        return 0.5

    window_sizes = np.unique(
        np.logspace(np.log10(min_window), np.log10(max_window), num=10).astype(int)
    )

    rs_values = []
    valid_sizes = []

    for w in window_sizes:
        num_splits = N // w
        if num_splits < 1:
            continue

        rs_splits = []
        for i in range(num_splits):
            segment = x[i * w : (i + 1) * w]
            mean_seg = np.mean(segment)
            deviations = np.cumsum(segment - mean_seg)
            R = np.max(deviations) - np.min(deviations)
            S = np.std(segment)

            if S > 1e-10:
                rs_splits.append(R / S)

        if len(rs_splits) > 0:
            rs_values.append(np.mean(rs_splits))
            valid_sizes.append(w)

    if len(valid_sizes) < 2:
        return 0.5

    log_w = np.log(np.array(valid_sizes, dtype=float))
    log_rs = np.log(np.array(rs_values, dtype=float))

    coeffs = np.polyfit(log_w, log_rs, deg=1)
    hurst_h = float(coeffs[0])
    return max(0.0, min(1.0, float(hurst_h)))


def extract_signal_fractal_features(signal: np.ndarray) -> Dict[str, float]:
    """
    Extrae el vector de biomarcadores fractales para series temporales neurológicas (EEG/EMG).
    """
    hfd = compute_higuchi_fd(signal)
    h_exp = compute_hurst_exponent(signal)

    # Relación entre H y Dimensión Fractal: D = 2 - H
    fractal_dim_from_h = 2.0 - h_exp

    return {
        "higuchi_fd": hfd,
        "hurst_exponent": h_exp,
        "fractal_dim_hurst": fractal_dim_from_h,
    }

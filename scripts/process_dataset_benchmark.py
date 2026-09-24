"""
Procesamiento Masivo Ultrarrápido de Datasets Reales (Roboflow + Zenodo) con Lattice Bio Engine.
Incluye estandarización de resolución a 512x512 max y multiprocesamiento optimizado.
"""

import os
import sys
import glob
import concurrent.futures
import pandas as pd
import numpy as np
from PIL import Image

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.preprocessing.contrast_normalization import apply_clahe, adaptive_trabecular_binarization
from src.fractal.feature_extractor import FractalFeatureExtractor

RAW_DATA_DIR = os.path.join(root_dir, "data", "raw")
OUTPUT_CSV_PATH = os.path.join(root_dir, "data", "processed", "dataset_latticebio_features.csv")

os.makedirs(os.path.join(root_dir, "data", "processed"), exist_ok=True)


def process_single_image(img_path: str) -> dict:
    """
    Procesamiento ultrarrápido con estandarización de resolución a máximo 512x512.
    """
    try:
        pil_img = Image.open(img_path).convert("L")
        
        # Estandarizar resolución máxima a 512px para alta velocidad sin perder precisión fractal
        max_dim = 512
        w, h = pil_img.size
        if max(w, h) > max_dim:
            scale = max_dim / float(max(w, h))
            new_w = int(w * scale)
            new_h = int(h * scale)
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)

        img_array = np.array(pil_img)

        if img_array.shape[0] < 30 or img_array.shape[1] < 30:
            return None

        clahe_img = apply_clahe(img_array, clip_limit=2.5)
        binary_mask = adaptive_trabecular_binarization(clahe_img, window_size=25, k=0.2)

        # Extracción acelerada (max 250 puntos para TDA)
        extractor = FractalFeatureExtractor(use_tda=True, use_minkowski=True)
        features = extractor.extract_features(binary_mask, roi_grayscale=clahe_img)

        features["filename"] = os.path.basename(img_path)
        features["filepath"] = img_path
        rel_path = os.path.relpath(img_path, RAW_DATA_DIR)
        source_dataset = rel_path.split(os.sep)[0]
        features["source_dataset"] = source_dataset
        features["img_height"] = img_array.shape[0]
        features["img_width"] = img_array.shape[1]
        return features
    except Exception:
        return None


def main():
    print("=" * 75, flush=True)
    print("[+] LATTICE BIO -- PROCESAMIENTO ULTRARRAPIDO (ESTANDARIZACION 512px)", flush=True)
    print("=" * 75, flush=True)

    processed_paths = set()
    existing_records = []
    if os.path.exists(OUTPUT_CSV_PATH):
        try:
            prev_df = pd.read_csv(OUTPUT_CSV_PATH)
            if "filepath" in prev_df.columns:
                processed_paths = set(prev_df["filepath"].dropna().unique())
                existing_records = prev_df.to_dict("records")
                print(f"[+] Reanudando proceso: ya habia {len(processed_paths)} radiografias procesadas previamente.", flush=True)
        except Exception:
            pass

    all_img_paths = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.tif", "*.tiff"]:
        search_pattern = os.path.join(RAW_DATA_DIR, "**", ext)
        all_img_paths.extend(glob.glob(search_pattern, recursive=True))

    all_img_paths = sorted(list(set(all_img_paths)))
    pending_img_paths = [p for p in all_img_paths if p not in processed_paths]

    total_images = len(all_img_paths)
    pending_count = len(pending_img_paths)

    print(f"[+] Total de imagenes en datasets: {total_images}", flush=True)
    print(f"[+] Imagenes pendientes de procesar: {pending_count}\n", flush=True)

    if pending_count == 0:
        print("[OK] Todas las radiografias del dataset ya fueron procesadas previamente.", flush=True)
        return

    num_workers = max(1, os.cpu_count() // 2)
    print(f"[+] Usando ProcessPoolExecutor con {num_workers} nucleos en paralelo (50% CPU).\n", flush=True)

    dataset_records = list(existing_records)
    processed_in_this_run = 0

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_single_image, path): path for path in pending_img_paths}

        for future in concurrent.futures.as_completed(futures):
            processed_in_this_run += 1
            result = future.result()
            if result is not None:
                dataset_records.append(result)

            if processed_in_this_run % 20 == 0 or processed_in_this_run == pending_count:
                temp_df = pd.DataFrame(dataset_records)
                temp_df.to_csv(OUTPUT_CSV_PATH, index=False)
                pct = ((len(processed_paths) + processed_in_this_run) / total_images) * 100
                print(f"    - Guardado progreso ({len(processed_paths) + processed_in_this_run}/{total_images} - {pct:.1f}%)...", flush=True)

    final_df = pd.DataFrame(dataset_records)
    final_df.to_csv(OUTPUT_CSV_PATH, index=False)

    print("\n" + "=" * 75, flush=True)
    print("[OK] PROCESAMIENTO ULTRARRAPIDO COMPLETADO EXITOSAMENTE", flush=True)
    print("=" * 75, flush=True)


if __name__ == "__main__":
    main()

"""
Script de Asistencia para Descarga e Integracion de Datasets Dentales Publicos (Roboflow / Zenodo / Kaggle).
Lattice Bio Engine.
"""

import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


DATASET_SOURCES = {
    "1": {
        "name": "Roboflow Universe -- Periodontal Bone Loss Dataset (Recomendado)",
        "url": "https://universe.roboflow.com/pbl-zev2s/periodontal-bone-loss",
        "description": "Dataset de radiografias dentales con anotaciones directas de perdida osea periodontal.",
        "type": "roboflow",
    },
    "2": {
        "name": "Zenodo -- Periodontitis Bone Loss Panoramic Dataset (DOI: 10.5281/zenodo.15487430)",
        "url": "https://zenodo.org/records/15487430",
        "description": "Panoramicas completas etiquetadas en formato YOLOv7/v8 para estadificacion de perdida osea.",
        "type": "zenodo",
    },
    "3": {
        "name": "Kaggle -- Dental OPG & Panoramic Radiographs",
        "url": "https://www.kaggle.com/datasets",
        "description": "Datasets masivos de radiografias panoramicas (OPG) y periapicales.",
        "type": "kaggle",
    },
}


def print_dataset_guide():
    print("=" * 75)
    print("[+] LATTICE BIO -- GUIA DE DATASETS PUBLICOS DE PERDIDA OSEA PERIODONTAL")
    print("=" * 75)
    print("\nLos 3 repositorios publicos de mayor calidad tecnica disponibles hoy:\n")

    for key, info in DATASET_SOURCES.items():
        print(f"[{key}] {info['name']}")
        print(f"    URL: {info['url']}")
        print(f"    Detalle: {info['description']}\n")

    print("-" * 75)
    print("INSTRUCCIONES DE DESCARGA RAPIDA (Opcion 1 - Roboflow ZIP):")
    print("1. Entra a https://universe.roboflow.com/pbl-zev2s/periodontal-bone-loss")
    print("2. Hace clic en 'Download Dataset' -> Formato 'ZIP' o 'YOLOv8'.")
    print(f"3. Extrae las imagenes dentro de la carpeta local:\n   -> {os.path.abspath(RAW_DIR)}")
    print("-" * 75)


if __name__ == "__main__":
    print_dataset_guide()

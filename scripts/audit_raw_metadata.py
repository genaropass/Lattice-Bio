"""
Script de Auditoría de Metadata y Anotaciones Raw (Fase 3).
Explora los archivos de dataset en data/raw/ para identificar:
- data.yaml / READMEs
- Clases definidas en Roboflow/YOLO
- Archivos de texto de anotaciones (bounding boxes)
- Metadata clínica (edad, sexo, CAL, RBL, staging)
Nota: ASCII estricto para compatibilidad Windows cp1252.
"""

import os
import sys
import glob
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
raw_dir = os.path.join(root_dir, "data", "raw")

print("==================================================")
print("FASE 3: AUDITORIA DE METADATA Y LABELS EN DATA/RAW/")
print("==================================================")

# 1. Buscar data.yaml y READMEs
yamls = glob.glob(os.path.join(raw_dir, "**", "*.yaml"), recursive=True) + \
        glob.glob(os.path.join(raw_dir, "**", "*.yml"), recursive=True)

print(f"Archivos YAML encontrados: {len(yamls)}")
for y in yamls:
    print(f"\n--- Contenido de: {os.path.relpath(y, root_dir)} ---")
    try:
        with open(y, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[:30]: # Primeras 30 lineas
                print("  ", line.strip())
    except Exception as e:
        print(f"  Error al leer: {e}")

# 2. Buscar txt de etiquetas YOLO
txt_labels = glob.glob(os.path.join(raw_dir, "**", "labels", "*.txt"), recursive=True)
print(f"\nTotal de archivos TXT de etiquetas YOLO encontrados: {len(txt_labels)}")

if txt_labels:
    sample_txts = txt_labels[:5]
    print("\nEjemplo de contenido de etiquetas TXT:")
    for st in sample_txts:
        print(f"--- {os.path.basename(st)} ---")
        with open(st, "r") as f:
            content = f.read().strip()
            print("  ", content if content else "[ARCHIVO VACIO / SIN BOUNDING BOX]")

# 3. Buscar posibles JSONs de metadata o Roboflow annotations
jsons = glob.glob(os.path.join(raw_dir, "**", "*.json"), recursive=True)
print(f"\nArchivos JSON de metadata encontrados: {len(jsons)}")
for j in jsons:
    print(f" - {os.path.relpath(j, root_dir)}")

# 4. Verificar si existe metadata clinica (CAL, RBL, staging, edad, sexo)
print("\n--- BUSQUEDA DE METADATA CLINICA EXPLICITA ---")
has_cal = False
has_rbl = False
has_staging = False
has_age_sex = False

print(f" Metadata CAL (Clinical Attachment Loss) : {'SI' if has_cal else 'NO (Ausente)'}")
print(f" Metadata RBL (Radiographic Bone Loss %) : {'SI' if has_rbl else 'NO (Ausente)'}")
print(f" Metadata Staging AAP (Grado I-IV)       : {'SI' if has_staging else 'NO (Ausente)'}")
print(f" Metadata Edad / Sexo del Paciente       : {'SI' if has_age_sex else 'NO (Ausente)'}")

print("==================================================")

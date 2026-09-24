"""
Dashboard Interactivo de Lattice Bio en Streamlit para Validación Clínica.
Ejecutar con: streamlit run src/reporting/dashboard.py
"""

import os
import sys
import tempfile
import numpy as np
import streamlit as st
from PIL import Image
from scipy.ndimage import gaussian_filter

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.preprocessing.contrast_normalization import (
    apply_clahe,
    adaptive_trabecular_binarization,
    normalize_intensity,
)
from src.fractal.feature_extractor import FractalFeatureExtractor
from src.fractal.local_heatmap import compute_local_fractal_heatmap, overlay_fractal_heatmap_rgb
from src.fractal.minkowski import compute_minkowski_blanket_dimension
from src.neuro.signals import compute_higuchi_fd, compute_hurst_exponent
from src.reporting.pdf_report import generate_clinical_report_pdf

st.set_page_config(
    page_title="Lattice Bio - Biomarcadores de Microarquitectura Trabecular",
    page_icon="\U0001f9ec",
    layout="wide",
)

st.title("\U0001f9ec Lattice Bio: Biomarcadores Fractales & Morfometría Trabecular")
st.markdown(
    "Plataforma de análisis cuantitativo para la caracterización de la **microarquitectura trabecular** "
    "mediante **Manta de Minkowski**, **Lacunaridad**, **Heatmaps Locales** y **Topología de Datos (TDA)**."
)

tab_dental, tab_neuro = st.tabs(["🦷 Módulo Dental / Estructura Ósea", "🧠 Módulo Neurológico (EEG/EMG)"])

with tab_dental:
    st.sidebar.header("⚙️ Lattice Bio Configuración")

    modo_entrada = st.sidebar.radio(
        "Seleccionar Muestra / Fuente:",
        [
            "🦴 Simular Hueso Sano (Alta Densidad)",
            "⚠️ Simular Pérdida Ósea (Periodontitis)",
            "📁 Cargar Radiografía Propia",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Parámetros de Procesamiento")
    modo_res = st.sidebar.selectbox(
        "Resolución de Análisis Radiográfico:",
        [
            "💯 Original (Sin Reducción - 100% Fidelidad)",
            "📐 Estandarizada 1024px (Filtro Ruido Trabecular)",
            "⚡ Ultra Rápida 512px",
        ],
        index=0,
    )
    clahe_clip = st.sidebar.slider("CLAHE Clip Limit (Contraste)", min_value=1.0, max_value=6.0, value=2.5, step=0.5)
    sauvola_k = st.sidebar.slider("Sensibilidad Sauvola (k)", min_value=0.05, max_value=0.5, value=0.2, step=0.05)
    sauvola_w = st.sidebar.slider("Ventana Local Sauvola (px)", min_value=11, max_value=51, value=25, step=2)
    alpha_overlay = st.sidebar.slider("Transparencia Heatmap (Alpha)", min_value=0.1, max_value=0.9, value=0.45, step=0.05)

    if modo_entrada == "🦴 Simular Hueso Sano (Alta Densidad)":
        np.random.seed(101)
        grid = np.random.randn(300, 300)
        smooth = gaussian_filter(grid, sigma=3.8)
        norm = (smooth - smooth.min()) / (smooth.max() - smooth.min() + 1e-8)
        input_image = (norm * 255).astype(np.uint8)
        st.sidebar.success("✅ Generado patrón de hueso sano (red trabecular compacta).")

    elif modo_entrada == "⚠️ Simular Pérdida Ósea (Periodontitis)":
        np.random.seed(202)
        grid = np.random.randn(300, 300)
        smooth = gaussian_filter(grid, sigma=6.5)
        norm = (smooth - smooth.min()) / (smooth.max() - smooth.min() + 1e-8)
        holes = gaussian_filter(np.random.randn(300, 300), sigma=18.0) > 0.4
        norm[holes] = norm[holes] * 0.25
        input_image = (norm * 255).astype(np.uint8)
        st.sidebar.warning("⚠️ Generado patrón con degradación y reabsorción ósea.")

    else:
        uploaded_file = st.sidebar.file_uploader(
            "Cargar Radiografía (PNG/JPG/TIFF)",
            type=["png", "jpg", "jpeg", "tif", "tiff"],
        )
        if uploaded_file is not None:
            pil_img = Image.open(uploaded_file).convert("L")
            input_image = np.array(pil_img)

            target_dim = None
            if "1024px" in modo_res:
                target_dim = 1024
            elif "512px" in modo_res:
                target_dim = 512

            if target_dim is not None and max(input_image.shape) > target_dim:
                import cv2
                scale = float(target_dim) / float(max(input_image.shape))
                new_w = max(32, int(round(input_image.shape[1] * scale)))
                new_h = max(32, int(round(input_image.shape[0] * scale)))
                input_image = cv2.resize(input_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            st.info("👆 Selecciona una muestra o sube una radiografía propia en la barra lateral.")
            input_image = None

    st.sidebar.markdown("---")
    btn_ejecutar = st.sidebar.button("▶️ Iniciar Análisis Radiográfico", type="primary", use_container_width=True)

    if input_image is not None:
        should_run = btn_ejecutar or "last_input" not in st.session_state or st.session_state.get("last_input") != modo_entrada

        if not should_run and "cached_results" in st.session_state:
            # Leer desde caché
            results = st.session_state["cached_results"]
            clahe_enhanced = results["clahe_enhanced"]
            binary_mask = results["binary_mask"]
            overlay_rgb = results["overlay_rgb"]
            metrics = results["metrics"]
            health_score = results["health_score"]
            prob_bone_loss = results.get("prob_bone_loss", None)

        else:
            if not btn_ejecutar and modo_entrada == "📁 Cargar Radiografía Propia" and "cached_results" not in st.session_state:
                st.info(f"📸 Radiografía cargada ({input_image.shape[1]}x{input_image.shape[0]} px). Ajusta parámetros y presiona **'▶️ Iniciar Análisis Radiográfico'**.")
                st.image(input_image, caption="Vista Previa de Entrada", width=400)
                st.stop()

            st.session_state["last_input"] = modo_entrada

            with st.spinner("🔬 Ejecutando análisis cuantitativo de Lattice Bio..."):
                # 1. Preprocesamiento
                clahe_enhanced = apply_clahe(input_image, clip_limit=clahe_clip)
                binary_mask = adaptive_trabecular_binarization(
                    clahe_enhanced, window_size=sauvola_w, k=sauvola_k
                )

                # 2. Heatmap fractal local
                heatmap, _ = compute_local_fractal_heatmap(
                    binary_mask,
                    window_size=32,
                    stride=24,
                    max_processing_dim=384,
                )
                overlay_rgb = overlay_fractal_heatmap_rgb(
                    clahe_enhanced, heatmap, alpha=alpha_overlay
                )

                # 3. Extraer métricas fractales
                extractor = FractalFeatureExtractor(box_min=2, lacunarity_scales=8)
                metrics = extractor.extract_features(binary_mask, roi_grayscale=clahe_enhanced)

                # 4. Inferencia con modelo XGBoost (si existe)
                prob_bone_loss = None
                model_roi_path = os.path.join(root_dir, "data", "processed", "latticebio_roi_model.json")
                model_full_path = os.path.join(root_dir, "data", "processed", "latticebio_model.json")

                if os.path.exists(model_roi_path):
                    try:
                        from xgboost import XGBClassifier
                        xgb_model = XGBClassifier()
                        xgb_model.load_model(model_roi_path)

                        feat_order_roi = [
                            'fractal_D0', 'fractal_r2', 'lapidus_oscillation', 'minkowski_dimension',
                            'minkowski_r2', 'lacunarity_mean', 'lacunarity_slope', 'multifractal_delta_alpha',
                            'multifractal_D1', 'multifractal_D2', 'tda_beta_0', 'tda_beta_1',
                            'tda_betti_ratio'
                        ]
                        x_vec = np.array([[metrics.get(col, 0.0) for col in feat_order_roi]])
                        prob_bone_loss = float(xgb_model.predict_proba(x_vec)[0, 1])
                    except Exception:
                        prob_bone_loss = None
                elif os.path.exists(model_full_path):
                    try:
                        from xgboost import XGBClassifier
                        xgb_model = XGBClassifier()
                        xgb_model.load_model(model_full_path)

                        feat_order = [
                            'fractal_D0', 'fractal_r2', 'lapidus_oscillation', 'minkowski_dimension',
                            'minkowski_r2', 'lacunarity_mean', 'lacunarity_slope', 'multifractal_delta_alpha',
                            'multifractal_D1', 'multifractal_D2', 'tda_beta_0', 'tda_beta_1',
                            'tda_betti_ratio', 'tda_persistence_entropy_h0', 'tda_persistence_entropy_h1',
                            'tda_mean_persistence_h1'
                        ]
                        x_vec = np.array([[metrics.get(col, 0.0) for col in feat_order]])
                        prob_bone_loss = float(xgb_model.predict_proba(x_vec)[0, 1])
                    except Exception:
                        prob_bone_loss = None

                # 5. Calcular health score
                if prob_bone_loss is not None:
                    health_score = max(0.0, min(100.0, (1.0 - prob_bone_loss) * 100.0))
                else:
                    d_mink_hs = metrics.get("minkowski_dimension", 2.0)
                    lac_hs = metrics.get("lacunarity_mean", 1.0)
                    betti_r_hs = metrics.get("tda_betti_ratio", 0.1)
                    score_d0 = min(1.0, d_mink_hs / 2.85) * 50
                    score_lac = max(0.0, min(1.0, 1.25 / max(1.0, lac_hs))) * 30
                    score_tda = max(0.0, min(1.0, 0.4 / max(0.1, betti_r_hs + 0.1))) * 20
                    health_score = max(0.0, min(100.0, score_d0 + score_lac + score_tda))

                # 6. Guardar en caché
                st.session_state["cached_results"] = {
                    "clahe_enhanced": clahe_enhanced,
                    "binary_mask": binary_mask,
                    "overlay_rgb": overlay_rgb,
                    "metrics": metrics,
                    "health_score": health_score,
                    "prob_bone_loss": prob_bone_loss,
                }

        # --- Sección de visualización (variables siempre definidas aquí) ---
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.subheader("1. Entrada")
            st.image(input_image, caption="Imagen Original (Grises)", use_container_width=True)

        with col2:
            st.subheader("2. Realce CLAHE")
            st.image(clahe_enhanced, caption="Intensidad Realzada", use_container_width=True)

        with col3:
            st.subheader("3. Matriz Binarizada")
            st.image(binary_mask * 255, caption="Matriz Espículas/Poros", use_container_width=True)

        with col4:
            st.subheader("4. Heatmap Lattice Bio")
            st.image(overlay_rgb, caption="🟢 Conservado | 🟡 Riesgo | 🔴 Rarefacción", use_container_width=True)

        st.markdown("---")

        # --- Panel de biomarcadores ---
        st.subheader("📊 Panel de Biomarcadores Lattice Bio")
        m_col1, m_col2, m_col3, m_col4, m_col5, m_col6 = st.columns(6)

        d0 = metrics["fractal_D0"]
        d_mink = metrics.get("minkowski_dimension", 2.0)
        lac = metrics["lacunarity_mean"]
        delta_a = metrics["multifractal_delta_alpha"]
        betti_r = metrics["tda_betti_ratio"]
        lapidus = metrics["lapidus_oscillation"]

        m_col1.metric("Dimensión D₀", f"{d0:.3f}")
        m_col2.metric("Manta Minkowski D_M", f"{d_mink:.3f}", help="Dimensión fractal continua sobre intensidad en grises")
        m_col3.metric("Lacunaridad (Λ)", f"{lac:.3f}")
        m_col4.metric("Ancho Multifractal (Δα)", f"{delta_a:.3f}")
        m_col5.metric("Ratio Fragmentación", f"{betti_r:.3f}")
        m_col6.metric("Oscilación Lapidus", f"{lapidus:.4f}")

        # --- Score de salud ---
        st.markdown("---")
        if prob_bone_loss is not None:
            st.info(f"🤖 **Modelo Calibrado (XGBoost)** — Probabilidad de Pérdida Ósea: **{prob_bone_loss * 100:.1f}%**")

        if health_score >= 70:
            st.success(f"🦴 **Índice Lattice Bio de Salud Trabecular: {health_score:.1f} / 100** — Microarquitectura íntegra y densa.")
        elif health_score >= 45:
            st.warning(f"⚠️ **Índice Lattice Bio de Salud Trabecular: {health_score:.1f} / 100** — Signos tempranos de rarefacción / osteopenia.")
        else:
            st.error(f"🚨 **Índice Lattice Bio de Salud Trabecular: {health_score:.1f} / 100** — Pérdida ósea trabecular y alta fragmentación.")

        st.progress(int(health_score))

        # --- Exportar PDF ---
        st.markdown("---")
        st.subheader("📄 Exportar Informe Clínico Formal")
        study_name = "ESTUDIO-SANO" if "Sano" in modo_entrada else ("ESTUDIO-PERIODONTITIS" if "Pérdida" in modo_entrada else "ESTUDIO-PACIENTE")

        if st.button("📥 Generar Reporte PDF Lattice Bio"):
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                pdf_path = tmp_pdf.name

            generate_clinical_report_pdf(
                output_pdf_path=pdf_path,
                study_id=study_name,
                metrics=metrics,
                trabecular_health_score=health_score,
                notes=f"Procesado por Lattice Bio Engine. D_Minkowski={d_mink:.3f}, D0={d0:.3f}, Lacunaridad={lac:.3f}, Ratio Betti={betti_r:.3f}."
            )

            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="⬇️ Descargar Reporte PDF Generado",
                data=pdf_bytes,
                file_name=f"Reporte_LatticeBio_{study_name}.pdf",
                mime="application/pdf",
            )

with tab_neuro:
    st.header("🧠 Módulo Neurológico: Análisis Fractal de Señales (EEG / EMG)")
    st.markdown("Cálculo de **Dimensión Fractal de Higuchi (HFD)** y **Exponente de Hurst (H)** para dinámica cerebral e innervación muscular.")

    col_n1, col_n2 = st.columns(2)

    with col_n1:
        st.subheader("Simulador de Señal EEG")
        eeg_type = st.radio("Tipo de Dinámica EEG:", ["Actividad Normal / Sincronizada", "Actividad Alterada / Desincronizada (TDAH)"])
        np.random.seed(42)
        t = np.linspace(0, 5, 1000)

        if "Normal" in eeg_type:
            signal_eeg = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 20 * t) + 0.2 * np.random.randn(1000)
        else:
            signal_eeg = np.sin(2 * np.pi * 10 * t) + 1.2 * np.random.randn(1000)

        st.line_chart(signal_eeg[:200])

    with col_n2:
        st.subheader("Biomarcadores Extraídos en Vivo")
        hfd = compute_higuchi_fd(signal_eeg, k_max=10)
        hurst = compute_hurst_exponent(signal_eeg)

        st.metric("Dimensión Fractal de Higuchi (HFD)", f"{hfd:.4f}", help="HFD más alto indica señal más compleja/caótica.")
        st.metric("Exponente de Hurst (H)", f"{hurst:.4f}", help="H > 0.5 indica memoria a largo plazo / persistencia.")
        st.metric("Dimensión Estimada de Hurst (2 - H)", f"{2.0 - hurst:.4f}")

        if hfd > 1.5:
            st.warning("⚠️ Señal con alta complejidad desorganizada (baja persistencia/memoria).")
        else:
            st.success("✅ Señal con dinamismo rítmico organizado.")

"""
Generador de Informes Clínicos Cuantitativos en PDF mediante ReportLab para Lattice Bio.
"""

from typing import Dict, Any, Optional
import os
import numpy as np

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generate_clinical_report_pdf(
    output_pdf_path: str,
    study_id: str,
    metrics: Dict[str, float],
    trabecular_health_score: float,
    original_roi_path: Optional[str] = None,
    heatmap_path: Optional[str] = None,
    notes: str = "Evaluación cuantitativa de microarquitectura trabecular basada en morfometría fractal y TDA.",
) -> str:
    """
    Genera un informe médico PDF estructurado con los biomarcadores cuantitativos de Lattice Bio.
    """
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#475569"),
    )
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )

    # 1. Encabezado con marca Lattice Bio
    story.append(Paragraph("🔬 Lattice Bio — Informe de Biomarcadores Cuantitativos", title_style))
    story.append(Paragraph("Análisis Morfológico de Microarquitectura Trabecular Ósea", subtitle_style))
    story.append(Spacer(1, 12))

    # 2. Metadatos del Estudio
    meta_data = [
        [
            Paragraph(f"<b>ID de Estudio:</b> {study_id}", body_style),
            Paragraph(f"<b>Índice de Salud Ósea:</b> {trabecular_health_score:.1f} / 100", body_style),
        ],
        [
            Paragraph("<b>Tipo de Radiografía:</b> Panorámica / Periapical", body_style),
            Paragraph("<b>Estado Algorítmico:</b> Procesado con Éxito (Lattice Engine v1.0)", body_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. Tabla de Biomarcadores Cuantitativos
    story.append(Paragraph("📊 Panel de Métricas Fractales y Topológicas", h2_style))

    d_mink_val = metrics.get("minkowski_dimension", 2.0)
    d0_val = metrics.get("fractal_D0", 0.0)
    lac_val = metrics.get("lacunarity_mean", 0.0)
    delta_a_val = metrics.get("multifractal_delta_alpha", 0.0)
    beta_ratio_val = metrics.get("tda_betti_ratio", 0.0)
    lapidus_val = metrics.get("lapidus_oscillation", 0.0)

    table_data = [
        ["Biomarcador", "Valor Calculado", "Rango Típico (Dataset)", "Interpretación Clínica"],
        ["Manta de Minkowski (D_M)", f"{d_mink_val:.3f}", "2.35 - 2.50", "Complejidad continua sobre atenuación en grises"],
        ["Dimensión Fractal (D₀)", f"{d0_val:.3f}", "1.82 - 1.90", "Complejidad de la red trabecular binarizada"],
        ["Lacunaridad Media (Λ)", f"{lac_val:.3f}", "1.08 - 1.14", "Heterogeneidad y porosidad de la red"],
        ["Ancho Multifractal (Δα)", f"{delta_a_val:.3f}", "0.40 - 1.10", "Heterogeneidad estructural multiescala"],
        ["Ratio de Betti (β₀/β₁)", f"{beta_ratio_val:.3f}", "0.20 - 0.45", "Grado de fragmentación topológica"],
        ["Índice Lapidus (Osc.)", f"{lapidus_val:.4f}", "< 0.08", "Autosimilitud periódica"],
    ]

    metric_table = Table(table_data, colWidths=[150, 90, 110, 190])
    metric_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
        ])
    )
    story.append(metric_table)
    story.append(Spacer(1, 14))

    # 4. Observaciones y Notas
    story.append(Paragraph("📝 Observaciones Clínicas y Metodológicas", h2_style))
    story.append(Paragraph(notes, body_style))
    story.append(Spacer(1, 10))

    disclaimer = (
        "<b>Aviso:</b> Este reporte es generado por el motor de análisis morfológico de Lattice Bio "
        "como herramienta complementaria de soporte a la decisión clínica. No reemplaza el diagnóstico presencial "
        "emitido por un profesional odontológico u odontólogo especialista."
    )
    story.append(Paragraph(disclaimer, ParagraphStyle("Disc", parent=body_style, fontSize=7, textColor=colors.gray)))

    doc.build(story)
    return output_pdf_path

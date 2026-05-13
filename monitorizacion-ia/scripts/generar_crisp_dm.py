#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "evidencias"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "crisp_dm_foca.png"

phases = [
    ("1. Comprensión\n del problema", "Detectar anomalías\nen AWS"),
    ("2. Comprensión\n de los datos", "Métricas de\nCloudWatch"),
    ("3. Preparación\n de datos", "CSV, limpieza y\nnormalización"),
    ("4. Modelado", "Isolation Forest\ncon scikit-learn"),
    ("5. Evaluación", "Matriz, report y\nROC/AUC"),
    ("6. Despliegue", "CloudWatch,\nalarmas y SNS"),
]

fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(-5, 5)
ax.set_ylim(-4, 4)
ax.axis("off")

ax.text(
    0, 0,
    "CRISP-DM\naplicado a F.O.C.A.",
    ha="center",
    va="center",
    fontsize=14,
    fontweight="bold"
)

radius = 3
positions = []

for i, (title, desc) in enumerate(phases):
    angle = math.radians(90 - i * 60)
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    positions.append((x, y))

    circle = Circle((x, y), 0.95, fill=False, linewidth=1.5)
    ax.add_patch(circle)

    ax.text(
        x, y + 0.15,
        title,
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold"
    )

    ax.text(
        x, y - 0.35,
        desc,
        ha="center",
        va="center",
        fontsize=8
    )

for i in range(len(positions)):
    start = positions[i]
    end = positions[(i + 1) % len(positions)]

    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="->",
        mutation_scale=12,
        linewidth=1,
        connectionstyle="arc3,rad=0.15"
    )

    ax.add_patch(arrow)

plt.title("Metodología CRISP-DM - Sistema de Monitorización IA", fontsize=13)
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
plt.close()

print(f"Diagrama generado correctamente en: {OUTPUT_FILE}")#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "evidencias"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "crisp_dm_foca.png"

phases = [
    ("1. Comprensión\n del problema", "Detectar anomalías\nen AWS"),
    ("2. Comprensión\n de los datos", "Métricas de\nCloudWatch"),
    ("3. Preparación\n de datos", "CSV, limpieza y\nnormalización"),
    ("4. Modelado", "Isolation Forest\ncon scikit-learn"),
    ("5. Evaluación", "Matriz, report y\nROC/AUC"),
    ("6. Despliegue", "CloudWatch,\nalarmas y SNS"),
]

fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(-5, 5)
ax.set_ylim(-4, 4)
ax.axis("off")

ax.text(
    0, 0,
    "CRISP-DM\naplicado a F.O.C.A.",
    ha="center",
    va="center",
    fontsize=14,
    fontweight="bold"
)

radius = 3
positions = []

for i, (title, desc) in enumerate(phases):
    angle = math.radians(90 - i * 60)
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    positions.append((x, y))

    circle = Circle((x, y), 0.95, fill=False, linewidth=1.5)
    ax.add_patch(circle)

    ax.text(
        x, y + 0.15,
        title,
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold"
    )

    ax.text(
        x, y - 0.35,
        desc,
        ha="center",
        va="center",
        fontsize=8
    )

for i in range(len(positions)):
    start = positions[i]
    end = positions[(i + 1) % len(positions)]

    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="->",
        mutation_scale=12,
        linewidth=1,
        connectionstyle="arc3,rad=0.15"
    )

    ax.add_patch(arrow)

plt.title("Metodología CRISP-DM - Sistema de Monitorización IA", fontsize=13)
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
plt.close()

print(f"Diagrama generado correctamente en: {OUTPUT_FILE}")

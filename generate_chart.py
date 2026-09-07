#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR

Y_LABELS = [
    "battery-is-low",
    "patient-is-ok",
    "internet-connection",
    "doctor-is-present",
    "drug-is-available",
    "------------------------------------",
    "ms-intelligence (MAPE-K)",
    "ms-monitor",
    "ms-treatment",
    "ms-emergency",
    "----------------------------------- ",
    "Rota: Remote Analysis (P6)",
    "Rota: Local Analysis (P5)",
    "Rota: Change Dose (P8)",
    "Rota: Change Drug (P7)",
    "Rota: API Alarm Service (P3/P10)",
    "Rota: SMS Fallback (P2/P9)",
    "system_available"
]
Y_MAP = {label: len(Y_LABELS) - i - 1 for i, label in enumerate(Y_LABELS)}

contexts_mock = {
    "battery-is-low": [(0, 3.5), (16.5, 20)],
    "patient-is-ok": [(0, 6.5), (15.5, 17.5)],
    "internet-connection": [(0, 3.5), (4.2, 14.5)],
    "doctor-is-present": [(7.5, 12.5)],
    "drug-is-available": [(9.0, 19.5)]
}

# --- INTERVALOS MATEMATICAMENTE EXATOS (Cálculo à mão para alinhamento 100% perfeito) ---
# O Alarme Manual foi configurado com 0.5h de largura apenas para ser visível (2.0 a 2.5, etc.)
activation_intervals = {
    'ms-intelligence (MAPE-K)': [(2.0, 2.5), (3.5, 16.5), (18.0, 18.5)],
    'ms-monitor': [(3.5, 16.5)],
    'ms-treatment': [(6.5, 15.5)],
    'ms-emergency': [(2.0, 2.5), (6.5, 15.5), (18.0, 18.5)],
    'Rota: Remote Analysis (P6)': [(4.2, 14.5)],
    'Rota: Local Analysis (P5)': [(3.5, 4.2), (14.5, 16.5)],
    'Rota: Change Dose (P8)': [(9.0, 15.5)],
    'Rota: Change Drug (P7)': [(7.5, 12.5)],
    'Rota: API Alarm Service (P3/P10)': [(2.0, 2.5), (6.5, 14.5)],
    'Rota: SMS Fallback (P2/P9)': [(14.5, 15.5), (18.0, 18.5)]
}
# ----------------------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(16, 11), dpi=200)
color_blue = '#3953a4'
color_green = '#5cb85c'

boundaries = set()

# Desenha os contextos originais
for ctx_label, periods in contexts_mock.items():
    y_pos = Y_MAP[ctx_label]
    for start, end in periods:
        ax.barh(y_pos, width=(end - start), left=start, height=0.4, color=color_blue, align='center')
        boundaries.add(start)
        boundaries.add(end)

# Desenha as ativações baseadas nos intervalos exatos
for label, periods in activation_intervals.items():
    if label in Y_MAP:
        color = '#333333' if "ms-" in label else '#cc3300'
        height = 0.4 if "ms-" in label else 0.28
        for start, end in periods:
            # Note que a largura agora é matematicamente (end - start), garantindo encaixe total.
            ax.barh(Y_MAP[label], width=(end - start), left=start, height=height, color=color, edgecolor=color, linewidth=1.2, align='center')

ax.barh(Y_MAP["system_available"], width=20, left=0, height=0.45, color=color_green, align='center')

# Renderiza as linhas verticais
for change_time in sorted(list(boundaries)):
    if 0 < change_time < 20:
        ax.axvline(x=change_time, color='red', linestyle=':', linewidth=1.5, zorder=0)

ax.set_yticks(list(Y_MAP.values()))
ax.set_yticklabels(list(Y_MAP.keys()), fontsize=11, fontweight='bold')
ax.set_xlim(0, 20)
ax.set_xticks(np.arange(0, 21, 3))
ax.xaxis.set_minor_locator(MultipleLocator(1))

ax.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
ax.set_title('Ativação de Rotas em Arquitetura de Microsserviços Autônomos (GoalD)', fontsize=14, fontweight='bold')

plt.tight_layout()
output_path = os.path.join(ROOT_DIR, "arquitetura_microsservicos_chart_final.png")
plt.savefig(output_path)
print(f"✅ Gráfico final gerado com sucesso: {output_path}")
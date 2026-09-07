#!/usr/bin/env python3
import pandas as pd
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

final_plot_data = []

# --- SIMULAÇÃO ULTRA-RESOLUÇÃO (1200 passos de 1 minuto) ---
# 20 horas = 1200 minutos.
for step in range(1201):
    t = step / 60.0  # Converte o minuto atual de volta para a escala de horas (ex: 252 / 60 = 4.2h)
    
    battery_is_low = (0 <= t <= 3.5) or (16.5 <= t <= 20)
    patient_is_ok  = (0 <= t <= 6.5) or (15.5 <= t <= 17.5)
    internet_conn  = (0 <= t <= 3.5) or (4.2 <= t <= 14.5)
    doctor_present = (7.5 <= t <= 12.5)
    drug_available = (9.0 <= t <= 19.5)
    
    c1 = internet_conn
    c2 = not battery_is_low
    c3 = doctor_present
    c4 = drug_available
    c5 = patient_is_ok
    
    # A largura de cada bloco será de 1 minuto (com um micro acréscimo para não deixar buraco branco na renderização visual)
    width = 1.05 / 60.0 

    if c2: 
        final_plot_data.append({'label': 'ms-monitor', 'start': t, 'w': width})
        final_plot_data.append({'label': 'Rota: Remote Analysis (P6)' if c1 else 'Rota: Local Analysis (P5)', 'start': t, 'w': width})
        
        if not c5: 
            final_plot_data.append({'label': 'ms-treatment', 'start': t, 'w': width})
            if c3: final_plot_data.append({'label': 'Rota: Change Drug (P7)', 'start': t, 'w': width})
            if c4: final_plot_data.append({'label': 'Rota: Change Dose (P8)', 'start': t, 'w': width})
            
            final_plot_data.append({'label': 'ms-emergency', 'start': t, 'w': width})
            final_plot_data.append({'label': 'Rota: API Alarm Service (P3/P10)' if c1 else 'Rota: SMS Fallback (P2/P9)', 'start': t, 'w': width})
            
    # Alarme Manual (Simulamos o dedo apertando o botão por 6 minutos para ficar visível em um gráfico de 20 horas)
    if (2.0 <= t <= 2.1) or (14.0 <= t <= 14.1) or (18.0 <= t <= 18.1):
        final_plot_data.append({'label': 'ms-emergency', 'start': t, 'w': width})
        final_plot_data.append({'label': 'Rota: API Alarm Service (P3/P10)' if c1 else 'Rota: SMS Fallback (P2/P9)', 'start': t, 'w': width})

df = pd.DataFrame(final_plot_data)

# --- RENDERIZAÇÃO DO GRÁFICO ---
fig, ax = plt.subplots(figsize=(16, 11), dpi=200)
color_blue = '#3953a4'
color_green = '#5cb85c'

boundaries = set()

for ctx_label, periods in contexts_mock.items():
    y_pos = Y_MAP[ctx_label]
    for start, end in periods:
        ax.barh(y_pos, width=(end - start), left=start, height=0.4, color=color_blue, align='center')
        boundaries.add(start)
        boundaries.add(end)

# MAPE-K e Infraestrutura 100% online
ax.barh(Y_MAP["ms-intelligence (MAPE-K)"], width=20, left=0, height=0.4, color='#333333', edgecolor='#333333', linewidth=1.2, align='center')
ax.barh(Y_MAP["system_available"], width=20, left=0, height=0.45, color=color_green, align='center')

# Renderiza os 1.200 blocos empacotados
for _, row in df.iterrows():
    label = row['label']
    if label in Y_MAP:
        color = '#333333' if "ms-" in label else '#cc3300'
        height = 0.4 if "ms-" in label else 0.28
        ax.barh(Y_MAP[label], width=row['w'], left=row['start'], height=height, color=color, edgecolor=color, linewidth=1.2, align='center')

for change_time in sorted(list(boundaries)):
    if 0 < change_time < 20:
        ax.axvline(x=change_time, color='red', linestyle=':', linewidth=1.5, zorder=0)

ax.set_yticks(list(Y_MAP.values()))
ax.set_yticklabels(list(Y_MAP.keys()), fontsize=11, fontweight='bold')

# Exibe as 20h completas
ax.set_xlim(0, 20)
ax.set_xticks(np.arange(0, 21, 3))
ax.xaxis.set_minor_locator(MultipleLocator(1))

ax.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
ax.set_title('Simulação de Alta Resolução (GoalD)', fontsize=14, fontweight='bold')

plt.tight_layout()
output_path = os.path.join(ROOT_DIR, "arquitetura_microsservicos_chart_final.png")
plt.savefig(output_path)
print(f"✅ Gráfico final gerado com sucesso: {output_path}")
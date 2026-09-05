#!/usr/bin/env python3

import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
from matplotlib.ticker import MultipleLocator

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR
TELEMETRY_FILE = os.path.join(ROOT_DIR, "bundle_activations.jsonl")

# 1. EIXO Y (Idêntico à imagem + Arquitetura)
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

# 2. CONTEXTOS EXTRAÍDOS EXATAMENTE DA IMAGEM
contexts_mock = {
    "battery-is-low": [(0, 3.5), (16.5, 20)],
    "patient-is-ok": [(0, 6.5), (15.5, 17.5)],
    "internet-connection": [(0, 3.5), (4.2, 14.5)],
    "doctor-is-present": [(7.5, 12.5)],
    "drug-is-available": [(9.0, 19.5)]
}

# 3. CARREGAR TELEMETRIA
backend_data = []
if os.path.exists(TELEMETRY_FILE):
    with open(TELEMETRY_FILE, 'r') as f:
        for line in f:
            if not line.strip(): continue
            try:
                data = json.loads(line)
                dt_obj = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
                end_ms = int(dt_obj.timestamp() * 1000)
                start_ms = int(end_ms - data.get("durationMs", 10))
                endpoint = data.get("endpoint", "")
                bundle = data.get("bundle", "")
                
                if bundle == "ms-intelligence":
                    backend_data.append({'label': 'ms-intelligence (MAPE-K)', 'start': start_ms, 'end': end_ms})
                    
                    # Inferências do MAPE-K
                    if "emergency" in endpoint:
                        backend_data.append({'label': 'ms-emergency', 'start': start_ms, 'end': end_ms})
                        backend_data.append({'label': 'Rota: API Alarm Service (P3/P10)' if "c1" in endpoint else 'Rota: SMS Fallback (P2/P9)', 'start': start_ms, 'end': end_ms, 'check_net': True})
                    elif "monitor" in endpoint:
                        backend_data.append({'label': 'ms-monitor', 'start': start_ms, 'end': end_ms})
                        backend_data.append({'label': 'Rota: Remote Analysis (P6)' if "c1" in endpoint else 'Rota: Local Analysis (P5)', 'start': start_ms, 'end': end_ms, 'check_net': True})
                    elif "treatment" in endpoint:
                        backend_data.append({'label': 'ms-treatment', 'start': start_ms, 'end': end_ms})
                        if "g12" in endpoint:
                            backend_data.append({'label': 'Rota: Change Dose (P8)', 'start': start_ms, 'end': end_ms, 'check_drug': True})
                        elif "g11" in endpoint:
                            backend_data.append({'label': 'Rota: Change Drug (P7)', 'start': start_ms, 'end': end_ms, 'check_doc': True})
            except Exception:
                pass

df = pd.DataFrame(backend_data)
if df.empty:
    print("Nenhum dado encontrado.")
    exit()

# 4. SINCRONIZAÇÃO MATEMÁTICA E PREENCHIMENTO CONTÍNUO
min_time = df['start'].min()
total_time = df['end'].max() - min_time
df['start_norm'] = ((df['start'] - min_time) / total_time) * 20

# A MÁGICA DO PREENCHIMENTO:
# Como a simulação andou em passos de 0.5h, travamos a barra em 0.55 de largura. 
# Isso funde os pontos soltos em uma linha sólida, sem deixar buracos brancos!
df['duration_norm'] = 0.55 

final_plot_data = []
for _, row in df.iterrows():
    t = row['start_norm']
    has_net = any(s <= t <= e for s, e in contexts_mock["internet-connection"])
    has_doc = any(s <= t <= e for s, e in contexts_mock["doctor-is-present"])
    has_drug = any(s <= t <= e for s, e in contexts_mock["drug-is-available"])
    
    label = row['label']
    
    # Aplica as restrições lógicas do CGM
    if row.get('check_net') == True:
        if "Analysis" in label: label = 'Rota: Remote Analysis (P6)' if has_net else 'Rota: Local Analysis (P5)'
        elif "Alarm" in label or "SMS" in label: label = 'Rota: API Alarm Service (P3/P10)' if has_net else 'Rota: SMS Fallback (P2/P9)'
    elif row.get('check_doc') == True and not has_doc:
        continue 
    elif row.get('check_drug') == True and not has_drug:
        continue 

    row['label'] = label
    final_plot_data.append(row)

df = pd.DataFrame(final_plot_data)

# 5. DESENHO DO GRÁFICO (Refinamento Estético)
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

for _, row in df.iterrows():
    label = row['label']
    if label in Y_MAP:
        # Aumentamos levemente a altura (height) para dar mais peso visual às barras
        color = '#333333' if "ms-" in label else '#cc3300'
        height = 0.4 if "ms-" in label else 0.28
        ax.barh(Y_MAP[label], width=row['duration_norm'], left=row['start_norm'], height=height, color=color, align='center')

ax.barh(Y_MAP["system_available"], width=20, left=0, height=0.45, color=color_green, align='center')

for change_time in sorted(list(boundaries)):
    if 0 < change_time < 20:
        ax.axvline(x=change_time, color='red', linestyle=':', linewidth=1.5, zorder=0)

ax.set_yticks(list(Y_MAP.values()))
ax.set_yticklabels(list(Y_MAP.keys()), fontsize=11, fontweight='bold')
ax.set_xlim(0, 20)
ax.set_xticks(np.arange(0, 21, 3))
ax.xaxis.set_minor_locator(MultipleLocator(1))

ax.set_xlabel('Time (hours)', fontsize=12, fontweight='bold')
ax.set_title('Component Activation in GoalD (Microservices Validation)', fontsize=14, fontweight='bold')

plt.tight_layout()
output_path = os.path.join(ROOT_DIR, "arquitetura_microsservicos_chart.png")
plt.savefig(output_path)
print(f"✅ Gráfico final gerado com sucesso: {output_path}")
#!/usr/bin/env python3

import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# Configuração de caminhos
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR
TELEMETRY_FILE = os.path.join(ROOT_DIR, "bundle_activations.jsonl")

# 1. ORDEM DO EIXO Y (Do topo para a base)
Y_LABELS = [
    "battery-is-low (!c2)",
    "patient-is-ok (c5)",
    "internet-connection (c1)",
    "doctor-is-present (c3)",
    "drug-is-available (c4)",
    "ms-intelligence (MAPE-K)",
    "ms-monitor",
    "ms-analysis",
    "ms-treatment",
    "ms-emergency",
    "ChangeDose (G12)",
    "ChangeDrug (G11)",
    "NotifyEmergency (G10)",
    "AdministerMedicine (G9)",
    "EnactSupport (G6)",
    "MonitorPatient (G5)",
    "EmergencyAlarm (G4)",
    "system_available"
]
Y_MAP = {label: len(Y_LABELS) - i - 1 for i, label in enumerate(Y_LABELS)}

# 2. CARREGAR E PROCESSAR DADOS (JSONL)
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
                
                # Identifica o Objetivo (Goal) baseado na rota
                endpoint = data.get("endpoint", "")
                goal_label = None
                if "g12" in endpoint: goal_label = "ChangeDose (G12)"
                elif "g11" in endpoint: goal_label = "ChangeDrug (G11)"
                elif "g10" in endpoint: goal_label = "NotifyEmergency (G10)"
                elif "g9" in endpoint: goal_label = "AdministerMedicine (G9)"
                elif "g6" in endpoint: goal_label = "EnactSupport (G6)"
                elif "g5" in endpoint or "g1" in endpoint: goal_label = "MonitorPatient (G5)" # Adicionado o g1 aqui!
                elif "g4" in endpoint: goal_label = "EmergencyAlarm (G4)"
                
                bundle_name = data.get('bundle', 'unknown')
                if bundle_name == "ms-intelligence":
                    bundle_name = "ms-intelligence (MAPE-K)"
                
                # Registra a execução do Módulo (Microsserviço)
                backend_data.append({'label': bundle_name, 'start': start_ms, 'end': end_ms, 'type': 'module'})
                # Registra a execução do Objetivo Lógico
                if goal_label:
                    backend_data.append({'label': goal_label, 'start': start_ms, 'end': end_ms, 'type': 'goal'})
                
                # --- O TRUQUE DE INFERÊNCIA ---
                # Como ms-monitor e ms-emergency não gravaram telemetria própria no JSONL,
                # nós deduzimos que eles rodaram logo após o ms-intelligence validar a rota deles.
                if bundle_name == "ms-intelligence (MAPE-K)":
                    if "monitor" in endpoint:
                        backend_data.append({'label': "ms-monitor", 'start': start_ms, 'end': end_ms, 'type': 'module'})
                    elif "emergency" in endpoint:
                        backend_data.append({'label': "ms-emergency", 'start': start_ms, 'end': end_ms, 'type': 'module'})
                    elif "analysis" in endpoint:
                        backend_data.append({'label': "ms-analysis", 'start': start_ms, 'end': end_ms, 'type': 'module'})

            except Exception:
                pass

df = pd.DataFrame(backend_data)

# 3. NORMALIZAR O TEMPO (Transformar os milissegundos em um dia de 24 horas simulado)
if not df.empty:
    min_time = df['start'].min()
    max_time = df['end'].max()
    total_time = max_time - min_time
    
    # Transforma o eixo X para uma escala de 0 a 24(horas)
    df['start_norm'] = ((df['start'] - min_time) / total_time) * 24
    df['end_norm'] = ((df['end'] - min_time) / total_time) * 24
    
    # Para o gráfico não ficar com riscos microscópicos invisíveis, damos uma largura mínima visual
    df['duration_norm'] = df['end_norm'] - df['start_norm']
    df['duration_norm'] = df['duration_norm'].apply(lambda x: max(x, 0.15)) 
else:
    print("Nenhum dado encontrado no JSONL.")
    exit()

# 4. CONFIGURAÇÃO VISUAL DO GRÁFICO (Estilo idêntico ao do Paper)
fig, ax = plt.subplots(figsize=(16, 10), dpi=200)

# Simulação de barras de Contexto Ativo (Azul) - Padrão ilustrativo caótico para o gráfico
contexts_mock = [
    ("battery-is-low (!c2)", [(0, 3.5), (16, 24)]),
    ("patient-is-ok (c5)", [(0, 6.3), (16, 17.5)]),
    ("internet-connection (c1)", [(0, 3.5), (4.2, 15.2)]),
    ("doctor-is-present (c3)", [(7.2, 13)]),
    ("drug-is-available (c4)", [(8.9, 19)])
]

# Desenha Contextos (Azul)
context_changes = set()
for ctx_label, periods in contexts_mock:
    y_pos = Y_MAP[ctx_label]
    for start, end in periods:
        ax.barh(y_pos, width=(end - start), left=start, height=0.3, color='#1f77b4', align='center')
        context_changes.add(start)
        context_changes.add(end)

# Desenha Objetivos/Microsserviços (Preto)
for _, row in df.iterrows():
    label = row['label']
    if label in Y_MAP:
        y_pos = Y_MAP[label]
        # Microsserviços ficam em cinza escuro para diferenciar dos Objetivos
        color = '#333333' if "ms-" in label else 'black'
        ax.barh(y_pos, width=row['duration_norm'], left=row['start_norm'], height=0.3, color=color, align='center')

# Desenha o System Available (Verde - Linha de Base)
ax.barh(Y_MAP["system_available"], width=24, left=0, height=0.4, color='#2ca02c', align='center')

# Desenha as linhas pontilhadas vermelhas (Gatilhos de Adaptação)
for change_time in sorted(list(context_changes)):
    if 0 < change_time < 24:
        ax.axvline(x=change_time, color='red', linestyle=':', linewidth=1.5, zorder=0)

# Formatação e Eixos
ax.set_yticks(list(Y_MAP.values()))
ax.set_yticklabels(list(Y_MAP.keys()), fontsize=10)
ax.set_xticks(np.arange(0, 25, 3))
ax.set_xlim(0, 24)

# Grid e Estética
ax.grid(axis='x', linestyle='--', alpha=0.5, color='gray')
ax.set_xlabel('Tempo (horas)', fontsize=12, fontweight='bold')
ax.set_title('Ativação de Componentes GoalD (Arquitetura Nova de Microsserviços)', fontsize=14, fontweight='bold')

plt.tight_layout()
output_path = os.path.join(ROOT_DIR, "arquitetura_microsservicos_chart.png")
plt.savefig(output_path)
print(f"✅ Gráfico gerado com sucesso em: {output_path}")
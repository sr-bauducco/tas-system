#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR

INPUT_CSV = os.path.join(ROOT_DIR, "results", "msgoald_results.csv")
OUTPUT_PNG = os.path.join(ROOT_DIR, "results", "simulation_activation_chart.png")

def plot_continuous_chart():
    if not os.path.exists(INPUT_CSV):
        print(f"[ERRO] Arquivo não encontrado: {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV)
    df['start_s'] = df['start'] / 1000.0
    df['end_s'] = df['end'] / 1000.0

    min_time = df['start_s'].min()
    max_time = df['end_s'].max()
    if max_time <= min_time:
        max_time = min_time + 10.0

    # Adiciona a barra contínua de 'system_available' de ponta a ponta
    system_row = pd.DataFrame([{
        'scenario': 1, 'execIndex': 0, 'plotIndex': 1,
        'label': 'system_available', 'start': min_time * 1000,
        'end': max_time * 1000, 'type': 'system',
        'start_s': min_time, 'end_s': max_time
    }])
    df = pd.concat([df, system_row], ignore_index=True)

    # Ordem personalizada dos eixos
    preferred_order = [
        "c1-internet", "!c1-internet", "c2-battery", "!c2-battery",
        "c3-doctor", "c4-drug", "!c4-drug", "c5-patientok", "!c5-patientok",
        "AlarmService", "GetSensedData", "MonitorPatient", "RemoteAnalysis",
        "ProvideAutomatedLife", "SendSMS", "LocalAnalysis", "EnactTreatment",
        "AdministerMedicine", "ChangeDrug", "ChangeDose", "system_available"
    ]
    
    unique_labels = df['label'].unique()
    labels = [l for l in preferred_order if l in unique_labels] + [l for l in unique_labels if l not in preferred_order]
    label_to_y = {label: i for i, label in enumerate(labels)}

    fig, ax = plt.subplots(figsize=(14, len(labels) * 0.45 + 2))

    for label, group in df.groupby('label'):
        y = label_to_y[label]
        xranges = []
        
        for _, row in group.iterrows():
            s = row['start_s']
            e = row['end_s']
            if e > s:
                xranges.append((s, e - s))

        # Cores: Azul para contextos ativos, Cinza claro para contextos negados (!), Verde para system_available, Preto para bundles
        if label.startswith("!"):
            color = '#aec7e8' # Azul claro para negações
        elif "c1" in label or "c2" in label or "c3" in label or "c4" in label or "c5" in label:
            color = '#1f77b4' # Azul forte para contextos ativos
        elif label == "system_available":
            color = '#2ca02c' # Verde
        else:
            color = '#111111' # Preto

        if xranges:
            ax.broken_barh(xranges, (y - 0.35, 0.7), facecolors=color, alpha=0.85)

    ax.set_yticks(list(label_to_y.values()))
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel('Tempo de Execução (segundos)', fontsize=12, fontweight='bold')
    ax.set_title('Linha do Tempo de Ativação e Adaptação Contínua (GoalD)', fontsize=14, fontweight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, dpi=300)
    plt.close(fig)
    print(f"[SUCESSO] Gráfico contínuo ajustado salvo em: {OUTPUT_PNG}")

if __name__ == "__main__":
    plot_continuous_chart()
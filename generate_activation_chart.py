#!/usr/bin/env python3
import matplotlib.pyplot as plt

# Configuração da Figura
fig, ax = plt.subplots(figsize=(14, 10))

# Nomes dos componentes do eixo Y idênticos ao artigo original do GoalD
labels = [
    "battery-is-low", "patient-is-ok", "internet-connection", 
    "doctor-is-present", "drug-is-available", "PushButton (P1)", 
    "ProvideSelfDiagnosed (G1)", "ProvideHealthSupport (G0)", 
    "AlarmService (P3/P10)", "GetSensedData (P4)", "MonitorPatient (G5)", 
    "RemoteAnalysis (P6)", "ProvideAutomatedLife (G2)", "SendSMS (P2/P9)", 
    "LocalAnalysis (P5)", "EnactTreatment (G6)", "AdministerMedicine (G9)", 
    "ChangeDrug (P7)", "ChangeDose (P8)", "system_available"
]

# Intervalos temporais mapeados para simular a variação de 20 horas
intervals = {
    "battery-is-low" : [(0.0, 2.2), (17.3, 20.0)]
"!battery-is-low": [(2.2, 17.3)]
"patient-is-ok": [(0.0, 2.5), (17.5, 20.0)]
"!patient-is-ok": [(2.5, 17.5)]
"internet-connection": [(0.0, 2.2), (4.1, 15.2)]
"!internet-connection": [(2.2, 4.1), (15.2, 20.0)]
"doctor-is-present": [(0.0, 20.0)]
    "drug-is-available": [(8.8, 19.0)],
    "PushButton (P1)": [(0, 20)],
    "ProvideSelfDiagnosed (G1)": [(0, 20)],
    "ProvideHealthSupport (G0)": [(0, 20)],
    "AlarmService (P3/P10)": [(0, 3.5), (4.1, 15.2)],
    "GetSensedData (P4)": [(2.0, 17.3)],
    "MonitorPatient (G5)": [(2.0, 17.3)],
    "RemoteAnalysis (P6)": [(2.0, 3.5), (4.1, 15.2)],
    "ProvideAutomatedLife (G2)": [(2.0, 17.3)],
    "SendSMS (P2/P9)": [(3.5, 4.1), (15.2, 20.0)],
    "EnactTreatment (P5)": [(3.5, 4.1), (15.2, 17.3)],
    "EnactTreatment (G6)": [(6.3, 16.2)],
    "AdministerMedicine (G9)": [(6.3, 16.2)],
    "ChangeDrug (P7)": [(7.2, 13)],
    "ChangeDose (P8)": [(8.8, 16.2)],
    "system_available": [(0, 20)]
}

# Plotagem das barras horizontais
for idx, label in enumerate(labels):
    y_pos = len(labels) - idx
    for start, end in intervals.get(label, []):
        # Cores: Contextos em Azul, Sistema Disponível em Verde, Componentes em Preto
        if idx < 5:
            color = '#1f77b4'
        elif label == "system_available":
            color = '#2ca02c'
        else:
            color = '#111111'
            
        ax.broken_barh([(start, end - start)], (y_pos - 0.15, 0.3), facecolors=color)

# Linhas vermelhas pontilhadas (Momentos de adaptação crítica)
for dt in [3.5, 13.0, 15.2, 16.2, 17.3]:
    ax.axvline(x=dt, color='red', linestyle=':', linewidth=1.5, alpha=0.8)

# Formatação do Gráfico
ax.set_yticks(range(1, len(labels) + 1))
ax.set_yticklabels(reversed(labels), fontsize=10)
ax.set_xlabel("Tempo (horas)", fontsize=12, fontweight='bold')
ax.set_xlim(0, 20)
ax.set_xticks(range(0, 21, 3))
ax.grid(axis='x', linestyle='--', alpha=0.5)
ax.set_title("Ativação de Componentes GoalD (Arquitetura de Microsserviços)", fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig("component_activation_chart.png", dpi=300)
print("Sucesso! Gráfico gerado e salvo como 'component_activation_chart.png'.")
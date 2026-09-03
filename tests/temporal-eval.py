#!/usr/bin/env python3
import requests
import time
import json
import pandas as pd
from datetime import datetime
import os

# ==========================================
# CONFIGURAÇÕES DO CENÁRIO DO GRÁFICO
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR

TELEMETRY_FILE = os.path.join(ROOT_DIR, "results", "bundle_activations.jsonl")
OUTPUT_CSV = os.path.join(ROOT_DIR, "results", "msgoald_results.csv")
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

GATEWAY_URL = "http://localhost:8080/treatment/g11/execute"
CONTEXT_URL = "http://localhost:8080/api/context"

# Marcos temporais (em horas simuladas) onde ocorrem as mudanças críticas de contexto no gráfico
# Derivados diretamente de normalize-data.py (ex: quedas de internet, bateria baixa, etc.)
TIMELINE_CHECKPOINTS = [
    {"hour": 0.0,  "contexts": {"C1_Internet": True,  "C2_Battery": True,  "C3_Doctor": True,  "C4_Drug": True,  "C5_PatientOK": True}},
    {"hour": 2.2,  "contexts": {"C1_Internet": True,  "C2_Battery": False, "C3_Doctor": True,  "C4_Drug": True,  "C5_PatientOK": True}},
    {"hour": 3.5,  "contexts": {"C1_Internet": False, "C2_Battery": False, "C3_Doctor": True,  "C4_Drug": True,  "C5_PatientOK": True}},
    {"hour": 4.1,  "contexts": {"C1_Internet": True,  "C2_Battery": False, "C3_Doctor": True,  "C4_Drug": True,  "C5_PatientOK": True}},
    {"hour": 6.3,  "contexts": {"C1_Internet": True,  "C2_Battery": False, "C3_Doctor": True,  "C4_Drug": True,  "C5_PatientOK": False}},
    {"hour": 7.2,  "contexts": {"C1_Internet": True,  "C2_Battery": False, "C3_Doctor": True,  "C4_Drug": True,  "C5_PatientOK": False}},
    {"hour": 8.8,  "contexts": {"C1_Internet": True,  "C2_Battery": False, "C3_Doctor": True,  "C4_Drug": True,  "C5_PatientOK": False}},
    {"hour": 13.0, "contexts": {"C1_Internet": True,  "C2_Battery": False, "C3_Doctor": True,  "C4_Drug": False, "C5_PatientOK": False}},
    {"hour": 15.2, "contexts": {"C1_Internet": False, "C2_Battery": False, "C3_Doctor": True,  "C4_Drug": False, "C5_PatientOK": False}},
    {"hour": 16.2, "contexts": {"C1_Internet": True,  "C2_Battery": False, "C3_Doctor": True,  "C4_Drug": False, "C5_PatientOK": False}},
    {"hour": 17.3, "contexts": {"C1_Internet": True,  "C2_Battery": True,  "C3_Doctor": True,  "C4_Drug": False, "C5_PatientOK": False}},
    {"hour": 20.0, "contexts": {"C1_Internet": True,  "C2_Battery": True,  "C3_Doctor": True,  "C4_Drug": True,  "C5_PatientOK": True}}
]

def clear_old_telemetry():
    if os.path.exists(TELEMETRY_FILE):
        open(TELEMETRY_FILE, 'w').close()

def update_system_context(contexts):
    """Injeta as mudanças de contexto no microsserviço/gateway."""
    for ctx_key, state in contexts.items():
        try:
            requests.post(f"{CONTEXT_URL}/{ctx_key}?state={'true' if state else 'false'}", timeout=1.0)
        except Exception:
            pass

def run_simulation():
    clear_old_telemetry()
    print("[SIMULAÇÃO TAS] Replay temporal do GoalD iniciado...")
    
    client_results = []
    
    # Fator de compressão: 1 hora simulada = 0.5 segundo real para agilizar os testes
    TIME_SCALE = 0.5 
    test_start_epoch = int(time.time() * 1000)
    
    for idx, cp in enumerate(TIMELINE_CHECKPOINTS):
        sim_hour = cp["hour"]
        contexts = cp["contexts"]
        
        print(f" -> [Tempo Simulado: {sim_hour}h] Aplicando alteração de contexto...")
        update_system_context(contexts)
        
        # Constrói cabeçalhos HTTP com o estado atual dos contextos do gráfico
        headers = {
            "X-Target-Goal": "G11_Treatment",
            "Content-Type": "application/json",
            "X-Context-Internet": str(contexts["C1_Internet"]),
            "X-Context-Battery": str(contexts["C2_Battery"]),
            "X-Context-Doctor": str(contexts["C3_Doctor"]),
            "X-Context-Drug": str(contexts["C4_Drug"]),
            "X-Context-Patient": str(contexts["C5_PatientOK"])
        }
        
        req_start = int(time.time() * 1000)
        status_code = 500
        try:
            res = requests.post(GATEWAY_URL, headers=headers, json={"patientId": "P-101"}, timeout=3.0)
            status_code = res.status_code
        except Exception:
            pass
        req_end = int(time.time() * 1000)
        
        # Grava os estados ativos para a geração do gráfico equivalente
        for ctx_name, state in contexts.items():
            label_name = ctx_name.lower().replace('_', '-')
            if not state:
                label_name = f"!{label_name}"
                
            client_results.append({
                "scenario": 1,
                "execIndex": idx + 1,
                "plotIndex": 0,
                "label": label_name,
                "start": req_start,
                "end": req_end,
                "type": "context"
            })
            
        client_results.append({
            "scenario": 1,
            "execIndex": idx + 1,
            "plotIndex": 0,
            "label": "client-request",
            "start": req_start,
            "end": req_end,
            "type": f"http-{status_code}"
        })
        
        time.sleep(TIME_SCALE)

    return client_results

def process_results(client_results):
    print("Consolidando telemetria interna com os marcos temporais...")
    server_results = []
    
    if os.path.exists(TELEMETRY_FILE):
        with open(TELEMETRY_FILE, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    dt_obj = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
                    end_ms = int(dt_obj.timestamp() * 1000)
                    
                    if data["type"] == "execution":
                        duration_ms = data.get("durationMs", 0)
                        start_ms = int(end_ms - duration_ms)
                        label = data.get("bundle", "unknown")
                        plot_index = 1
                        type_label = "bundle"
                    else:
                        start_ms = end_ms
                        label = f"{data.get('source')}-{data.get('eventName')}"
                        plot_index = 2
                        type_label = "event"
                    
                    server_results.append({
                        "scenario": 1,
                        "execIndex": 1,
                        "plotIndex": plot_index,
                        "label": label,
                        "start": start_ms,
                        "end": end_ms,
                        "type": type_label
                    })
                except Exception:
                    pass

    df = pd.DataFrame(client_results + server_results)
    if not df.empty:
        min_start = df['start'].min()
        df['start'] = df['start'] - min_start
        df['end'] = df['end'] - min_start
        
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[SUCESSO] Simulação concluída! Dados salvos em: {OUTPUT_CSV}")
    return df

if __name__ == "__main__":
    client_data = run_simulation()
    time.sleep(1)
    df_final = process_results(client_data)
    print(df_final.head(10).to_string())
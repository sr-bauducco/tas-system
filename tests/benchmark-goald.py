#!/usr/bin/env python3

import requests
import time
import json
import pandas as pd
from datetime import datetime
import itertools
import os

# ==========================================
# CONFIGURAÇÕES DE DIRETÓRIOS E ROTAS
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR

TELEMETRY_FILE = os.path.join(ROOT_DIR, "results", "bundle_activations.jsonl")
OUTPUT_CSV = os.path.join(ROOT_DIR, "results", "msgoald_results.csv")
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

GATEWAY_URL = "http://localhost:8080/treatment/g11/execute"

# ==========================================
# DEFINIÇÃO DOS CONTEXTOS C1 ATÉ C5
# ==========================================
# C1: Internet Connection, C2: Battery Low, C3: Doctor Present, C4: Drug Available, C5: Patient OK
CONTEXT_KEYS = ["C1_Internet", "C2_BatteryLow", "C3_DoctorPresent", "C4_DrugAvailable", "C5_PatientOK"]

def clear_old_telemetry():
    if os.path.exists(TELEMETRY_FILE):
        open(TELEMETRY_FILE, 'w').close()

def run_exhaustive_context_tests():
    clear_old_telemetry()
    print("[TESTE EXAUSTIVO] Iniciando testes para todas as combinações de C1 a C5 (32 cenários)...")
    
    client_results = []
    scenario_id = 1
    
    # Gera todas as permutações booleanas de C1 a C5 (True/False)
    for combination in itertools.product([True, False], repeat=5):
        context_state = dict(zip(CONTEXT_KEYS, combination))
        
        # Mapeia para os cabeçalhos esperados pela arquitetura
        headers = {
            "X-Target-Goal": "G11_Treatment",
            "Content-Type": "application/json",
            "X-Context-Internet": str(context_state["C1_Internet"]),
            "X-Context-Battery": str(context_state["C2_BatteryLow"]),
            "X-Context-Doctor": str(context_state["C3_DoctorPresent"]),
            "X-Context-Drug": str(context_state["C4_DrugAvailable"]),
            "X-Context-Patient": str(context_state["C5_PatientOK"])
        }
        
        payload = {"patientId": "P-101", "contextState": context_state}
        
        start_time = int(time.time() * 1000)
        status_code = 500
        try:
            response = requests.post(GATEWAY_URL, headers=headers, json=payload, timeout=3.0)
            status_code = response.status_code
        except Exception:
            pass
        end_time = int(time.time() * 1000)
        
        # Registra o estado dos contextos como linhas de contexto no padrão GoalD
        for ctx_name, state in context_state.items():
            label_name = f"{ctx_name.lower().replace('_', '-')}"
            if not state:
                label_name = f"!{label_name}"
                
            client_results.append({
                "scenario": scenario_id,
                "execIndex": scenario_id,
                "plotIndex": 0,
                "label": label_name,
                "start": start_time,
                "end": end_time,
                "type": "context"
            })
            
        # Registra a requisição do cliente
        client_results.append({
            "scenario": scenario_id,
            "execIndex": scenario_id,
            "plotIndex": 0,
            "label": "client-request",
            "start": start_time,
            "end": end_time,
            "type": f"http-{status_code}"
        })
        
        scenario_id += 1
        time.sleep(0.02) # Pequeno resfriamento entre cenários

    return client_results

def process_telemetry(client_results):
    print("Processando rastros de telemetria dos microserviços...")
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

    all_data = client_results + server_results
    df = pd.DataFrame(all_data)
    
    if not df.empty:
        min_start = df['start'].min()
        df['start'] = df['start'] - min_start
        df['end'] = df['end'] - min_start
        
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[SUCESSO] Benchmark completo salvo em: {OUTPUT_CSV}")
    return df

if __name__ == "__main__":
    client_res = run_exhaustive_context_tests()
    time.sleep(1)
    df_final = process_telemetry(client_res)
    print("\nAmostra do resultado gerado:")
    print(df_final.head(10).to_string())
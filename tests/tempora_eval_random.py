#!/usr/bin/env python3
import requests
import time
import json
import random
import pandas as pd
from datetime import datetime
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR

TELEMETRY_FILE = os.path.join(ROOT_DIR, "results", "bundle_activations.jsonl")
OUTPUT_CSV = os.path.join(ROOT_DIR, "results", "random_msgoald_results.csv")
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

GATEWAY_URL = "http://localhost:8080/treatment/g11/execute"

# Chaves padronizadas para corresponder exatamente aos dicionários
CONTEXT_KEYS = ["c1-internet", "c2-battery", "c3-doctor", "c4-drug", "c5-patientok"]

def clear_old_telemetry():
    if os.path.exists(TELEMETRY_FILE):
        open(TELEMETRY_FILE, 'w').close()

def run_random_chaos_simulation(iterations=30):
    clear_old_telemetry()
    print(f"[CHAOS SIMULATION] Iniciando {iterations} ciclos com mudanças contextuais aleatórias...")
    
    client_results = []
    base_time = int(time.time() * 1000)
    
    active_states = {k: True for k in CONTEXT_KEYS}
    state_start_times = {k: base_time for k in CONTEXT_KEYS}

    for step in range(1, iterations + 1):
        req_start = int(time.time() * 1000)
        
        current_contexts = {
            "c1-internet": random.choice([True, True, False]),
            "c2-battery": random.choice([True, False]),
            "c3-doctor": random.choice([True, True, False]),
            "c4-drug": random.choice([True, False]),
            "c5-patientok": random.choice([True, False, False])
        }
        
        headers = {
            "X-Target-Goal": "G11_Treatment",
            "Content-Type": "application/json",
            "X-Context-Internet": str(current_contexts["c1-internet"]),
            "X-Context-Battery": str(current_contexts["c2-battery"]),
            "X-Context-Doctor": str(current_contexts["c3-doctor"]),
            "X-Context-Drug": str(current_contexts["c4-drug"]),
            "X-Context-Patient": str(current_contexts["c5-patientok"])
        }
        
        print(f" -> [Ciclo {step}] Contexto Sorteado: {current_contexts}")
        
        status_code = 500
        try:
            res = requests.post(GATEWAY_URL, headers=headers, json={"patientId": "P-101"}, timeout=2.0)
            status_code = res.status_code
        except Exception:
            pass
        req_end = int(time.time() * 1000)
        
        for ctx_name, state in current_contexts.items():
            prev_state = active_states.get(ctx_name)
            if prev_state != state:
                old_label = ctx_name if prev_state else f"!{ctx_name}"
                client_results.append({
                    "scenario": 1, "execIndex": step, "plotIndex": 0,
                    "label": old_label, "start": state_start_times[ctx_name],
                    "end": req_end, "type": "context"
                })
                active_states[ctx_name] = state
                state_start_times[ctx_name] = req_end

        client_results.append({
            "scenario": 1, "execIndex": step, "plotIndex": 0,
            "label": "client-request", "start": req_start, "end": req_end,
            "type": f"http-{status_code}"
        })
        
        time.sleep(0.5)

    final_end = int(time.time() * 1000)
    for ctx_name, state in active_states.items():
        label = ctx_name if state else f"!{ctx_name}"
        client_results.append({
            "scenario": 1, "execIndex": 99, "plotIndex": 0,
            "label": label, "start": state_start_times[ctx_name],
            "end": final_end, "type": "context"
        })

    return client_results

def process_results(client_results):
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
                        server_results.append({
                            "scenario": 1, "execIndex": 1, "plotIndex": 1,
                            "label": label, "start": start_ms, "end": end_ms, "type": "bundle"
                        })
                except Exception:
                    pass

    df = pd.DataFrame(client_results + server_results)
    if not df.empty:
        min_start = df['start'].min()
        df['start'] = df['start'] - min_start
        df['end'] = df['end'] - min_start
        
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[SUCESSO] Simulação de caos concluída! Dados salvos em: {OUTPUT_CSV}")
    return df

if __name__ == "__main__":
    client_data = run_random_chaos_simulation(iterations=100)
    process_results(client_data)
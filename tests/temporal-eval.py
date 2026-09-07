#!/usr/bin/env python3
import requests
import time
import json
import pandas as pd
from datetime import datetime
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR

TELEMETRY_FILE = os.path.join(ROOT_DIR, "results", "bundle_activations.jsonl")
OUTPUT_CSV = os.path.join(ROOT_DIR, "results", "msgoald_results.csv")
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

GATEWAY_URL = "http://localhost:8080/treatment/g11/execute"
CONTEXT_URL = "http://localhost:8080/api/context"

# Marcos temporais (em horas simuladas) e seus estados de contexto correspondentes
TIMELINE_CHECKPOINTS = [
    {"hour": 0.0,  "contexts": {"c1-internet": True,  "c2-battery": True,  "c3-doctor": True,  "c4-drug": True,  "c5-patientok": True}},
    {"hour": 2.2,  "contexts": {"c1-internet": True,  "c2-battery": False, "c3-doctor": True,  "c4-drug": True,  "c5-patientok": True}},
    {"hour": 3.5,  "contexts": {"c1-internet": False, "c2-battery": False, "c3-doctor": True,  "c4-drug": True,  "c5-patientok": True}},
    {"hour": 4.1,  "contexts": {"c1-internet": True,  "c2-battery": False, "c3-doctor": True,  "c4-drug": True,  "c5-patientok": True}},
    {"hour": 6.3,  "contexts": {"c1-internet": True,  "c2-battery": False, "c3-doctor": True,  "c4-drug": True,  "c5-patientok": False}},
    {"hour": 7.2,  "contexts": {"c1-internet": True,  "c2-battery": False, "c3-doctor": True,  "c4-drug": True,  "c5-patientok": False}},
    {"hour": 8.8,  "contexts": {"c1-internet": True,  "c2-battery": False, "c3-doctor": True,  "c4-drug": True,  "c5-patientok": False}},
    {"hour": 13.0, "contexts": {"c1-internet": True,  "c2-battery": False, "c3-doctor": True,  "c4-drug": False, "c5-patientok": False}},
    {"hour": 15.2, "contexts": {"c1-internet": False, "c2-battery": False, "c3-doctor": True,  "c4-drug": False, "c5-patientok": False}},
    {"hour": 16.2, "contexts": {"c1-internet": True,  "c2-battery": False, "c3-doctor": True,  "c4-drug": False, "c5-patientok": False}},
    {"hour": 17.3, "contexts": {"c1-internet": True,  "c2-battery": True,  "c3-doctor": True,  "c4-drug": False, "c5-patientok": False}},
    {"hour": 20.0, "contexts": {"c1-internet": True,  "c2-battery": True,  "c3-doctor": True,  "c4-drug": True,  "c5-patientok": True}}
]

def clear_old_telemetry():
    if os.path.exists(TELEMETRY_FILE):
        open(TELEMETRY_FILE, 'w').close()

def run_simulation():
    clear_old_telemetry()
    print("[SIMULAÇÃO TAS] Gerando intervalos contínuos de contexto...")
    
    client_results = []
    TIME_SCALE = 0.5  # Fator de velocidade em segundos por checkpoint
    
    # Rastreia o momento de início de cada estado de contexto
    active_states = {}
    state_start_times = {}

    base_time = time.time() * 1000

    for idx, cp in enumerate(TIMELINE_CHECKPOINTS):
        sim_hour = cp["hour"]
        contexts = cp["contexts"]
        current_time = base_time + (sim_hour * 3600 * 1000 / 3600) * (TIME_SCALE * 1000 / 0.5) # Escala proporcional

        for ctx_name, state in contexts.items():
            prev_state = active_states.get(ctx_name)
            
            # Se o estado mudou ou é o primeiro registro
            if prev_state != state:
                # Se já havia um estado anterior ativo, fecha o intervalo dele
                if prev_state is not None:
                    old_label = ctx_name if prev_state else f"!{ctx_name}"
                    client_results.append({
                        "scenario": 1,
                        "execIndex": idx,
                        "plotIndex": 0,
                        "label": old_label,
                        "start": state_start_times[ctx_name],
                        "end": int(current_time),
                        "type": "context"
                    })
                # Inicia o novo estado
                active_states[ctx_name] = state
                state_start_times[ctx_name] = int(current_time)

        # Dispara requisição HTTP simulando a carga no gateway
        try:
            requests.post(GATEWAY_URL, json={"patientId": "P-101"}, timeout=1.0)
        except Exception:
            pass

    # Fecha os estados pendentes até o final da simulação (20h)
    final_time = base_time + (20.0 * 1000 * TIME_SCALE * 2)
    for ctx_name, state in active_states.items():
        label = ctx_name if state else f"!{ctx_name}"
        client_results.append({
            "scenario": 1,
            "execIndex": 99,
            "plotIndex": 0,
            "label": label,
            "start": state_start_times[ctx_name],
            "end": int(final_time),
            "type": "context"
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
    print(f"[SUCESSO] Dados contínuos salvos em: {OUTPUT_CSV}")
    return df

if __name__ == "__main__":
    client_data = run_simulation()
    process_results(client_data)
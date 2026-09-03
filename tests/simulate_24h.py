#!/usr/bin/env python3
import requests
import time
import json
import random
import pandas as pd
from datetime import datetime
import os

# Configurações de Diretórios
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR

TELEMETRY_FILE = os.path.join(ROOT_DIR, "bundle_activations.jsonl")
OUTPUT_CSV = os.path.join(ROOT_DIR, "results", "msgoald_24h_results.csv")
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

GATEWAY_URL = "http://localhost:8080/treatment/g11/execute"
CONTEXT_KEYS = ["c1-internet", "c2-battery", "c3-doctor", "c4-drug", "c5-patientok"]

def clear_old_telemetry():
    if os.path.exists(TELEMETRY_FILE):
        open(TELEMETRY_FILE, 'w').close()

def wait_for_gateway():
    print("[INIT] Aquecendo o Gateway para simulação de 24h...")
    headers = {
        "X-Target-Goal": "G11_Treatment",
        "Content-Type": "application/json",
        "X-Context-Internet": "True",
        "X-Context-Battery": "True",
        "X-Context-Doctor": "True",
        "X-Context-Drug": "True",
        "X-Context-Patient": "True",
        "X-Simulation-Time-Ms": str(int(time.time() * 1000)),
        "X-Scenario": "24h",
        "X-Exec-Index": "0"
    }
    for attempt in range(30):
        try:
            res = requests.post(GATEWAY_URL, headers=headers, json={"patientId": "warmup"}, timeout=2.0)
            if res.status_code == 200:
                print("[INIT] Gateway Roteando com Sucesso! Iniciando simulação temporal...\n")
                time.sleep(1)
                return
        except Exception:
            pass
        time.sleep(2)
    print("\n[FATAL] Gateway indisponível.")
    exit(1)

def run_24h_simulation():
    wait_for_gateway()
    clear_old_telemetry()
    
    client_results = []
    base_time = int(time.time() * 1000)
    
    active_states = {k: True for k in CONTEXT_KEYS}
    state_start_times = {k: base_time for k in CONTEXT_KEYS}
    
    # 48 ciclos simulando intervalos de 30 minutos em um dia
    ciclos = 48 
    print(f"[SIMULAÇÃO 24H] Rodando {ciclos} ciclos de perturbação e requisições...")

    for step in range(1, ciclos + 1):
        req_start = int(time.time() * 1000)
        
        # Probabilidades realistas para as flutuações das variáveis ao longo do dia
        current_contexts = {
            "c1-internet": random.choices([True, False], weights=[85, 15])[0], # Internet cai 15% do tempo
            "c2-battery": random.choices([True, False], weights=[60, 40])[0],  # Bateria oscila mais
            "c3-doctor": random.choices([True, False], weights=[50, 50])[0],   # Médico entra e sai em turnos
            "c4-drug": random.choices([True, False], weights=[70, 30])[0],     # Remédio às vezes acaba
            "c5-patientok": random.choices([True, False], weights=[90, 10])[0] # Paciente tem crises esporádicas
        }
        
        headers = {
            "X-Target-Goal": "G11_Treatment",
            "Content-Type": "application/json",
            "X-Context-Internet": str(current_contexts["c1-internet"]),
            "X-Context-Battery": str(current_contexts["c2-battery"]),
            "X-Context-Doctor": str(current_contexts["c3-doctor"]),
            "X-Context-Drug": str(current_contexts["c4-drug"]),
            "X-Context-Patient": str(current_contexts["c5-patientok"]),
            "X-Simulation-Time-Ms": str(req_start),
            "X-Scenario": "24h",
            "X-Exec-Index": str(step)
        }
        
        # Simula de 1 a 4 chamadas daquele contexto para estressar o balanceador e disparar bundles
        for _ in range(random.randint(1, 4)):
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
                    "scenario": "24h", "execIndex": step, "plotIndex": 0,
                    "label": old_label, "start": state_start_times[ctx_name],
                    "end": req_end, "type": "context"
                })
                active_states[ctx_name] = state
                state_start_times[ctx_name] = req_end

        client_results.append({
            "scenario": "24h", "execIndex": step, "plotIndex": 0,
            "label": "client-request", "start": req_start, "end": req_end,
            "type": f"http-{status_code}"
        })
        
        time.sleep(0.15) # Compressão do tempo de simulação

    final_end = int(time.time() * 1000)
    for ctx_name, state in active_states.items():
        label = ctx_name if state else f"!{ctx_name}"
        client_results.append({
            "scenario": "24h", "execIndex": 99, "plotIndex": 0,
            "label": label, "start": state_start_times[ctx_name],
            "end": final_end, "type": "context"
        })

    return client_results

def process_and_analyze(client_results):
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
                            "scenario": "24h", "execIndex": data.get("traceId", 1), "plotIndex": 1,
                            "label": label, "start": start_ms, "end": end_ms, "type": "bundle"
                        })
                except Exception:
                    pass

    df = pd.DataFrame(client_results + server_results)
    if df.empty:
        return

    # Normaliza o tempo
    min_start = df['start'].min()
    df['start'] = df['start'] - min_start
    df['end'] = df['end'] - min_start
    df['duration_ms'] = df['end'] - df['start']
    
    df.to_csv(OUTPUT_CSV, index=False)
    
    print("\n" + "="*70)
    print(" 📊 RELATÓRIO EXECUTIVO - SIMULAÇÃO DE 24 HORAS ")
    print("="*70)
    
    print("\n--- 1. TEMPO DE ATIVAÇÃO DOS CONTEXTOS AMBIENTAIS ---")
    # Calcula o tempo total real gasto correndo o teste para calcular a porcentagem
    total_sim_time = df[df['type'] == 'context']['duration_ms'].sum() / len(CONTEXT_KEYS)
    
    context_df = df[df['type'] == 'context'].groupby('label')['duration_ms'].sum().reset_index()
    for _, row in context_df.iterrows():
        lbl = row['label']
        dur = row['duration_ms']
        perc = (dur / total_sim_time) * 100 if total_sim_time > 0 else 0
        status_text = "🟢 ATIVO" if not lbl.startswith('!') else "🔴 EM FALHA"
        # Ajusta nome legível
        print(f"[{status_text}] {lbl:15} : Passou {perc:5.1f}% do dia nesse estado")

    print("\n--- 2. EXECUÇÃO DE ROTAS / MICROSSERVIÇOS (CPU TIME) ---")
    bundle_df = df[df['type'] == 'bundle']
    if bundle_df.empty:
        print("Nenhum componente registrou telemetria neste período.")
    else:
        bundle_stats = bundle_df.groupby('label').agg(
            chamadas=('label', 'count'),
            tempo_total_ms=('duration_ms', 'sum'),
            tempo_medio_ms=('duration_ms', 'mean')
        ).sort_values(by='chamadas', ascending=False).reset_index()
        
        for _, row in bundle_stats.iterrows():
            print(f"🚀 Rota/Plano: {row['label']:20} | Acionada: {row['chamadas']:<3} vezes | Tempo Total: {row['tempo_total_ms']:6.1f}ms | Média: {row['tempo_medio_ms']:.1f}ms/chamada")
            
    print("="*70 + "\n")

if __name__ == "__main__":
    client_data = run_24h_simulation()
    process_and_analyze(client_data)
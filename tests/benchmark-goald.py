#!/usr/bin/env python3

import requests
import time
import json
import pandas as pd
from datetime import datetime
import concurrent.futures
import os

# ==========================================
# CONFIGURAÇÕES DE DIRETÓRIOS (ROBUSTO)
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(SCRIPT_DIR) == "tests":
    ROOT_DIR = os.path.dirname(SCRIPT_DIR)
else:
    ROOT_DIR = SCRIPT_DIR

TELEMETRY_FILE = os.path.join(ROOT_DIR, "results", "bundle_activations.jsonl")
OUTPUT_CSV = os.path.join(ROOT_DIR, "results", "msgoald_benchmark_results.csv")

os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# ==========================================
# CONFIGURAÇÕES DO TESTE
# ==========================================
GATEWAY_URL = "http://localhost:8080/treatment/g11/execute" 
HEADERS = {"X-Target-Goal": "G11_Treatment", "Content-Type": "application/json"}

NUM_REQUESTS = 50
CONCURRENT_USERS = 10

# ==========================================
# FUNÇÕES DE EXECUÇÃO
# ==========================================
def clear_old_telemetry():
    """Limpa a telemetria antiga para garantir um teste limpo."""
    if os.path.exists(TELEMETRY_FILE):
        open(TELEMETRY_FILE, 'w').close()

def send_request(exec_index):
    """Envia uma requisição ao Gateway e mede a latência do lado do cliente."""
    start_time = int(time.time() * 1000)
    
    try:
        payload = {"patientId": "P-101"}
        response = requests.post(GATEWAY_URL, headers=HEADERS, json=payload, timeout=5)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        
    end_time = int(time.time() * 1000)
    
    return {
        "scenario": 1,
        "execIndex": exec_index + 1,
        "plotIndex": 0,
        "label": "client-request",
        "start": start_time,
        "end": end_time,
        "type": f"http-{status_code}"
    }

def run_stress_test():
    """Executa as requisições em paralelo."""
    print(f"Iniciando teste com {NUM_REQUESTS} requisições ({CONCURRENT_USERS} simultâneas)...")
    client_results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = [executor.submit(send_request, i) for i in range(NUM_REQUESTS)]
        for future in concurrent.futures.as_completed(futures):
            client_results.append(future.result())
            
    return client_results

# ==========================================
# PROCESSAMENTO DE DADOS
# ==========================================
def process_telemetry(client_results):
    """Lê o JSONL gerado pelos microserviços e formata para o padrão CSV."""
    print("Processando dados de telemetria dos microserviços...")
    server_results = []
    
    trace_to_index = {}
    current_exec_index = 1
    
    if os.path.exists(TELEMETRY_FILE):
        with open(TELEMETRY_FILE, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    
                    dt_obj = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
                    end_ms = int(dt_obj.timestamp() * 1000)
                    
                    trace_id = data.get("traceId", "N/A")
                    if trace_id not in trace_to_index:
                        trace_to_index[trace_id] = current_exec_index
                        current_exec_index += 1
                    numeric_exec_index = trace_to_index[trace_id]
                    
                    if data["type"] == "execution":
                        duration_ms = data.get("durationMs", 0)
                        start_ms = int(end_ms - duration_ms)
                        label = data.get("bundle", "unknown")
                        plot_index = 1 
                        type_label = "context"
                    else:
                        start_ms = end_ms
                        label = f"{data.get('source')}-{data.get('eventName')}"
                        plot_index = 2
                        type_label = "event"
                    
                    server_results.append({
                        "scenario": 1,
                        "execIndex": numeric_exec_index,
                        "plotIndex": plot_index, 
                        "label": label,
                        "start": start_ms,
                        "end": end_ms,
                        "type": type_label
                    })
                except Exception as e:
                    print(f"Erro ao analisar linha: {e}")
    
    all_data = client_results + server_results
    df = pd.DataFrame(all_data)
    
    if not df.empty:
        min_start = df['start'].min()
        df['start'] = df['start'] - min_start
        df['end'] = df['end'] - min_start
        
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSucesso! Resultados salvos em: {OUTPUT_CSV}")
    return df

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    clear_old_telemetry()
    client_res = run_stress_test()
    time.sleep(2) 
    df_final = process_telemetry(client_res)
    
    print("\nAmostra dos resultados gerados:")
    print(df_final.head().to_string())
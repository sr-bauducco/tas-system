import requests
import time
import json
import pandas as pd
from datetime import datetime
import concurrent.futures
import os

# ==========================================
# CONFIGURAÇÕES DO TESTE
# ==========================================
# Atualize este endpoint para a rota real do seu ms-gateway
GATEWAY_URL = "http://localhost:8080/api/v1/trigger-adaptation" 
NUM_REQUESTS = 50
CONCURRENT_USERS = 10

TELEMETRY_FILE = "results/bundle_activations.jsonl"
OUTPUT_CSV = "results/msgoald_benchmark_results.csv"

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
        # Substitua este payload pelo JSON esperado pelo seu sistema
        payload = {"context": "battery-is-low", "value": 15}
        response = requests.post(GATEWAY_URL, json=payload, timeout=5)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        
    end_time = int(time.time() * 1000)
    
    return {
        "scenario": 1,
        "execIndex": exec_index,
        "plotIndex": 0,
        "label": "client-request",
        "start": start_time,
        "end": end_time,
        "type": f"http-{status_code}"
    }

def run_stress_test():
    """Executa as requisições em paralelo (Stress Test)."""
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
    """Lê o JSONL gerado pelos microserviços Java e formata para o padrão GoalD."""
    print("Processando dados de telemetria dos microserviços...")
    server_results = []
    
    if os.path.exists(TELEMETRY_FILE):
        with open(TELEMETRY_FILE, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    
                    # Converte o timestamp ISO 8601 (Instant.now() do Java) para epoch (ms)
                    dt_obj = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
                    end_ms = int(dt_obj.timestamp() * 1000)
                    
                    if data["type"] == "execution":
                        # Se for execução de bundle, calculamos o start baseado na duração
                        duration_ms = data.get("durationMs", 0)
                        start_ms = int(end_ms - duration_ms)
                        label = data.get("bundle", "unknown")
                    else:
                        # Se for apenas um evento de sistema (ex: system_available)
                        start_ms = end_ms
                        label = f"{data.get('source')}-{data.get('eventName')}"
                    
                    server_results.append({
                        "scenario": 1,
                        "execIndex": data.get("traceId", "N/A"), # TraceID unifica o ciclo
                        "plotIndex": 1, 
                        "label": label,
                        "start": start_ms,
                        "end": end_ms,
                        "type": data["type"]
                    })
                except Exception as e:
                    print(f"Erro ao analisar linha da telemetria: {e}")
    
    # Junta os tempos medidos pelo cliente com os tempos medidos pelo Java
    all_data = client_results + server_results
    df = pd.DataFrame(all_data)
    
    # Normalização da Linha do Tempo
    # Subtrai o menor 'start' de todos os registros para que o teste comece em t=0ms
    if not df.empty:
        min_start = df['start'].min()
        df['start'] = df['start'] - min_start
        df['end'] = df['end'] - min_start
        
    # Salva o arquivo final
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSucesso! Resultados salvos em: {OUTPUT_CSV}")
    return df

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
if __name__ == "__main__":
    clear_old_telemetry()
    
    client_res = run_stress_test()
    
    # Aguarda o sistema de I/O do Java terminar as gravações pendentes
    time.sleep(2) 
    
    df_final = process_telemetry(client_res)
    
    print("\nAmostra dos resultados gerados:")
    print(df_final.head().to_markdown())
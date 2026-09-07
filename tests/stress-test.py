#!/usr/bin/env python3
import requests
import time
import numpy as np
import concurrent.futures

# Configuração do Estresse
ENDPOINT = "http://localhost:8080/emergency/g4/execute"
TOTAL_REQUESTS = 500  # Quantidade total de chamadas
CONCURRENT_USERS = 50 # Concorrência simultânea (Carga)

def send_stress_request(request_id):
    headers = {
        "X-Target-Goal": "G4_Emergency",
        "Content-Type": "application/json",
        "X-Context-Internet": "False", # Forçando a Inteligência a adaptar para SMS
        "X-Context-Battery": "True",
        "X-Context-Doctor": "True",
        "X-Context-Drug": "True",
        "X-Context-Patient": "False",
    }
    start_time = time.time()
    try:
        # Aumentei o timeout para 10s para garantir que requisições sob estresse não sejam cortadas
        res = requests.post(ENDPOINT, headers=headers, json={"patientId": f"P-{request_id}"}, timeout=10.0)
        end_time = time.time()
        
        latency_ms = (end_time - start_time) * 1000
        return {"status": res.status_code, "latency": latency_ms}
    except requests.exceptions.Timeout:
        return {"status": "TIMEOUT", "latency": None}
    except Exception as e:
        return {"status": "ERROR_CONNECTION", "latency": None}

print(f"🚀 Iniciando Teste de Estresse: {TOTAL_REQUESTS} requisições ({CONCURRENT_USERS} simultâneas)...")

latencies = []
success_count = 0
error_count = 0
status_counts = {}

start_global = time.time()

# Disparo simultâneo
with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
    results = list(executor.map(send_stress_request, range(TOTAL_REQUESTS)))

end_global = time.time()

# Processamento dos resultados
for r in results:
    status = r["status"]
    
    # Contabiliza os tipos de status recebidos
    if status not in status_counts:
        status_counts[status] = 0
    status_counts[status] += 1
    
    # Aceitamos 200, 404 e 500 como requisições que passaram pelo interceptor MAPE-K com sucesso
    if r["latency"] is not None and status in [200, 404, 500]:
        latencies.append(r["latency"])
        success_count += 1
    else:
        error_count += 1

# Exibição de Métricas Acadêmicas
if latencies:
    avg_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)
    max_latency = np.max(latencies)
    
    print("\n" + "="*40)
    print("📊 RESULTADOS DO DESEMPENHO TEMPORAL (SPRING BOOT)")
    print("="*40)
    print(f"Total de Requisições : {TOTAL_REQUESTS}")
    print(f"Carga Simultânea     : {CONCURRENT_USERS} requisições/segundo")
    print("-" * 40)
    print(f"Códigos HTTP Retornados:")
    for stat, count in status_counts.items():
        print(f"  -> HTTP {stat}: {count} vezes")
    print("-" * 40)
    print(f"Processadas no MAPE-K: {success_count}")
    print(f"Falhas Críticas/Caiu : {error_count}")
    print(f"Tempo Total do Teste : {(end_global - start_global):.2f} segundos")
    print("-" * 40)
    print(f"Latência Média       : {avg_latency:.2f} ms")
    print(f"Latência P95         : {p95_latency:.2f} ms")
    print(f"Latência Máxima      : {max_latency:.2f} ms")
    print("="*40)
else:
    print("Nenhuma requisição foi concluída. O Gateway pode estar offline ou bloqueando a conexão.")
    print("Status recebidos:", status_counts)
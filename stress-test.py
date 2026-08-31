#!/usr/bin/env python3
import requests
import time
import concurrent.futures

# --- CONFIGURAÇÃO ---
# Altere a URL abaixo para apontar para o Spring Boot ou para o OSGi, dependendo de qual estiver testando
TARGET_URL = "http://localhost:8080/treatment/g11/execute" 
HEADERS = {"X-Target-Goal": "G11_Treatment", "Content-Type": "application/json"}
PAYLOAD = {"patientId": "P-101"}

NUM_USERS = 50
REQUESTS_PER_USER = 100

def simulate_device(user_id):
    success, failed = 0, 0
    total_latency = 0.0
    
    for _ in range(REQUESTS_PER_USER):
        req_start = time.perf_counter()
        try:
            res = requests.post(TARGET_URL, headers=HEADERS, json=PAYLOAD, timeout=2.0)
            if res.status_code in [200, 201, 202, 204, 404, 405]:
                success += 1
                total_latency += (time.perf_counter() - req_start) * 1000.0 # Converte para ms
            else:
                failed += 1
        except Exception:
            failed += 1
        time.sleep(0.1)
        
    avg_latency = (total_latency / success) if success > 0 else 0
    return user_id, success, failed, avg_latency

if __name__ == "__main__":
    print(f"[TESTE DE DESEMPENHO] Iniciando com {NUM_USERS} usuários virtuais...")
    start_time = time.time()
    
    total_success, total_failed = 0, 0
    sum_of_avg_latencies = 0.0
    valid_users = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_USERS) as executor:
        results = executor.map(simulate_device, range(NUM_USERS))
        
        for user_id, success, failed, avg_latency in results:
            total_success += success
            total_failed += failed
            if success > 0:
                sum_of_avg_latencies += avg_latency
                valid_users += 1

    duration = time.time() - start_time
    global_avg_latency = (sum_of_avg_latencies / valid_users) if valid_users > 0 else 0

    print("\n--- RESULTADOS DO TESTE DE DESEMPENHO ---")
    print(f"Tempo total do lote: {duration:.2f} segundos")
    print(f"Requisições com Sucesso: {total_success}")
    print(f"Requisições com Falha: {total_failed}")
    print(f"Throughput: {(total_success + total_failed) / duration:.2f} req/s")
    print(f"Latência Média por Requisição: {global_avg_latency:.2f} ms")
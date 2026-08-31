#!/usr/bin/env python3
import requests
import time
import statistics

# --- CONFIGURAÇÃO ---
# Altere para a porta do OSGi quando for avaliar a abordagem base
BASE_URL = "http://localhost:8080"

# Cenários de comportamento equivalente mapeados para extração de custo temporal
SCENARIOS = {
    "Fluxo_Normal_Tratamento": {
        "url": f"{BASE_URL}/treatment/g11/execute",
        "headers": {"X-Target-Goal": "G11_Treatment", "Content-Type": "application/json"},
        "payload": {"patientId": "P-101", "status": "STABLE"}
    },
    "Fluxo_Resposta_Emergencia": {
        "url": f"{BASE_URL}/api/context/C5_PatientOK?state=false", # Ou a rota exata de emergência
        "headers": {"X-Target-Goal": "G10_Emergency", "Content-Type": "application/json"},
        "payload": {"patientId": "P-102", "status": "CRITICAL"}
    }
}

ITERATIONS = 100

def evaluate_temporal_cost(scenario_name, config):
    print(f"\nIniciando avaliação: {scenario_name}...")
    latencies = []
    
    # Realiza um 'warm-up' (aquecimento) para compilar o JIT do Java e mapear o Eureka
    try:
        requests.post(config["url"], headers=config["headers"], json=config["payload"], timeout=2.0)
    except:
        pass

    for i in range(ITERATIONS):
        start_time = time.perf_counter()
        try:
            res = requests.post(config["url"], headers=config["headers"], json=config["payload"], timeout=2.0)
            if res.status_code in [200, 201, 202, 204, 404, 405]:
                latency = (time.perf_counter() - start_time) * 1000.0
                latencies.append(latency)
        except Exception:
            pass
        
        # Pausa para isolar o custo temporal (evitar enfileiramento HTTP)
        time.sleep(0.05)
        
    if not latencies:
        print(f"[ERRO] Nenhuma requisição completou o ciclo no {scenario_name}.")
        return

    print(f"--- RESULTADOS: {scenario_name} ---")
    print(f"Amostras válidas : {len(latencies)} execuções completas")
    print(f"Tempo Médio (E2E): {statistics.mean(latencies):.2f} ms")
    print(f"Tempo Mediano    : {statistics.median(latencies):.2f} ms")
    print(f"Tempo Mínimo     : {min(latencies):.2f} ms")
    print(f"Tempo Máximo     : {max(latencies):.2f} ms")

if __name__ == "__main__":
    print("=== AVALIAÇÃO DE DESEMPENHO TEMPORAL DE ARQUITETURA ===")
    for name, config in SCENARIOS.items():
        evaluate_temporal_cost(name, config)
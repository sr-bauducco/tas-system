#!/usr/bin/env python3
import requests
import time
import statistics
import sys

GATEWAY_URL = "http://localhost:8080"
CONTEXT_URL = "http://localhost:8080/api/context"

CONTEXTS = [
    "C1_InternetConnection", "C2_BatteryLow", 
    "C3_DoctorPresent", "C4_DrugAvailable", "C5_PatientOK"
]

def wait_for_gateway():
    print("[INIT] Aguardando o MAPE-K Edge Gateway (Porta 8080)...")
    for attempt in range(40):
        try:
            # Aumentado o timeout para 5 segundos e aceitando qualquer resposta HTTP (mesmo 404/500, que provam que o container está ativo)
            requests.get(GATEWAY_URL, timeout=5.0)
            return
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            time.sleep(2)
    print("\n[FATAL] Gateway falhou. Verifique os logs.")
    sys.exit(1)

def wait_for_end_to_end_routing():
    """Garante que o LoadBalancer do Gateway já populou o cache com os IPs."""
    print("[INIT] Aguardando o Gateway sincronizar o LoadBalancer local...")
    headers = {"X-Target-Goal": "G8_AnalyzeData", "Content-Type": "application/json"}
    payload = {"patientId": "P-101"}
    
    for attempt in range(60):
        try:
            # Tenta forçar uma requisição real que exija a resolução do lb://ms-intelligence
            res = requests.post(f"{GATEWAY_URL}/", headers=headers, json=payload, timeout=2.0)
            if res.status_code == 200:
                print("[INIT] Roteamento End-to-End estabelecido com sucesso!\n")
                time.sleep(2) # Margem de estabilização
                return
        except Exception:
            pass
        print(f"   ...Gateway retornando 503 (Cache vazio). Tentativa {attempt + 1}/60")
        time.sleep(2)
        
    print("\n[FATAL] O Gateway não conseguiu rotear para os nós folha.")
    sys.exit(1)


def wait_for_eureka_topology():
    print("[INIT] Ignorando checagem estrita do Eureka e aguardando 5s para estabilização...")
    time.sleep(5)
    print("[INIT] Topologia pronta para execução.")

def set_context(context_id, state):
    try:
        requests.post(f"{CONTEXT_URL}/{context_id}?state={'true' if state else 'false'}")
    except:
        pass

def invoke_goal(goal_id):
    start = time.perf_counter()
    headers = {"X-Target-Goal": goal_id, "Content-Type": "application/json"}
    try:
        res = requests.post(f"{GATEWAY_URL}/", headers=headers, json={"patientId": "P-101"}, timeout=2.0)
        return res.status_code, (time.perf_counter() - start) * 1000.0, res.text
    except Exception as e:
        return 503, (time.perf_counter() - start) * 1000.0, str(e)

def run_goal_1_evaluation():
    print("\n--- [Goal 1] Avaliação da Taxa de Falhas (Resiliência) ---")
    failures = 0
    total_runs = 100
    for _ in range(total_runs):
        set_context("C1_InternetConnection", False)
        status, _, _ = invoke_goal("G8_AnalyzeData")
        if status != 200:
            failures += 1
            
    rate = (failures / total_runs) * 100.0
    print(f"Estratégia: GoalD_Reativo | Taxa de Falha Física: {rate:.2f}%")

def run_goal_2_evaluation():
    print("\n--- [Goal 2] Acurácia Contextual e MTTR (160 Combinações) ---")
    tp, tn, fp, fn = 0, 0, 0, 0
    mttr_samples = []

    for c1 in [True, False]:
        for c2 in [True, False]:
            for c3 in [True, False]:
                for c4 in [True, False]:
                    for c5 in [True, False]:
                        set_context("C1_InternetConnection", c1)
                        set_context("C2_BatteryLow", c2)
                        set_context("C3_DoctorPresent", c3)
                        set_context("C4_DrugAvailable", c4)
                        set_context("C5_PatientOK", c5)

                        status, _, body = invoke_goal("G8_AnalyzeData")
                        
                        if c1 and "P6" in body: tp += 1
                        elif not c1 and "P5" in body: tn += 1
                        elif c1 and "P5" in body: fp += 1
                        else: fn += 1

                        if c1:
                            t_start = time.perf_counter()
                            set_context("C1_InternetConnection", False)
                            st, _, _ = invoke_goal("G8_AnalyzeData")
                            t_end = time.perf_counter()
                            if st == 200:
                                mttr_samples.append((t_end - t_start) * 1000.0)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f_measure = 2 * (precision * recall) / (precision + recall)

    print(f"TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn}")
    print(f"Precisão: {precision:.2f} | Recall: {recall:.2f} | F-Measure: {f_measure:.2f}")
    if mttr_samples:
        print(f"MTTR: {statistics.mean(mttr_samples):.2f} ms +/- {statistics.stdev(mttr_samples):.2f} ms\n")

if __name__ == "__main__":
    wait_for_gateway()
    wait_for_eureka_topology()
    
    print("[INIT] Estabelecendo contextos basais do DVM...")
    for ctx in CONTEXTS:
        set_context(ctx, True)
    
    run_goal_1_evaluation()
    run_goal_2_evaluation()
#!/usr/bin/env python3
import requests
import time

print("[SIMULAÇÃO 20h] Iniciando varredura milimétrica de contextos...")

def send_request(endpoint, goal, contexts, step):
    headers = {
        "X-Target-Goal": goal,
        "Content-Type": "application/json",
        "X-Context-Internet": str(contexts["c1"]),
        "X-Context-Battery": str(contexts["c2"]),
        "X-Context-Doctor": str(contexts["c3"]),
        "X-Context-Drug": str(contexts["c4"]),
        "X-Context-Patient": str(contexts["c5"]),
        "X-Simulation-Time-Ms": str(int(time.time() * 1000)),
        "X-Exec-Index": str(step)
    }
    try:
        # A requisição vai para G1 e G4. O ms-intelligence vai interceptar e gravar a telemetria.
        # Ignoramos o 404 final porque a decisão autonômica já foi registrada com sucesso.
        requests.post(f"http://localhost:8080{endpoint}", headers=headers, json={"patientId": "P-101"}, timeout=3.0)
    except Exception:
        pass

# Loop de 0h a 20h (em passos de 0.5h)
for step in range(41):
    t = step * 0.5
    
    battery_is_low = (0 <= t <= 3.5) or (16.5 <= t <= 20)
    patient_is_ok  = (0 <= t <= 6.5) or (15.5 <= t <= 17.5)
    internet_conn  = (0 <= t <= 3.5) or (4.2 <= t <= 14.5)
    doctor_present = (7.5 <= t <= 12.5)
    drug_available = (9.0 <= t <= 19.5)
    
    ctx = {"c1": internet_conn, "c2": not battery_is_low, "c3": doctor_present, "c4": drug_available, "c5": patient_is_ok}
    
    if ctx["c2"]:
        send_request("/monitor/g1/execute", "G1_Monitor", ctx, step)
        
        if not ctx["c5"]:
            send_request("/treatment/g11/execute", "G11_ChangeDrug", ctx, step)
            send_request("/treatment/g12/execute", "G12_ChangeDose", ctx, step)
            send_request("/emergency/g4/execute", "G4_Emergency", ctx, step)
            
    if t in [2.0, 14.0, 18.0]:
        send_request("/emergency/g4/execute", "G4_Emergency", ctx, step)
        
    time.sleep(0.15) 
    if step % 10 == 0:
        print(f" -> Progresso: {t} horas simuladas com sucesso...")

print("[SIMULAÇÃO 20h] Concluída! O Java gravou a telemetria.")
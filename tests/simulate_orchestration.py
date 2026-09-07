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
TELEMETRY_FILE = os.path.join(ROOT_DIR, "bundle_activations.jsonl")

# MAPA COMPLETO DE GOALS DO SISTEMA (Adicione ou ajuste conforme seus microsserviços)
ALL_GOALS = [
    {"id": "G1", "name": "Monitoramento", "url": "http://localhost:8080/monitor/g1/execute", "header": "G1_Monitor"},
    {"id": "G3", "name": "AnaliseContexto", "url": "http://localhost:8080/analysis/g3/execute", "header": "G3_Analysis"},
    {"id": "G4", "name": "EmergenciaAlarm", "url": "http://localhost:8080/emergency/g4/execute", "header": "G4_Emergency"},
    {"id": "G11", "name": "TratamentoDrug", "url": "http://localhost:8080/treatment/g11/execute", "header": "G11_Treatment"},
    {"id": "G12", "name": "TratamentoDose", "url": "http://localhost:8080/treatment/g12/execute", "header": "G12_Treatment"}
]

def clear_old_telemetry():
    if os.path.exists(TELEMETRY_FILE):
        try:
            open(TELEMETRY_FILE, 'w').close()
        except PermissionError:
            print("[AVISO] Sem permissão para limpar o JSONL. Usando 'sudo'.")

def run_full_hierarchy_simulation(ciclos=60):
    clear_old_telemetry()
    print(f"[MAPE-K FULL TEST] Iniciando varredura de todos os objetivos ({ciclos} ciclos)...")
    
    client_results = []
    
    for step in range(1, ciclos + 1):
        req_start = int(time.time() * 1000)
        
        # Perturbações ambientais caóticas
        ctx = {
            "c1-internet": random.choices([True, False], weights=[75, 25])[0],
            "c2-battery": random.choices([True, False], weights=[60, 40])[0],
            "c3-doctor": random.choices([True, False], weights=[50, 50])[0],
            "c4-drug": random.choices([True, False], weights=[70, 30])[0],
            "c5-patientok": random.choices([True, False], weights=[80, 20])[0]
        }
        
        # Seleciona ciclicamente ou aleatoriamente um Goal da árvore completa
        target_goal = random.choice(ALL_GOALS)
        
        headers = {
            "X-Target-Goal": target_goal["header"],
            "Content-Type": "application/json",
            "X-Context-Internet": str(ctx["c1-internet"]),
            "X-Context-Battery": str(ctx["c2-battery"]),
            "X-Context-Doctor": str(ctx["c3-doctor"]),
            "X-Context-Drug": str(ctx["c4-drug"]),
            "X-Context-Patient": str(ctx["c5-patientok"]),
            "X-Simulation-Time-Ms": str(req_start),
            "X-Scenario": target_goal["id"],
            "X-Exec-Index": str(step)
        }
        
        status_code = 500
        try:
            res = requests.post(target_goal["url"], headers=headers, json={"patientId": "P-101"}, timeout=2.0)
            status_code = res.status_code
        except Exception:
            pass
            
        req_end = int(time.time() * 1000)
        
        client_results.append({
            "goal_id": target_goal["id"], "execIndex": step,
            "start": req_start, "end": req_end, "type": f"http-{status_code}"
        })
        
        time.sleep(0.15)

    return client_results

def analyze_telemetry_report(client_results):
    server_results = []
    linhas_lidas = 0

    if os.path.exists(TELEMETRY_FILE):
        with open(TELEMETRY_FILE, 'r') as f:
            for line in f:
                if not line.strip(): continue
                linhas_lidas += 1
                try:
                    data = json.loads(line)
                    endpoint = data.get("endpoint", "")
                    
                    # Mapeia o bundle executado de volta para o Goal correspondente
                    matched_id = "Desconhecido"
                    for g in ALL_GOALS:
                        if g["url"].replace("http://localhost:8080", "") in endpoint:
                            matched_id = g["id"]
                            break

                    server_results.append({
                        "goal_id": matched_id,
                        "bundle": data.get("bundle", "unknown"),
                        "duration_ms": data.get("durationMs", 0)
                    })
                except Exception:
                    pass

    print("\n" + "="*85)
    print(" 🚀 RELATÓRIO DE VALIDAÇÃO DA HIERARQUIA MAPE-K (G0 -> FIM) ")
    print("="*85)
    
    client_df = pd.DataFrame(client_results)
    server_df = pd.DataFrame(server_results)
    
    print(f"📊 Total de Registros de Telemetria Analisados: {linhas_lidas}")
    print(f"🌐 Distribuição de Status HTTP do Gateway: {client_df['type'].value_counts().to_dict()}")
    print("-" * 85)

    # Relatório detalhado por Objetivo (Goal)
    for goal in ALL_GOALS:
        gid = goal["id"]
        gname = goal["name"]
        gurl = goal["url"]
        
        print(f"\n🎯 OBJETIVO [{gid}] - {gname.upper()} ({gurl})")
        
        # Quantas vezes foi solicitado vs Executado no backend
        solicitacoes = len(client_df[client_df['goal_id'] == gid])
        execucoes_backend = server_df[server_df['goal_id'] == gid]
        
        print(f"   📥 Requisições Disparadas: {solicitacoes}")
        
        if execucoes_backend.empty:
            print("   -> ⚠️ Nenhuma ativação de bundle registrada (Verifique se o container está ativo ou se ocorreu HTTP 404/500).")
        else:
            stats = execucoes_backend.groupby('bundle').agg(
                ativacoes=('bundle', 'count'),
                tempo_total=('duration_ms', 'sum'),
                tempo_medio=('duration_ms', 'mean')
            ).reset_index()
            
            for _, row in stats.iterrows():
                print(f"   ✅ Plano/Bundle Ativado: [{row['bundle']:22}] | Acionamentos: {row['ativacoes']:<3} | CPU Total: {row['tempo_total']:6.1f}ms | Média: {row['tempo_medio']:.1f}ms")

    print("\n" + "="*85)

if __name__ == "__main__":
    data = run_full_hierarchy_simulation(ciclos=75)
    analyze_telemetry_report(data)
#!/usr/bin/env python3
import asyncio
import aiohttp
import time
import random
import pandas as pd
import matplotlib.pyplot as plt
import os

# ==========================================
# CONFIGURAÇÕES DO TESTE
# ==========================================
GATEWAY_URL = "http://localhost:8080/vitals" # Ajuste para a rota de entrada do seu API Gateway
RESULTS_CSV = "results/elasticity_results.csv"
RESULTS_CHART = "results/elasticity_chart.png"

# Fases do Teste: (Duração em segundos, Requisições por segundo)
PHASES = [
    (60, 50),   # Fase 1: Aquecimento (50 req/s por 1 minuto)
    (60, 150),  # Fase 2: Aumento de Carga (150 req/s por 1 minuto)
    (120, 300)  # Fase 3: Estresse Máximo (300 req/s por 2 minutos) -> HORA DE ESCALAR!
]

# ==========================================
# GERADOR DE CAOS CONTEXTUAL
# ==========================================
def generate_random_headers():
    """Gera contextos aleatórios para forçar o recalculo de rotas do GoalD/MAPE-K."""
    return {
        "X-Context-Internet": random.choice(["true", "false"]),
        "X-Context-Criticality": random.choice(["low", "medium", "high"]),
        "X-Context-Doctor": random.choice(["true", "false"]),
        "X-Context-Battery": random.choice(["normal", "low"])
    }

# ==========================================
# MOTOR ASSÍNCRONO DE REQUISIÇÕES
# ==========================================
async def fetch(session, url, start_time_global):
    headers = generate_random_headers()
    start_req = time.time()
    
    try:
        async with session.get(url, headers=headers, timeout=5) as response:
            await response.read()
            status = response.status
    except Exception:
        status = 500 # Falha de conexão ou timeout
        
    end_req = time.time()
    
    return {
        "timestamp_relativo": start_req - start_time_global,
        "status": status,
        "latencia_ms": (end_req - start_req) * 1000,
        "contexto": str(headers)
    }

async def run_phase(phase_duration, req_per_sec, session, start_time_global, results):
    """Executa uma fase do teste mantendo a taxa de requisições desejada."""
    print(f"🚀 Iniciando fase: {req_per_sec} req/s por {phase_duration} segundos...")
    phase_start = time.time()
    
    while time.time() - phase_start < phase_duration:
        loop_start = time.time()
        
        # Dispara as requisições do segundo atual simultaneamente
        tasks = [fetch(session, GATEWAY_URL, start_time_global) for _ in range(req_per_sec)]
        responses = await asyncio.gather(*tasks)
        results.extend(responses)
        
        # Aguarda o restante do segundo para manter a precisão do req/s
        elapsed = time.time() - loop_start
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)

async def main():
    results = []
    start_time_global = time.time()
    
    # Usa um pool de conexões otimizado para não gargalar no lado do cliente
    connector = aiohttp.TCPConnector(limit=0) 
    async with aiohttp.ClientSession(connector=connector) as session:
        for duration, rps in PHASES:
            await run_phase(duration, rps, session, start_time_global, results)
            
    print("\n✅ Teste de carga finalizado. Processando dados...")
    
    # ==========================================
    # ANÁLISE E GERAÇÃO DE GRÁFICOS
    # ==========================================
    os.makedirs("results", exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_CSV, index=False)
    
    # Calcula a média móvel de latência (janela de 5 segundos para suavizar o gráfico)
    df['tempo_segundos'] = df['timestamp_relativo'].astype(int)
    media_por_segundo = df.groupby('tempo_segundos')['latencia_ms'].mean().reset_index()
    media_por_segundo['media_movel'] = media_por_segundo['latencia_ms'].rolling(window=5, min_periods=1).mean()
    
    # Renderiza o Gráfico
    plt.figure(figsize=(12, 6))
    plt.plot(media_por_segundo['tempo_segundos'], media_por_segundo['media_movel'], color='#d9534f', linewidth=2)
    
    # Marcações visuais das fases
    plt.axvline(x=60, color='gray', linestyle='--', label='150 req/s')
    plt.axvline(x=120, color='gray', linestyle='-.', label='300 req/s (Pico)')
    
    plt.title('Teste de Elasticidade e Resiliência (Spring Boot / GoalD)', fontsize=14, fontweight='bold')
    plt.xlabel('Tempo de Execução (Segundos)', fontsize=12)
    plt.ylabel('Latência Média (ms)', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(RESULTS_CHART, dpi=300)
    print(f"📊 Gráfico exportado com sucesso para: {RESULTS_CHART}")
    print(f"📈 Dados brutos salvos em: {RESULTS_CSV}")

if __name__ == "__main__":
    asyncio.run(main())
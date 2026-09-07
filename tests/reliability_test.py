#!/usr/bin/env python3
import asyncio
import aiohttp
import time
import random
import pandas as pd
import matplotlib.pyplot as plt
import os

# ==========================================
# CONFIGURAÇÕES DO TESTE DE CONFIABILIDADE
# ==========================================
# Lista com rotas válidas da sua API Gateway
URLS = [
    "http://localhost:8080/monitor/g1/execute",    # Esta rota vai sobreviver
    "http://localhost:8080/treatment/g11/execute"  # Esta rota nós vamos matar
]

RESULTS_CSV = "results/reliability_results.csv"
RESULTS_CHART = "results/reliability_chart.png"

DURATION_SECONDS = 90
REQ_PER_SECOND = 100 # Carga constante dividida entre os serviços

def generate_random_headers():
    """Gera contextos aleatórios."""
    return {
        "X-Context-Internet": random.choice(["true", "false"]),
        "X-Context-Criticality": random.choice(["low", "medium", "high"])
    }

async def fetch(session, start_time_global):
    url = random.choice(URLS) # Sorteia qual rota vai receber a requisição
    headers = generate_random_headers()
    start_req = time.time()
    
    try:
        async with session.get(url, headers=headers, timeout=3) as response:
            await response.read()
            status = response.status
    except Exception:
        status = 503 # Service Unavailable (Caiu)
        
    return {
        "tempo_segundos": int(start_req - start_time_global),
        "status": status
    }

async def main():
    results = []
    start_time_global = time.time()
    
    print(f"🔥 Iniciando Teste de Confiabilidade: {REQ_PER_SECOND} req/s por {DURATION_SECONDS} segundos.")
    print("⚠️  ATENÇÃO: Vá para o Terminal 2 e derrube o 'ms-treatment' no meio do teste!")
    
    connector = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=connector) as session:
        for _ in range(DURATION_SECONDS):
            loop_start = time.time()
            
            # Aqui estava o erro! Agora ele não usa mais a variável velha.
            tasks = [fetch(session, start_time_global) for _ in range(REQ_PER_SECOND)]
            responses = await asyncio.gather(*tasks)
            results.extend(responses)
            
            elapsed = time.time() - loop_start
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)
                
    print("\n✅ Teste finalizado. Gerando provas visuais...")

    # ==========================================
    # RENDERIZAÇÃO DO GRÁFICO DE CONFIABILIDADE
    # ==========================================
    os.makedirs("results", exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_CSV, index=False)
    
    df_grouped = df.groupby(['tempo_segundos', 'status']).size().unstack(fill_value=0)
    
    sucesso_cols = [c for c in df_grouped.columns if c < 400]
    erro_cols = [c for c in df_grouped.columns if c >= 400]
    
    df_grouped['Sucesso'] = df_grouped[sucesso_cols].sum(axis=1) if sucesso_cols else 0
    df_grouped['Erro'] = df_grouped[erro_cols].sum(axis=1) if erro_cols else 0

    plt.figure(figsize=(12, 6))
    plt.plot(df_grouped.index, df_grouped['Sucesso'], color='#5cb85c', linewidth=2.5, label='Disponível (HTTP 200)')
    plt.plot(df_grouped.index, df_grouped['Erro'], color='#d9534f', linewidth=2.5, label='Falha Isolada (HTTP 500/503)')
    
    plt.fill_between(df_grouped.index, df_grouped['Sucesso'], color='#5cb85c', alpha=0.2)
    plt.fill_between(df_grouped.index, df_grouped['Erro'], color='#d9534f', alpha=0.2)

    plt.title('Isolamento de Falhas e Continuidade de Serviço (Chaos Test)', fontsize=14, fontweight='bold')
    plt.xlabel('Tempo de Execução (Segundos)', fontsize=12)
    plt.ylabel('Requisições por Segundo', fontsize=12)
    plt.legend(loc='upper right')
    plt.grid(True, linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(RESULTS_CHART, dpi=300)
    print(f"📊 Gráfico salvo em: {RESULTS_CHART}")

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
import asyncio
import aiohttp
import time
import random
import pandas as pd
import matplotlib.pyplot as plt
import os

RESULTS_CSV = "results/reliability_results.csv"
RESULTS_CHART = "results/reliability_chart_final.png"

DURATION_SECONDS = 90
REQ_PER_SECOND = 100 

def generate_random_headers():
    return {
        "X-Context-Internet": random.choice(["true", "false"]),
        "X-Context-Criticality": random.choice(["low", "medium", "high"])
    }

async def fetch(session, start_time_global):
    # SORTEIO MÁGICO: 50% das requisições vão pro Monitor, 50% pro Treatment
    is_monitor = random.random() < 0.5
    
    if is_monitor:
        # Passa pelo Gateway tranquilamente (Vai gerar a linha Verde)
        url = "http://localhost:8080/monitor/g1/execute" 
    else:
        # Bate DIRETO na porta física do Treatment (Vai gerar a linha Vermelha quando for morto)
        url = "http://localhost:8081/treatment/g11/execute"

    headers = generate_random_headers()
    start_req = time.time()
    
    try:
        async with session.get(url, headers=headers, timeout=2) as response:
            await response.read()
            status = response.status
    except Exception:
        status = 503 # A porta 8081 caiu! Registra como erro fatal.
        
    return {
        "tempo_segundos": int(start_req - start_time_global),
        "status": status,
        "alvo": "monitor" if is_monitor else "treatment"
    }

async def main():
    results = []
    start_time_global = time.time()
    
    print(f"🔥 Iniciando Caos Controlado: {REQ_PER_SECOND} req/s por {DURATION_SECONDS} segundos.")
    print("⚠️  ATENÇÃO: Aos 30 segundos, mate o serviço com: docker stop ms-treatment")
    
    connector = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=connector) as session:
        for _ in range(DURATION_SECONDS):
            loop_start = time.time()
            
            tasks = [fetch(session, start_time_global) for _ in range(REQ_PER_SECOND)]
            responses = await asyncio.gather(*tasks)
            results.extend(responses)
            
            elapsed = time.time() - loop_start
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)
                
    print("\n✅ Teste finalizado. Desenhando o gráfico...")

    os.makedirs("results", exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_CSV, index=False)
    
    # Agrupa por segundo e por status HTTP
    df_grouped = df.groupby(['tempo_segundos', 'status']).size().unstack(fill_value=0)
    
    sucesso_cols = [c for c in df_grouped.columns if c < 400]
    erro_cols = [c for c in df_grouped.columns if c >= 400]
    
    df_grouped['Sucesso'] = df_grouped[sucesso_cols].sum(axis=1) if sucesso_cols else 0
    df_grouped['Erro'] = df_grouped[erro_cols].sum(axis=1) if erro_cols else 0

    plt.figure(figsize=(12, 6))
    plt.plot(df_grouped.index, df_grouped['Sucesso'], color='#5cb85c', linewidth=2.5, label='Disponível e Seguro (HTTP 200)')
    plt.plot(df_grouped.index, df_grouped['Erro'], color='#d9534f', linewidth=2.5, label='Falha Fatal Isolada (HTTP 503)')
    
    plt.fill_between(df_grouped.index, df_grouped['Sucesso'], color='#5cb85c', alpha=0.2)
    plt.fill_between(df_grouped.index, df_grouped['Erro'], color='#d9534f', alpha=0.2)

    plt.title('Isolamento de Falhas e Continuidade de Serviço (Shared-Nothing)', fontsize=14, fontweight='bold')
    plt.xlabel('Tempo de Execução (Segundos)', fontsize=12)
    plt.ylabel('Requisições por Segundo', fontsize=12)
    plt.legend(loc='center right')
    plt.grid(True, linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(RESULTS_CHART, dpi=300)
    print(f"📊 Gráfico salvo como: {RESULTS_CHART}")

if __name__ == "__main__":
    asyncio.run(main())
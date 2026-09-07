#!/usr/bin/env python3

import pandas as pd
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR

RESULTS_CSV = os.path.join(ROOT_DIR, "results", "random_msgoald_results.csv")
OUTPUT_CORRELATION = os.path.join(ROOT_DIR, "results", "context_route_correlation.csv")

def analyze_correlation():
    if not os.path.exists(RESULTS_CSV):
        print(f"[ERRO] Arquivo de resultados não encontrado em {RESULTS_CSV}")
        return

    df = pd.read_csv(RESULTS_CSV)
    
    # Separa os registros de contexto e os registros de rotas/bundles/requisições
    contexts_df = df[df['type'] == 'context']
    requests_df = df[df['type'].str.startswith('http') | (df['type'] == 'bundle')]

    if requests_df.empty or contexts_df.empty:
        print("[AVISO] Dados insuficientes para correlação no CSV atual.")
        return

    correlations = []

    # Para cada execução/requisição, encontra quais contextos estavam ativos na mesma janela de tempo
    for _, req in requests_df.iterrows():
        r_start = req['start']
        r_end = req['end']
        
        # Filtra contextos ativos durante a janela [r_start, r_end] ou no mesmo execIndex
        active_ctxs = contexts_df[
            (contexts_df['execIndex'] == req['execIndex']) & 
            (contexts_df['type'] == 'context')
        ]['label'].tolist()

        correlations.append({
            "execIndex": req['execIndex'],
            "route_label": req['label'],
            "request_type": req['type'],
            "start_ms": r_start,
            "end_ms": r_end,
            "active_contexts": ", ".join(active_ctxs)
        })

    corr_df = pd.DataFrame(correlations)
    corr_df.to_csv(OUTPUT_CORRELATION, index=False)
    
    print(f"[SUCESSO] Tabela de correlação salva em: {OUTPUT_CORRELATION}")
    print("\nAmostra da Correlação Contexto x Rota:")
    print(corr_df[['execIndex', 'route_label', 'request_type', 'active_contexts']].head(10).to_string())

if __name__ == "__main__":
    analyze_correlation()
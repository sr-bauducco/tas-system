#!/usr/bin/env python3
import pandas as pd
import os

# Configuração de diretórios
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR
RESULTS_CSV = os.path.join(ROOT_DIR, "results", "msgoald_results.csv")

def map_plans_to_scenarios():
    if not os.path.exists(RESULTS_CSV):
        print(f"[ERRO] O arquivo {RESULTS_CSV} não foi encontrado.")
        return

    df = pd.read_csv(RESULTS_CSV)
    
    # Agrupa todos os eventos que aconteceram na mesma requisição/ciclo (mesmo execIndex)
    grouped = df.groupby('execIndex')
    
    scenario_mapping = {}

    for _, group in grouped:
        # Filtra os contextos ativos (ignorando os que começam com '!' para simplificar a leitura, 
        # ou mantendo todos para ter a assinatura exata do cenário)
        contexts = group[group['type'] == 'context']['label'].tolist()
        
        # Filtra os contextos positivos (ativos) para criar o nome do cenário
        active_contexts = sorted([ctx for ctx in contexts if not ctx.startswith('!')])
        scenario_signature = " + ".join(active_contexts) if active_contexts else "Nenhum Contexto Ativo (Pior Cenário)"
        
        # Filtra os bundles (planos) que foram executados nesse ciclo
        bundles = group[group['type'] == 'bundle']['label'].unique().tolist()
        
        if scenario_signature not in scenario_mapping:
            scenario_mapping[scenario_signature] = set()
            
        scenario_mapping[scenario_signature].update(bundles)

    # Exibição do Relatório
    print("="*80)
    print(" MAPEAMENTO DE ADAPTAÇÃO: CENÁRIOS vs PLANOS ACIONADOS")
    print("="*80)
    
    for scenario, plans in sorted(scenario_mapping.items()):
        print(f"\n[CENÁRIO AMBIENTAL]")
        print(f"Contextos Ativos : {scenario}")
        
        if plans:
            plan_str = "\n  - ".join(sorted(list(plans)))
            print(f"Planos Acionados :\n  - {plan_str}")
        else:
            print(f"Planos Acionados : [Nenhum plano registrou telemetria neste ciclo]")
            
    print("\n" + "="*80)

if __name__ == "__main__":
    map_plans_to_scenarios()    
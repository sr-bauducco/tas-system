#!/usr/bin/env python3
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "tests" else SCRIPT_DIR
INPUT_CSV = os.path.join(ROOT_DIR, "results", "msgoald_24h_results.csv")

def run_correlation_analysis():
    if not os.path.exists(INPUT_CSV):
        print(f"[ERRO] Arquivo não encontrado: {INPUT_CSV}. Rode a simulação 24h primeiro.")
        return

    df = pd.read_csv(INPUT_CSV)
    
    contexts_df = df[df['type'] == 'context']
    bundles_df = df[df['type'] == 'bundle']
    
    if bundles_df.empty:
        print("[AVISO] Nenhum bundle registrou execução no CSV.")
        return

    # 1. Cria a assinatura do ambiente para cada ciclo (execIndex)
    context_map = {}
    for exec_idx, group in contexts_df.groupby('execIndex'):
        active, inactive = [], []
        for _, row in group.iterrows():
            lbl = str(row['label'])
            if lbl.startswith('!'):
                inactive.append(lbl.replace('!', 'Sem '))
            else:
                # Ex: "c1-internet" -> "Com Internet"
                clean_name = lbl.split('-')[1].capitalize() if '-' in lbl else lbl
                active.append(f"Com {clean_name}")
                
        # Formata: "Com Internet, Com Doctor | Sem Battery"
        sig = f"[{', '.join(active)}] | [{', '.join(inactive)}]"
        context_map[exec_idx] = sig

    # 2. Associa cada bundle executado ao cenário em que ocorreu
    analysis_data = []
    for _, bundle in bundles_df.iterrows():
        exec_idx = bundle['execIndex']
        duration = bundle['end'] - bundle['start']
        scenario_sig = context_map.get(exec_idx, "Contexto Desconhecido")
        
        analysis_data.append({
            'Microsservico': bundle['label'],
            'Cenario_Ambiental': scenario_sig,
            'Duracao_ms': duration
        })

    analysis_df = pd.DataFrame(analysis_data)
    
    # 3. Agrupa as estatísticas
    summary = analysis_df.groupby(['Microsservico', 'Cenario_Ambiental']).agg(
        Chamadas=('Duracao_ms', 'count'),
        Tempo_Total_ms=('Duracao_ms', 'sum'),
        Tempo_Medio_ms=('Duracao_ms', 'mean')
    ).reset_index()

    # 4. Exibição Formatada do Relatório
    print("="*100)
    print(" 🔍 CORRELAÇÃO: COMPONENTES ACIONADOS vs ESTADO DO AMBIENTE (Simulação 24h)")
    print("="*100)
    
    for ms_name, group in summary.groupby('Microsservico'):
        print(f"\n⚙️  ROTA / PLANO: {ms_name.upper()}")
        print("-" * 100)
        for _, row in group.iterrows():
            print(f"🌍 Condições Ativas: {row['Cenario_Ambiental']}")
            print(f"⏱️  Acionamentos  : {row['Chamadas']:<4} vezes | CPU Time Total: {row['Tempo_Total_ms']:6.1f} ms | Média: {row['Tempo_Medio_ms']:.1f} ms/chamada")
            print("-" * 100)

if __name__ == "__main__":
    run_correlation_analysis()
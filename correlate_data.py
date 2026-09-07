#!/usr/bin/env python3

import pandas as pd
import json
from datetime import datetime
import os

# 1. Carrega os dados do Backend (JSONL)
backend_data = []
with open('bundle_activations.jsonl', 'r') as f:
    for line in f:
        if not line.strip(): continue
        data = json.loads(line)
        
        # Converte o Timestamp do Java para milissegundos (Unix Epoch)
        dt_obj = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        end_ms = int(dt_obj.timestamp() * 1000)
        
        backend_data.append({
            'timestamp_ms': end_ms,
            'bundle': data['bundle'],
            'endpoint': data['endpoint'],
            'duration': data['durationMs']
        })

df_backend = pd.DataFrame(backend_data)
# Ordena pelo tempo para o cruzamento funcionar
df_backend = df_backend.sort_values('timestamp_ms') 

# 2. Carrega os dados do Cliente/Simulador (CSV)
# Este é o CSV gerado pelo seu script simulate_all_goals.py
df_client = pd.read_csv('results/msgoald_results.csv')

# Filtramos apenas as linhas que representam o início de uma requisição HTTP
df_requests = df_client[df_client['type'].str.contains('http')].copy()
df_requests = df_requests.sort_values('end') # O 'end' do python é próximo ao 'timestamp' do Java

# 3. O Cruzamento (Join Temporal)
# Junta o dado do backend com a requisição do cliente que ocorreu no tempo mais próximo
df_merged = pd.merge_asof(
    df_backend, 
    df_requests, 
    left_on='timestamp_ms', 
    right_on='end', 
    direction='nearest',
    tolerance=500 # Aceita uma diferença de até 500ms entre o relógio do Python e do Java
)

# 4. Análise de Causa e Efeito
print("="*80)
print(" 🔗 RELAÇÃO: CONTEXTO vs BUNDLE ACIONADO ")
print("="*80)

# Agora podemos agrupar os dados para ver qual bundle roda em cada cenário
for endpoint, group in df_merged.groupby('endpoint'):
    print(f"\n📍 Rota/Endpoint: {endpoint}")
    
    # Conta quais bundles foram chamados para este endpoint
    bundle_counts = group['bundle'].value_counts()
    for bundle_name, count in bundle_counts.items():
        print(f"   ⚙️ Acionou o Bundle: [{bundle_name}] {count} vezes")
        
        # Exemplo de como você extrairia o contexto (se as colunas de contexto estiverem no CSV)
        # print(f"       -> Ambiente provável (Ciclo {group['execIndex'].iloc[0]})")

print("\n" + "="*80)
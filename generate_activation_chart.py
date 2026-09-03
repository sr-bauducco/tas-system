import json
import pandas as pd

data = []
# Lê o arquivo gerado pelo volume do Docker
with open('results/bundle_activations.jsonl', 'r') as file:
    for line in file:
        if line.strip(): # Ignora linhas em branco
            data.append(json.loads(line.strip()))

df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Exemplo de agrupamento de tempo de execução por componente
print(df.groupby('bundle')['durationMs'].describe())
#!/usr/bin/env python3

import csv
import pandas as pd

data = []
# Lê o arquivo gerado pelo volume do Docker
with open('results/msgoald_benchmark_results.csv', 'r') as file:
    for line in file:
        if line.strip(): # Ignora linhas em branco
            data.append(csv.DictReader(line.strip()))

df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Exemplo de agrupamento de tempo de execução por componente
print(df.groupby('bundle')['durationMs'].describe())
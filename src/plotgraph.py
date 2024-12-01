# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import re

def parse_data(data):
    results = []

    for block in data.strip().split("\n\n"):
        lines = block.split("\n")
        
        c_match = re.search(r"C\s*=\s*(\d+)", lines[0])
        if c_match:
            C = int(c_match.group(1))
        else:
            continue

        throughput = None
        latency = None

        for line in lines[1:]:
            if "Vazão total" in line or "Média vazão total" in line:
                throughput = float(re.search(r"[0-9]+\.[0-9]+", line).group())
            elif "latência total" in line:
                latency = float(re.search(r"[0-9]+\.[0-9]+", line).group())

        if throughput is not None and latency is not None:
            results.append((C, throughput, latency))

    return results

def plot_results(results):
    plt.figure(figsize=(10, 6))

    # sort
    results = sorted(results, key=lambda x: x[0])

    # extract values
    throughput_values = [r[1] for r in results]
    latency_values = [r[2] for r in results]
    C_values = [r[0] for r in results]

    # plot line
    plt.plot(throughput_values, latency_values, marker='o', linestyle='-', label=u"Vazão x Latência")


    for C, throughput, latency in results:
        plt.text(throughput, latency, u"C = {}".format(C), fontsize=10, ha='right')

    plt.title(u"Vazão x Latência")
    plt.xlabel(u"Vazão (requisições por segundo)")
    plt.ylabel(u"Latência (segundos)")
    plt.legend()
    plt.grid()
    plt.show()


data = """
C = 5 R =1
Tempo total do processo: 0.56 segundos
Vazão total: 9.01 requisições por segundo
Média latência total: 0.11 requisições por segundo

C = 50 R = 1
Tempo total do processo: 10.81 segundos
Média vazão total: 60.85 requisições por segundo
Média latência total: 4.84 requisições por segundo

C = 100 R = 1
Tempo total do processo: 10.81 segundos
Média vazão total: 100.22 requisições por segundo
Média latência total: 10.32 requisições por segundo

C = 150 R = 1
Tempo total do processo: 30.38 segundos
Vazão total: 64.72 requisições por segundo
Média latência total: 17.80 segundos

C = 200 R = 1
Tempo total do processo: 25.28 segundos
Vazão total: 100.81 requisições por segundo
Média latência total: 13.17 segundos (Lider 0 falhou e Lider 1 Continuou)
"""

results = parse_data(data)
plot_results(results)

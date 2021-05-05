import sys
import json
import optimization
import most_connected_node
import highest_eccentricity_node
import highest_load_node
import functions
import math

def average(policy, index):
    sum = 0
    counter = 0
    if index == 0:
        index = "num_cont"
    elif index == 1:
        index = "avg_load"
    elif index == 2:
        index = "avg_latency"
    for i in range(1, REPETITIONS):
        counter += 1
        sum += result[dataset_name][t][i][policy][t][index]
    return sum / counter

def deviation(policy, index, average):
    sum = 0
    counter = 0
    if index == 0:
        index = "num_cont"
    elif index == 1:
        index = "avg_load"
    elif index == 2:
        index = "avg_latency"
    for i in range(1, REPETITIONS):
        counter += 1
        sum += (result[dataset_name][t][i][policy][t][index] - average) * (result[dataset_name][t][i][policy][t][index] - average)
    sum /= counter
    return math.sqrt(sum)

if __name__ == "__main__":
    LMAX = 0.25
    CMAX = 20000
    datasets = {"nsfnet": 14, "geant2": 24}

    try:
        input = sys.argv[1]
        output = sys.argv[1] + "_results"
        REPETITIONS = int(sys.argv[2]) + 1
    except IndexError:
        print("Pass the name of the output file and the number of repetitions as argument")
        sys.exit()

    result = {}
    for name, size in datasets.items():
        dataset_name = name
        result[dataset_name] = {}
        N = size
        T = 5
        f = open(dataset_name + ".txt", "r")
        data = f.readline().split(",")
        f.close()
        graph = open(dataset_name + "_graph.txt", "r")

        for t in range(1, T+6, 5):
            if t > 1:
                t -= 1
            if t > N:
                   break
            result[dataset_name][t] = {}
            T = t

            for u in range(1, REPETITIONS):
                result[dataset_name][t][u] = {}
                X = functions.random_migration(T, N)

                graph.seek(0)
                G = functions.G_from_dataset(graph, N)
                L = functions.L_from_dataset(data, N)
                K = functions.K_from_dataset(data, N, G)

                # Optimization
                print("[T =", str(t) + "]" + "[" + str(u) + "]" + "[" + dataset_name + "]" + "[Optimization]")
                otimizacao = optimization.solve(N, T, L, LMAX, CMAX, K, X, G)
                while otimizacao == "nao tem solucao":
                    print("Tempo limite excedido. Tentando novamente")
                    X = functions.random_migration(T, N)
                    otimizacao = optimization.solve(N, T, L, LMAX, CMAX, K, X, G)

                # Most connected
                print("[T =", str(t) + "]" + "[" + str(u) + "]" + "[" + dataset_name + "]" + "[Most connected]")
                conectado = most_connected_node.solve(N, T, LMAX, CMAX, data, G, L, K, X)

                # Highest eccentricity
                print("[T =", str(t) + "]" + "[" + str(u) + "]" + "[" + dataset_name + "]" + "[Highest eccentricity]")
                diametro = highest_eccentricity_node.solve(N, T, LMAX, CMAX, data, G, L, K, X)

                # Highest load
                print("[T =", str(t) + "]" + "[" + str(u) + "]" + "[" + dataset_name + "]" + "[Highest load]")
                fluxo = highest_load_node.solve(N, T, LMAX, CMAX, data, G, L, K, X)

                result[dataset_name][t][u]["Scenario"] = {}
                result[dataset_name][t][u]["Scenario"]["sdn"] = X
                result[dataset_name][t][u]["Scenario"]["parameters"] = [LMAX, CMAX]
                result[dataset_name][t][u]["Optimization"] = otimizacao
                result[dataset_name][t][u]["Most connected"] = conectado
                result[dataset_name][t][u]["Highest eccentricity"] = diametro
                result[dataset_name][t][u]["Highest load"] = fluxo

            # Average number of controllers
            result[dataset_name][t]["Average"] = {}
            result[dataset_name][t]["Average"]["Optimization"] = average("Optimization", 0)
            result[dataset_name][t]["Average"]["Most connected"] = average("Most connected", 0)
            result[dataset_name][t]["Average"]["Highest eccentricity"] = average("Highest eccentricity", 0)
            result[dataset_name][t]["Average"]["Highest load"] = average("Highest load", 0)

            # Number of controllers standard deviation 
            result[dataset_name][t]["Desvio"] = {}
            result[dataset_name][t]["Desvio"]["Optimization"] = deviation("Optimization", 0, result[dataset_name][t]["Average"]["Optimization"])
            result[dataset_name][t]["Desvio"]["Most connected"] = deviation("Most connected", 0, result[dataset_name][t]["Average"]["Most connected"])
            result[dataset_name][t]["Desvio"]["Highest eccentricity"] = deviation("Highest eccentricity", 0, result[dataset_name][t]["Average"]["Highest eccentricity"])
            result[dataset_name][t]["Desvio"]["Highest load"] = deviation("Highest load", 0, result[dataset_name][t]["Average"]["Highest load"])

            # Average load
            result[dataset_name][t]["Average load"] = {}
            result[dataset_name][t]["Average load"]["Optimization"] = average("Optimization", 1)
            result[dataset_name][t]["Average load"]["Most connected"] = average("Most connected", 1)
            result[dataset_name][t]["Average load"]["Highest eccentricity"] = average("Highest eccentricity", 1)
            result[dataset_name][t]["Average load"]["Highest load"] = average("Highest load", 1)

            # Load standard deviation
            result[dataset_name][t]["Deviation load"] = {}
            result[dataset_name][t]["Deviation load"] = {}
            result[dataset_name][t]["Deviation load"]["Optimization"] = deviation("Optimization", 1, result[dataset_name][t]["Average load"]["Optimization"])
            result[dataset_name][t]["Deviation load"]["Most connected"] = deviation("Most connected", 1, result[dataset_name][t]["Average load"]["Most connected"])
            result[dataset_name][t]["Deviation load"]["Highest eccentricity"] = deviation("Highest eccentricity", 1, result[dataset_name][t]["Average load"]["Highest eccentricity"])
            result[dataset_name][t]["Deviation load"]["Highest load"] = deviation("Highest load", 1, result[dataset_name][t]["Average load"]["Highest load"])

            # Average latency
            result[dataset_name][t]["Average latency"] = {}
            result[dataset_name][t]["Average latency"]["Optimization"] = average("Most connected", 2)
            result[dataset_name][t]["Average latency"]["Most connected"] = average("Most connected", 2)
            result[dataset_name][t]["Average latency"]["Highest eccentricity"] = average("Highest eccentricity", 2)
            result[dataset_name][t]["Average latency"]["Highest load"] = average("Highest load", 2)

            # Latency standard deviation
            result[dataset_name][t]["Deviation latency"] = {}
            result[dataset_name][t]["Deviation latency"]["Optimization"] = deviation("Optimization", 2, result[dataset_name][t]["Average latency"]["Optimization"])
            result[dataset_name][t]["Deviation latency"]["Most connected"] = deviation("Most connected", 2, result[dataset_name][t]["Average latency"]["Most connected"])
            result[dataset_name][t]["Deviation latency"]["Highest eccentricity"] = deviation("Highest eccentricity", 2, result[dataset_name][t]["Average latency"]["Highest eccentricity"])
            result[dataset_name][t]["Deviation latency"]["Highest load"] = deviation("Highest load", 2, result[dataset_name][t]["Average latency"]["Highest load"])

            f = open(output + ".txt", "w")
            f.write(json.dumps(result, indent=4))
            f.close()

        graph.close()

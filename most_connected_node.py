import networkx as nx
import sys
import functions

def solve(N, T, LMAX, CMAX, data, G, L, K, X):
    c = {}
    c[0] = {}
    feasible = True

    for t in range(0, T):
        if t not in c:
            c[t] = {}
        if t > 0:
            # Redo all switch-controller mapping
            c = functions.reset_mapping(G, c, t)
            c = functions.assign_switches(G, c, X, t, K, CMAX, LMAX, L)
        # Check if all SDN switches are assigned to a controller
        all_controlled = functions.all_mapped(G, t, X, c)
        limite = 0
        # Try to add a new controller while there is an SDN switch not assigned to any controller
        while all_controlled == False and limite < N:
            # Find the most connected SDN node that does not host a controller
            highest = 0
            highest_degree = 0
            for n in range(0, N):
                if X[n][t] == 1 and n not in c[t]:
                    if G.degree[n] > highest_degree:
                        highest = n
                        highest_degree = G.degree[n]
            # Insert a new controller in this node
            if K[highest] <= CMAX:
                c = functions.insert_controller(G, c, t, highest, T, X, LMAX, CMAX, K, L)
                c = functions.reset_mapping(G, c, t)
                c = functions.assign_switches(G, c, X, t, K, CMAX, LMAX, L)
            # Check if all SDN switches are assigned to a controller
            all_controlled = functions.all_mapped(G, t, X, c)
            limite += 1
        # If it is not possible to assign an SDN switch to a controller, the problem is infeasible
        if all_controlled == False:
                print("Infeasible")
                feasible = False
                break

    if feasible:
        num_cont = {}
        for k, v in c.items():
            sum_avg_latency = 0
            sum_load = 0
            print("Step:", k, "\t\t\tControllers:", len(v.items()))
            num_cont[k+1] = {}
            num_cont[k+1]["num_cont"] = len(v.items())
            for k2, v2 in v.items():
                load = 0
                for i in range(0, len(v2)):
                    load += K[v2[i]]
                sum_load += load
                print("\tController:", k2, "[Load =", "{:.2f}".format(load) + "]")
                sum_latency = 0
                sum_assigned = 0
                for sw in v2:
                    sum_latency += L[sw][k2]
                    sum_assigned += 1
                    print("\t\tSwitch:", sw, "\tLatency =", L[sw][k2])
                if sum_assigned > 0:
                    sum_avg_latency += sum_latency / sum_assigned
                    print("\t\tAverage latency =", sum_latency / sum_assigned)
            try:
                num_cont[k+1]["avg_latency"] = sum_avg_latency / num_cont[k+1]["num_cont"]
            except ZeroDivisionError:
                num_cont[k+1]["avg_latency"] = 0
            print("\tAverage latency in step =", num_cont[k+1]["avg_latency"])
            print("")
            try:
                num_cont[k+1]["avg_load"] = sum_load / num_cont[k+1]["num_cont"]
            except ZeroDivisionError:
                num_cont[k+1]["avg_load"] = 0
            num_cont[k+1]["C"] = c[k]
        return num_cont
    else:
        return "infeasible"

if __name__ == "__main__":
    dataset_name = sys.argv[1]
    N = int(sys.argv[2])
    T = int(sys.argv[3])
    f = open(dataset_name + ".txt", "r")
    graph = open(dataset_name + "_graph.txt", "r")

    LMAX = 0.25
    CMAX = 20000

    data = f.readline().split(",")
    G = functions.G_from_dataset(graph, N)
    L = functions.L_from_dataset(data, N)
    K = functions.K_from_dataset(data, N, G)
    X = functions.random_migration(T, N)

    solve(N, T, LMAX, CMAX, data, G, L, K, X)

    f.close()
    graph.close()

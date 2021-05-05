import networkx as nx
import numpy as np

def L_from_dataset(data, N):
    L = [[0 for x in range(N)] for y in range(N)]
    for i in range(0, N):
        for j in range(0, N):
            L[i][j] = float(data[N*N*3 + (i*N+j)*7])
            if L[i][j] == -1:
                L[i][j] = 0
    return L

def K_from_dataset(data, N, G):
    K = [0 for x in range(N)]
    for n in range(0, N):
        load = 0
        for adj in G[n]:
            load += float(data[(adj*N+n)*3+1])
        # Worst case scenario
        #K[n] = load
        # Best case scenario
        K[n] = 0.204164824 * load + 0.01962201477
    return K

def G_from_dataset(graph, N):
    G = nx.DiGraph()
    for line in graph:
        line = line.strip()
        if line == "node [":
            next_line = graph.readline().strip()
            node = int(next_line[3:])
            G.add_node(node)
        elif line == "edge [":
            source = int(graph.readline().strip()[7:])
            target = int(graph.readline().strip()[7:])
            G.add_edge(source, target)
    return G

def fill_table(table, n, t):
    for i in range(t, len(table[0])):
        table[n][i] = 1
    return table

def random_migration(T, N):
    table = np.zeros([N,T])
    t_list = np.arange(T)
    n_list = np.arange(N)
    np.random.shuffle(t_list)
    np.random.shuffle(n_list)
    for i in range(0, T):
        if i == T-1:
            nodes = len(n_list)
        else:
            nodes = np.random.randint(1, len(n_list) - (T-1-i-1))
        for j in range(0, nodes):
            node = n_list[-1]
            n_list = n_list[:-1]
            table = fill_table(table, node, t_list[i])
    return table.tolist()

# Insert a new controller in node n
def insert_controller(G, c, t, n, T, X, LMAX, CMAX, K, L):
    N = G.number_of_nodes()
    # List of SDN switches that are not mapped to any controller
    sdns = []
    for i in range(0, N):
        if X[i][t] == 0 or i == n:
            continue
        found = False
        for k, v in c[t].items():
            if i in v:
                found = True
        if found == False:
            sdns.append(i)

    sum_load = K[n]
    switches = [n]
    # If all restrictions are satisfied, assign the switch to the new controller
    for i in range(0, len(sdns)):
        if sum_load + K[sdns[i]] <= CMAX and L[sdns[i]][n] <= LMAX:
            sum_load += K[sdns[i]]
            switches.append(sdns[i])

    # Insert a new controller in all following steps
    for i in range(t, T):
        try:
            if i == t:
                c[i][n] = switches
            else:
                c[i][n] = [n]
        except KeyError:
            c[i] = {}
            if i == t:
                c[i][n] = switches
            else:
                c[i][n] = [n]
    return c

# Redo all switch-controller mapping
def assign_switches(G, c, X, t, K, CMAX, LMAX, L):
    N = G.number_of_nodes()
    try:
        # List of SDN switches that are not mapped to any controller
        sdns = []
        for i in range(0, N):
            if X[i][t] == 1 and i not in c[t]:
                sdns.append(i)

        # Assign each SDN switch to a controller, satisfying the load and latency constraints
        for i in range(len(sdns)):
            for j in c[t]:
                sum_load = 0
                for k in range(len(c[t][j])):
                    sum_load += K[c[t][j][k]]
                if sdns[i] != j and sum_load + K[sdns[i]] <= CMAX and L[sdns[i]][j] <= LMAX:
                    c[t][j].append(sdns[i])
                    break
    except KeyError:
        pass
    return c

# Reset switch-controller mapping for a given t
def reset_mapping(G, c, t):
    try:
        for k, v in c[t].items():
            c[t][k] = [k]
    except KeyError:
        pass
    return c

# Check if all SDN switches are assigned to a controller
def all_mapped(G, t, X, c):
    N = G.number_of_nodes()
    # List of SDN switches in step t
    sdns = []
    for n in range(0, N):
        if X[n][t] == 1:
            sdns.append(n)

    try:
        # For every switch in the list, check if it is mapped to a controller. If not, return False
        for n in range(0, len(sdns)):
            found = False
            for k, v in c[t].items():
                if sdns[n] in v:
                    found = True
                    continue
            if found == False:
                return False
    except KeyError:
        pass
    return True

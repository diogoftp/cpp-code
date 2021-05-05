from ortools.linear_solver import pywraplp
import networkx as nx
import sys
import functions

def print_matrix(matrix, size):
    for x in range(size[0]):
        for y in range(size[1]):
            print(matrix[x][y], "\t", end="")
        print("")

def print_solution(matrix, size):
    for x in range(size[0]):
        for y in range(size[1]):
            print(matrix[x][y].solution_value(), "\t",  end="")
        print("")

def solve(N, T, L, LMAX, CMAX, K, X, G):
    solver = pywraplp.Solver("LinearProgrammingExample", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    #solver.set_time_limit(14400000)

    print("Number of switches (N) =", N)
    print("Latency matrix (L) =")
    print_matrix(L, [N, N])
    print("DSN switch matrix (X) =")
    print_matrix(X, [N, T])
    print("Switch load (K) =", K)

    # Decision variables
    # Controller placement
    Y = [[0 for x in range(N)] for y in range(T)]
    for t in range(0, T):
        for n in range(0, N):    
            Y[t][n] = solver.IntVar(0, 1, "Y[%i][%i]" % (t, n))
    
    # Switch-controller mapping
    Z = [[[0 for x in range(0, N)] for y in range(0, N)] for z in range(0, T)]
    for t in range(0, T):
        for n in range(0, N):
            for k in range(0, N):
                Z[t][n][k] = solver.IntVar(0, 1, "Z[%i][%i][%i]" % (t, n, k))

    # Constraints
    # Restriction (1): A controller can only be assigned to an SDN switch
    head = 0
    for t in range(0, T):
        for n in range(0, N):
            const = solver.Constraint(0, X[n][t], str(head))
            const.SetCoefficient(Y[t][n], 1)
            head = head + 1

    # Restriction (2): Switch-controller latency limit
    for t in range(0, T):
        for n in range(0, N):
            for k in range(0, N):
                const = solver.Constraint(0, LMAX, str(head))
                const.SetCoefficient(Z[t][n][k], L[n][k])
                head = head + 1

    # Restriction (3): Every SDN switch must be assigned to one, and only one, controller
    for t in range(0, T):
        for n in range(0, N):
            const = solver.Constraint(X[n][t], X[n][t], str(head))
            for k in range(0, N):
                const.SetCoefficient(Z[t][k][n], X[n][t])
            head = head + 1

    # Restriction (4): A switch in a node that hosts a controller must be assigned this controller
    for t in range(0, T):
        for n in range(0, N):
            const = solver.Constraint(0, 0, str(head))
            const.SetCoefficient(Y[t][n], 1)
            const.SetCoefficient(Z[t][n][n], -1)
            head = head + 1

    # Restriction (5): An SDN switch can only be assigned to a node that hosts a controller
    for t in range(0, T):
        for n in range(0, N):
            for k in range(0, N):
                const = solver.Constraint(0, 1, str(head))
                const.SetCoefficient(Y[t][n], 1)
                const.SetCoefficient(Z[t][n][k], -1)
                head = head + 1

    # Restriction (6): Controller load limit
    for t in range(0, T):
        for n in range(0, N):
            const = solver.Constraint(0, CMAX, str(head))
            for k in range(0, N):
                const.SetCoefficient(Z[t][n][k], K[k])
            head = head + 1

    # Restriction (7): Once a controller is placed, it stays in the same spot until the end of all future transition steps
    for n in range(0, N):
        for t in range(T-2, -1, -1):
            const = solver.Constraint(-1, 0, str(head))
            const.SetCoefficient(Y[t][n], 1)
            const.SetCoefficient(Y[t+1][n], -1)
            head = head + 1

    # Objective function
    objective = solver.Objective()
    for t in range(0, T):
        for n in range(0, N):
            objective.SetCoefficient(Y[t][n], 1)
    objective.SetMinimization()

    # Solution
    status = solver.Solve()

    if status != pywraplp.Solver.OPTIMAL:
        print("Infeasible")
        num_cont = "infeasible"
    else:
        #print("Number of variables =", solver.NumVariables())
        #print("Number of constraints =", solver.NumConstraints())
        print("Solution:")
        print("Controller location:")
        print_solution(Y, [T, N])

        print("Switch-controller mapping:")

        st=""
        num_cont = {}
        for t in range(0, T):
            sum_avg_latency = 0
            sum_assigned = 0
            sum_latency = 0
            num_cont[t+1] = {}
            num_cont[t+1]["num_cont"] = 0
            num_cont[t+1]["avg_load"] = 0
            print("Step", t+1)
            st+="\nStep"+str(t+1)+"\n"
            sum = 0
            for n in range(0, N):
                sum = sum + X[n][t]

            for n in range(0, N):
                if Y[t][n].solution_value() > 0:
                    print("Controller: [",n,"]")
                    num_cont[t+1]["num_cont"] += 1
                    sum_latency = 0
                    sum_assigned = 0
                    for k in range(0, N):
                        if Z[t][n][k].solution_value() > 0:
                            print("Z[",k,"]", "Latency =", L[n][k])
                            sum_latency += L[n][k]
                            sum_assigned += 1
                            pass
                    if sum_assigned > 0:
                        sum_avg_latency += sum_latency / sum_assigned
                        print("Average latency =", sum_latency / sum_assigned)
                st+="\n"
            try:
                num_cont[t+1]["avg_latency"] = sum_avg_latency / num_cont[t+1]["num_cont"]
            except ZeroDivisionError:
                num_cont[t+1]["avg_latency"] = 0
                print("Average latency in step =", num_cont[t+1]["avg_latency"])
            print("")
        # Carga de trabalho de cada controlador
        print("Controller load:")
        for t in range(0, T):
            sum_load = 0
            for n in range(0, N):
                sum = 0
                for k in range(0, N):
                    sum = sum + Z[t][n][k].solution_value() * K[k]
                if(Y[t][n].solution_value() > 0):
                    sum_load += sum
                    print("Step", t + 1, "controller", n, "=", sum)
            try:
                num_cont[t+1]["avg_load"] = sum_load / num_cont[t+1]["num_cont"]
            except ZeroDivisionError:
                num_cont[t+1]["avg_load"] = 0

            Y_solution = [[0 for x in range(N)] for y in range(T)]
            Z_solution = [[[0 for x in range(0, N)] for y in range(0, N)] for z in range(0, T)]
            for t2 in range(0, T):
                for n in range(0, N):
                    Y_solution[t2][n] = Y[t2][n].solution_value()
                    for k in range(0, N):
                        Z_solution[t2][n][k] = Z[t2][n][k].solution_value()
            num_cont[t+1]["Y"] = Y_solution
            num_cont[t+1]["Z"] = Z_solution
    return num_cont

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

    solve(N, T, L, LMAX, CMAX, K, X, G)

    f.close()
    graph.close()

import numpy as np
from tqdm import tqdm
from itertools import combinations


def TSP_SA(graph):
    s = list(range(len(graph)))
    c = cost(graph, s)
    T = 30
    alpha = 0.99
    for _ in range(30_000):
        n = np.random.randint(0, len(graph))

        while True:
            m = np.random.randint(0, len(graph))
            if n != m:
                break

        s1 = swap(s, m, n)
        c1 = cost(graph, s1)
        if c1 < c:
            s, c = s1, c1
        else:
            if np.inf not in (c, c1) and np.random.rand() < np.exp(-(c1 - c) / T):
                s, c = s1, c1
        T = alpha * T

    return s, c


def swap(s, m, n):
    i, j = min(m, n), max(m, n)
    s1 = s.copy()
    while i < j:
        s1[i], s1[j] = s1[j], s1[i]
        i += 1
        j -= 1
    return s1


def cost(graph, s):
    cost_ = 0
    for i in range(len(s) - 1):
        cost_ += graph[s[i]][s[i + 1]]
    cost_ += graph[s[len(s) - 1]][s[0]]
    return cost_


def swapEdgesTwoOPT(tour, i, j):
    """
    Method to swap two edges and replace with
    their cross.
    """
    newtour = tour[:i + 1]
    newtour.extend(reversed(tour[i + 1:j + 1]))
    newtour.extend(tour[j + 1:])

    return newtour


def swapEdgesThreeOPT(tour, i, j, k, case):
    """Method to swap edges from 3-OPT"""

    if case == 1:
        newtour = swapEdgesTwoOPT(tour.copy(), i, k)

    elif case == 2:
        newtour = swapEdgesTwoOPT(tour.copy(), i, j)

    elif case == 3:
        newtour = swapEdgesTwoOPT(tour.copy(), j, k)

    elif case == 4:
        newtour = tour[:i + 1]
        newtour.extend(tour[j + 1:k + 1])
        newtour.extend(reversed(tour[i + 1:j + 1]))
        newtour.extend(tour[k + 1:])

    elif case == 5:
        newtour = tour[:i + 1]
        newtour.extend(reversed(tour[j + 1:k + 1]))
        newtour.extend(tour[i + 1:j + 1])
        newtour.extend(tour[k + 1:])

    elif case == 6:
        newtour = tour[:i + 1]
        newtour.extend(reversed(tour[i + 1:j + 1]))
        newtour.extend(reversed(tour[j + 1:k + 1]))
        newtour.extend(tour[k + 1:])

    elif case == 7:
        newtour = tour[:i + 1]
        newtour.extend(tour[j + 1:k + 1])
        newtour.extend(tour[i + 1:j + 1])
        newtour.extend(tour[k + 1:])

    else:
        newtour = []

    return newtour


def twoOPT(graph, tour):
    """
    Method to create new tour using 2OPT
    args:
        tour: List of nodes forming a cycle
    return:
        tour: List of nodes forming a cycle
            Two optimal tour
        tourlen: int/float
            Length of two optimal tour
    """
    n = len(tour)
    if n <= 2:
        # no cycle possible
        return tour, 0

    # length of provided tour
    tour_cost = cost(graph, tour)

    # tracking improvemnt in tour
    improved = True

    while improved:
        improved = False

        for i in range(n):
            for j in range(i + 2, n - 1):

                a = graph[tour[i]][tour[i + 1]]
                b = graph[tour[j]][tour[j + 1]]
                c = graph[tour[i]][tour[j]]
                d = graph[tour[i + 1]][tour[j + 1]]

                new_tour = swapEdgesTwoOPT(tour.copy(), i, j)
                new_cost = cost(graph, new_tour)
                if new_cost < tour_cost:
                    improved = True
                    tour = new_tour
                    tour_cost = new_cost

    return tour, tour_cost


def threeOPT(graph, tour):
    """
    Method to create new tour using 3OPT
    args:
        tour: List of nodes forming a cycle
    return:
        tour: List of nodes forming a cycle
            Three optimal tour
        tourlen: int/float
            Length of three optimal tour
    """
    n = len(tour)
    if n <= 2:
        # no cycle possible
        return [], 0

    # length of provided tour
    tourlen = cost(graph, tour)

    # tracking improvemnt in tour
    improved = True

    while improved:

        improved = False
        for i in range(n):
            for j in range(i + 2, n - 1):
                for k in range(j + 2, n - 2 + (i > 0)):
                    # print(i, j, k)
                    a, b = tour[i], tour[i + 1]
                    c, d = tour[j], tour[j + 1]
                    e, f = tour[k], tour[k + 1]

                    # possible cases of removing three edges 
                    # and adding three
                    deltacase = {
                        1: graph[a][e] + graph[b][f] - graph[a][b] - graph[e][f],
                        2: graph[a][c] + graph[b][d] - graph[a][b] - graph[c][d],
                        3: graph[c][e] + graph[d][f] - graph[c][d] - graph[e][f],
                        4: graph[a][d] + graph[e][c] + graph[b][f] - graph[a][b] - graph[c][d] - graph[e][f],
                        5: graph[a][e] + graph[d][b] + graph[c][f] - graph[a][b] - graph[c][d] - graph[e][f],
                        6: graph[a][c] + graph[b][e] + graph[d][f] - graph[a][b] - graph[c][d] - graph[e][f],
                        7: graph[a][d] + graph[e][b] + graph[c][f] - graph[a][b] - graph[c][d] - graph[e][f],
                    }

                    # get the case with most benefit
                    bestcase = min(deltacase, key=deltacase.get)

                    if deltacase[bestcase] < 0:
                        # print(deltacase[bestcase], i, j, k, bestcase)
                        tour = swapEdgesThreeOPT(tour.copy(), i, j, k, case=bestcase)
                        # print(self.calculateTourLength(tour), tourlen + deltacase[bestcase])
                        tourlen += deltacase[bestcase]
                        improved = True

    return tour, tourlen


"""
0: CNY
1: EUR
2: GBP
3: JPY
4: USD
"""
g = [
    [0, 0.87, 0.05, 0.11, float('inf')],
    [0.87, 0, 0.31, float('inf'), 0.3],
    [0.05, 0.31, 0, float('inf'), 0.09],
    [0.11, float('inf'), float('inf'), 0, 0.43],
    [float('inf'), 0.3, 0.09, 0.43, 0]
]

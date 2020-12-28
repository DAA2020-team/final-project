import numpy as np
from typing import Tuple, List, Dict

from data_structures.currency import Currency


def tour_to_string(tour: List[Currency]) -> str:
    return "[" + " -> ".join([currency._code for currency in tour] + [tour[0]._code]) + "]"


def cost(graph: np.ndarray, tour: List[int]) -> float:
    tour_cost = 0
    for i in range(len(tour) - 1):
        tour_cost += graph[tour[i]][tour[i + 1]]
    tour_cost += graph[tour[len(tour) - 1]][tour[0]]
    return tour_cost


def simulated_annealing(graph: np.ndarray) -> Tuple[float, List[int]]:
    n = len(graph)
    tour = list(range(n))
    tour_cost = cost(graph, tour)
    T = 30
    alpha = 0.99
    for _ in range(25_000):  # TODO choose the best
        a = np.random.randint(0, n)

        while True:
            b = np.random.randint(0, n)
            if a != b:
                break

        new_tour = swap_simulated_annealing(tour, b, a)
        new_cost = cost(graph, new_tour)
        if new_cost < tour_cost:
            tour, tour_cost = new_tour, new_cost
        else:
            if np.random.rand() < np.exp(-(new_cost - tour_cost) / T):
                tour, tour_cost = new_tour, new_cost
        T = alpha * T

    return tour_cost, tour


def swap_simulated_annealing(tour: List[int], m: int, n: int) -> List[int]:
    i, j = min(m, n), max(m, n)
    new_tour = tour.copy()
    while i < j:
        new_tour[i], new_tour[j] = new_tour[j], new_tour[i]
        i += 1
        j -= 1
    return new_tour


def swap_two_opt(tour: List[int], i: int, j: int) -> List[int]:
    """Method to swap two edges and replace with their cross."""

    new_tour = tour[:i + 1]
    new_tour.extend(reversed(tour[i + 1:j + 1]))
    new_tour.extend(tour[j + 1:])

    return new_tour


def swap_three_opt(tour: List[int], i: int, j: int, k: int, case: int) -> List[int]:
    """Method to swap edges from 3-OPT"""

    if case == 1:
        new_tour = swap_two_opt(tour.copy(), i, k)

    elif case == 2:
        new_tour = swap_two_opt(tour.copy(), i, j)

    elif case == 3:
        new_tour = swap_two_opt(tour.copy(), j, k)

    elif case == 4:
        new_tour = tour[:i + 1]
        new_tour.extend(tour[j + 1:k + 1])
        new_tour.extend(reversed(tour[i + 1:j + 1]))
        new_tour.extend(tour[k + 1:])

    elif case == 5:
        new_tour = tour[:i + 1]
        new_tour.extend(reversed(tour[j + 1:k + 1]))
        new_tour.extend(tour[i + 1:j + 1])
        new_tour.extend(tour[k + 1:])

    elif case == 6:
        new_tour = tour[:i + 1]
        new_tour.extend(reversed(tour[i + 1:j + 1]))
        new_tour.extend(reversed(tour[j + 1:k + 1]))
        new_tour.extend(tour[k + 1:])

    elif case == 7:
        new_tour = tour[:i + 1]
        new_tour.extend(tour[j + 1:k + 1])
        new_tour.extend(tour[i + 1:j + 1])
        new_tour.extend(tour[k + 1:])

    else:
        new_tour = []

    return new_tour


def two_opt(graph: np.ndarray, tour: List[int]) -> Tuple[float, List[int]]:
    """
    Method to create new tour using 2OPT
    args:
        tour: List of nodes forming a cycle
    return:
        tour: List of nodes forming a cycle
            Two optimal tour
        tour_cost: int/float
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

                new_tour = swap_two_opt(tour.copy(), i, j)
                new_cost = cost(graph, new_tour)
                if new_cost < tour_cost:
                    improved = True
                    tour = new_tour
                    tour_cost = new_cost

    return tour_cost, tour


def three_opt(graph: np.ndarray, tour: List[int]) -> Tuple[float, List[int]]:
    """
    Method to create new tour using 3OPT
    args:
        tour: List of nodes forming a cycle
    return:
        tour: List of nodes forming a cycle
            Three optimal tour
        tour_cost: int/float
            Length of three optimal tour
    """
    n = len(tour)
    if n <= 2:
        # no cycle possible
        return [], 0

    # length of provided tour
    tour_cost = cost(graph, tour)

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
                    best_case = min(deltacase, key=deltacase.get)

                    if deltacase[best_case] < 0:
                        tour = swap_three_opt(tour.copy(), i, j, k, case=best_case)
                        tour_cost += deltacase[best_case]
                        improved = True

    return tour_cost, tour

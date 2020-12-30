import numpy as np
from typing import Tuple, List

from data_structures.currency import Currency


SA_NAME = 'sa'
TWO_OPT_NAME = '2opt'
THREE_OPT_NAME = '3opt'


def tour_to_string(tour: List[Currency]) -> str:
    """
    Converts a tour into a string
    :param tour: list of currencies representing the tour
    :return: the string representation of the tour
    """
    return "[" + " -> ".join([currency._code for currency in tour] + [tour[0]._code]) + "]"


def cost(graph: np.ndarray, tour: List[int]) -> float:
    """
    Computes the cost of the tour in the graph
    :param graph: the adjacency matrix of the graph containing the edge weights
    :param tour: the list of indices representing the tour
    :return: the sum of all edge weights involved in the tour
    """
    tour_cost = 0
    for i in range(len(tour) - 1):
        tour_cost += graph[tour[i]][tour[i + 1]]
    tour_cost += graph[tour[len(tour) - 1]][tour[0]]
    return tour_cost


def simulated_annealing(graph: np.ndarray) -> Tuple[float, List[int]]:
    """
    Looks for the exchange tour of minimal rate using the Simulated Annealing Local Search technique
    :param graph: the graph to search an exchange tour in
    :return:
        tour_cost: the cost of the tour
        tour: the tour
    """
    n = len(graph)
    tour = list(range(n))
    tour_cost = cost(graph, tour)
    t = 30
    alpha = 0.99
    for _ in range(10_000):
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
            if np.random.rand() < np.exp(-(new_cost - tour_cost) / t):
                tour, tour_cost = new_tour, new_cost
        t = alpha * t

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
        new_tour.extend(reversed(tour[i + 1:j + 1]))
        new_tour.extend(reversed(tour[j + 1:k + 1]))
        new_tour.extend(tour[k + 1:])

    elif case == 5:
        new_tour = tour[:i + 1]
        new_tour.extend(reversed(tour[j + 1:k + 1]))
        new_tour.extend(tour[i + 1:j + 1])
        new_tour.extend(tour[k + 1:])

    elif case == 6:
        new_tour = tour[:i + 1]
        new_tour.extend(tour[j + 1:k + 1])
        new_tour.extend(reversed(tour[i + 1:j + 1]))
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
    Looks for the exchange tour of minimal rate using the 2-Optimal Local Search technique
    :param graph: the graph to search an exchange tour in
    :return:
        tour_cost: the cost of the tour
        tour: the tour
    """
    n = len(tour)
    if n <= 2:
        # no cycle possible
        return 0.0, []

    # length of provided tour
    tour_cost = cost(graph, tour)

    # tracking improvement in tour
    improved = True

    while improved:
        improved = False

        for i in range(n):
            for j in range(i + 2, n - 1):
                a = graph[tour[i]][tour[i + 1]]
                b = graph[tour[j]][tour[j + 1]]
                c = graph[tour[i]][tour[j]]
                d = graph[tour[i + 1]][tour[j + 1]]

                # benefit from swapping i,i+1 and j,j+1 with i,j and i+1,j+1
                delta = - a - b + c + d
                if delta < 0:
                    tour = swap_two_opt(tour.copy(), i, j)
                    tour_cost += delta
                    improved = True

    return tour_cost, tour


def three_opt(graph: np.ndarray, tour: List[int]) -> Tuple[float, List[int]]:
    """
    Looks for the exchange tour of minimal rate using the 3-Optimal Local Search technique
    :param graph: the graph to search an exchange tour in
    :return:
        tour_cost: the cost of the tour
        tour: the tour
    """
    n = len(tour)
    if n <= 2:
        # no cycle possible
        return 0.0, []

    # length of provided tour
    tour_cost = cost(graph, tour)

    # tracking improvement in tour
    improved = True

    while improved:

        improved = False
        for i in range(n):
            for j in range(i + 2, n - 1):
                for k in range(j + 2, n - 2 + (i > 0)):
                    a, b = tour[i], tour[i + 1]
                    c, d = tour[j], tour[j + 1]
                    e, f = tour[k], tour[k + 1]

                    # possible cases of removing three edges and adding three
                    delta_case = {
                        1: graph[a][e] + graph[b][f] - graph[a][b] - graph[e][f],
                        2: graph[a][c] + graph[b][d] - graph[a][b] - graph[c][d],
                        3: graph[c][e] + graph[d][f] - graph[c][d] - graph[e][f],

                        4: graph[a][c] + graph[b][e] + graph[d][f] - graph[a][b] - graph[c][d] - graph[e][f],
                        5: graph[a][e] + graph[d][b] + graph[c][f] - graph[a][b] - graph[c][d] - graph[e][f],
                        6: graph[a][d] + graph[e][c] + graph[b][f] - graph[a][b] - graph[c][d] - graph[e][f],

                        7: graph[a][d] + graph[e][b] + graph[c][f] - graph[a][b] - graph[c][d] - graph[e][f],
                    }

                    # get the case with most benefit
                    best_case = min(delta_case, key=delta_case.get)
                    delta = delta_case[best_case]

                    if delta < 0:
                        tour = swap_three_opt(tour.copy(), i, j, k, case=best_case)
                        tour_cost += delta
                        improved = True

    return tour_cost, tour


def sa_two_opt(graph: np.ndarray) -> Tuple[float, List[int]]:
    _, tour = simulated_annealing(graph)
    return two_opt(graph, tour)

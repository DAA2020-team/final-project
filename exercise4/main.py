import sys
sys.path.append('../final-project')

from data_structures.currency import Currency
from data_structures.min_heap_priority_queue import HeapPriorityQueue

from iso4217 import Currency as iso_currency
from random import random, shuffle, seed
from typing import Set, List, Dict, Tuple
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from time import perf_counter

from exercise4.tsp import twoOPT, threeOPT, TSP_SA


OVER_COST = 10 ** 10


def create_currencies(n: int) -> List[Currency]:
    currencies = [currency for currency in iso_currency]
    codes = [currency.code for currency in currencies]
    shuffle(codes)
    currencies = [Currency(code) for code in codes[:n]]
    for i, c1 in enumerate(currencies):
        for c2 in currencies[i + 1:]:
            if random() < 0.8:
                change = random()
                c1.add_change(c2._code, change)
                c2.add_change(c1._code, change)
    return currencies


def show_graph(ids: Dict[int, Currency], graph: List[List[float]]):
    n = len(graph)

    g = nx.Graph()

    # for i in range(n):
    #    g.add_node(i)

    for i in range(n):
        for j in range(n):
            weight = graph[i][j]
            if weight < OVER_COST:
                g.add_edge(ids[i]._code, ids[j]._code, weight=weight)

    plt.plot()
    layout = nx.shell_layout(g)
    nx.draw(g, layout, with_labels=True)
    node_labels = nx.get_node_attributes(g, 'label')
    edge_labels = nx.get_edge_attributes(g, "weight")
    for key, weight in edge_labels.items():
        edge_labels[key] = round(edge_labels[key], 3)
    nx.draw_networkx_edge_labels(g, pos=layout, label_pos=0.5, font_color='b', edge_labels=edge_labels, font_size=9)
    plt.show()


def create_custom_curencies() -> List[Currency]:
    mru = Currency("MRU")
    pen = Currency("PEN")
    lbp = Currency("LBP")
    sar = Currency("SAR")
    sek = Currency("SEK")

    mru.add_change("PEN", 0.86)
    mru.add_change("LBP", 0.75)
    mru.add_change("SEK", 0.91)

    pen.add_change("SAR", 0.32)
    pen.add_change("MRU", 0.86)
    pen.add_change("LBP", 0.99)
    pen.add_change("SEK", 0.57)

    lbp.add_change("MRU", 0.75)
    lbp.add_change("PEN", 0.99)
    lbp.add_change("SAR", 0.62)

    sar.add_change("PEN", 0.32)
    sar.add_change("LBP", 0.62)

    sek.add_change("MRU", 0.91)
    sek.add_change("PEN", 0.57)

    return [
        mru,
        pen,
        lbp,
        sar,
        sek
    ]


def create_graph_from_currencies(currencies: List[Currency]) -> List[List[float]]:
    shuffle(currencies)
    n = len(currencies)
    ids = {i: currency for i, currency in enumerate(currencies)}
    graph = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                graph[i][j] = 0
            else:
                c1 = ids[i]
                c2 = ids[j]
                try:
                    graph[i][j] = c1.get_change(c2._code)
                except KeyError as e:  # r(c1, c2) does not exist
                    graph[i][j] = OVER_COST

    retval = np.allclose(graph, graph.T)  # TODO decidere se lasciare questa riga o meno
    if not retval:
        raise ValueError("currencies change rates are not symmetric.")

    return ids, graph


def call_and_time(name, ids, func, *args):
    print(name, end='')
    t0 = perf_counter()
    tour, tour_cost = func(*args)
    t1 = perf_counter()
    print(f", {t1 - t0 : .4f}s")
    print(tour_cost, [ids[i]._code for i in tour])


def find_exchange_tour(currencies: Set[Currency]) -> Tuple[List[Currency], float]:
    ids, graph = create_graph_from_currencies(currencies)
    # show_graph(ids, graph)
    call_and_time("2-OPT", ids, twoOPT, graph, list(range(len(graph))))
    call_and_time("3-OPT", ids, threeOPT, graph, list(range(len(graph))))
    call_and_time("Simulated Annealing", ids, TSP_SA, graph)

def main():
    # currencies = create_currencies(5)
    # find_exchange_tour(set(currencies))

    # currencies = create_custom_curencies()
    currencies = create_currencies(100)
    find_exchange_tour(currencies)

    # show_graph(ids, graph)


if __name__ == '__main__':
    main()

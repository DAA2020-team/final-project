import sys
sys.path.append('../final-project')

from data_structures.currency import Currency

from iso4217 import Currency as iso_currency
from random import random, shuffle
from typing import Set, List, Dict, Tuple
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from time import perf_counter
import argparse

from exercise4.exchange_tour import (simulated_annealing, two_opt, three_opt, sa_two_opt, tour_to_string,
                                     SA_NAME, TWO_OPT_NAME, THREE_OPT_NAME, SA_2OPT_NAME)


global technique
OVER_COST = 10 ** 10


def init_parameter():
    """
    Create argument parser.
    usage: main.py [-h] [-i {custom,random}] [-n N] [-t {sa,2opt,3opt,sa2opt} [{sa,2opt,3opt,sa2opt} ...]] [-v [V]]
    Currencies exchange tour
    optional arguments:
      -h, --help            show this help message and exit
      -i {custom,random}, --input {custom,random}
                            where the input set of currencies comes from.
                            If 'custom', the set of currencies is loaded by the create_custom_currencies() function.
                            If 'random', the set of currencies is randomly chosen in ISO-4217.
                            (default: custom)
      -n N                  the number of currencies to insert in the graph (randomly chosen in ISO-4217).
                            It is only effective if the input is 'random'.
                            (default: 100)
      -t {sa,2opt,3opt,sa2opt} [{sa,2opt,3opt,sa2opt} ...], --technique {sa,2opt,3opt,sa2opt} [{sa,2opt,3opt,sa2opt} ...]
                            the technique to use in order to find an exchange tour of minimal rate.
                            sa stands for Simulated Annealing; 2opt stands for 2-Optimal; 3opt stands for 3-Optimal;
                            sa2opt uses the solution returned by Simulated Annealing as input to 2-Optimal.
                            (default: sa2opt)
      -v [V], --verbose [V]
                            if set, it prints the exchange tour and the execution time. (default: false)
    """
    parser = argparse.ArgumentParser(description='Currencies exchange tour')
    parser.add_argument("-i", "--input", type=str, choices=['custom', 'random'], default='custom', dest='i',
                        help="where the input set of currencies comes from. "
                             "If 'custom', the set of currencies is loaded by the create_custom_currencies() function. "
                             "If 'random', the set of currencies is randomly chosen in ISO-4217. (default: custom)")
    parser.add_argument("-n", type=int, default=100,
                        help="the number of currencies to insert in the graph (randomly chosen in ISO-4217). "
                             "It is only effective if the input is 'random'. (default: 100)")
    parser.add_argument('-t', '--technique', type=str, choices=[SA_NAME, TWO_OPT_NAME, THREE_OPT_NAME, SA_2OPT_NAME],
                        default=(SA_2OPT_NAME, ), nargs='+', dest='t',
                        help='the technique to use in order to find an exchange tour of minimal rate. '
                             f'{SA_NAME} stands for Simulated Annealing; '
                             f'{TWO_OPT_NAME} stands for 2-Optimal; '
                             f'{THREE_OPT_NAME} stands for 3-Optimal; '
                             f'{SA_2OPT_NAME} uses the solution returned by Simulated Annealing as input to 2-Optimal. '
                             f'(default: {SA_2OPT_NAME})')
    parser.add_argument("-v", "--verbose", metavar='V', const=True, nargs='?', dest='v',
                        help="if set, it prints the exchange tour and the execution time. (default: false)")
    return parser.parse_args()


def create_currencies(n: int) -> List[Currency]:
    """
    Creates a random set of n currencies, randomly chosen from ISO-4217
    :param n: the number of currencies
    :return: a set of currencies from ISO-4217
    """
    currencies = [currency for currency in iso_currency]
    codes = [currency.code for currency in currencies]
    shuffle(codes)
    currencies = [Currency(code) for code in codes[:n]]
    for i, c1 in enumerate(currencies):
        for c2 in currencies[i + 1:]:
            if random() < 0.8:
                change = round(random(), 4)
                c1.add_change(c2._code, change)
                c2.add_change(c1._code, change)
    return currencies


def show_graph(ids: Dict[int, Currency], graph: np.ndarray):
    """
    Displays the graph of currencies represented in ids.
    :param graph: the graph to display
    :param ids: the association between indices and codes
    """
    n = len(graph)

    g = nx.Graph()

    for i in range(n):
        for j in range(n):
            weight = graph[i][j]
            if weight < OVER_COST:
                g.add_edge(ids[i]._code, ids[j]._code, weight=weight)

    plt.plot()
    layout = nx.shell_layout(g)
    nx.draw(g, layout, with_labels=True)
    edge_labels = nx.get_edge_attributes(g, "weight")
    for key, weight in edge_labels.items():
        edge_labels[key] = round(edge_labels[key], 4)
    nx.draw_networkx_edge_labels(g, pos=layout, label_pos=0.5, font_color='b', edge_labels=edge_labels, font_size=9)
    plt.show()


def create_custom_currencies() -> Set[Currency]:
    """
    [CHANGE HERE]
    Creates a custom set of currencies
    :return: a set of currencies
    """
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

    return {mru, pen, lbp, sar, sek}


def create_graph_from_currencies(currencies: List[Currency]) -> Tuple[Dict[int, Currency], np.ndarray]:
    """
    Creates an undirected graph, implemented as an adjacency matrix representing currencies.
    :param currencies: the currencies to insert in the graph
    :return:
        ids: the association between indices and codes
        graph: the adjacency matrix of the graph representing currencies
    """
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
                except KeyError:  # r(c1, c2) does not exist
                    graph[i][j] = OVER_COST

    ret_val = np.allclose(graph, graph.T)
    if not ret_val:
        raise ValueError("currencies change rates are not symmetric.")

    return ids, graph


def find_exchange_tour(currencies: Set[Currency]) -> Tuple[np.ndarray, float, List[Currency]]:
    """
    Finds an exchange tour of minimal rate among currencies.
    :param currencies: the set of currencies to search the exchange tour in
    :return:
        graph: the adjacency matrix of the graph representing currencies
        rate: the rate of the exchange tour found
        exchange_tour: the list of currencies involved in the exchange tour
    """
    ids, graph = create_graph_from_currencies(list(currencies))

    if technique == SA_NAME:
        rate, exchange_tour = simulated_annealing(graph)
    elif technique == TWO_OPT_NAME:
        rate, exchange_tour = two_opt(graph, list(range(len(graph))))
    elif technique == THREE_OPT_NAME:
        rate, exchange_tour = three_opt(graph, list(range(len(graph))))
    elif technique == SA_2OPT_NAME:
        rate, exchange_tour = sa_two_opt(graph)
    else:
        raise ValueError("Technique unknown.")

    return graph, rate, [ids[step] for step in exchange_tour]


def main(i='custom', n=100, t=(SA_NAME, ), verbose=False):
    global technique
    algorithm_names = {
        SA_NAME: 'Simulated Annealing',
        TWO_OPT_NAME: '2-Optimal',
        THREE_OPT_NAME: '3-Optimal',
        SA_2OPT_NAME: 'Simulated Annealing + 2-Optimal'
    }

    if i == 'custom':
        currencies = create_custom_currencies()
    elif i == 'random':
        currencies = create_currencies(n)
    else:
        raise ValueError("Input unknown.")

    for algorithm in t:
        technique = algorithm
        print(algorithm_names[algorithm], end='', flush=True)
        t0 = perf_counter()
        graph, rate, exchange_tour = find_exchange_tour(set(currencies))
        t1 = perf_counter()
        print(f', {t1 - t0 : .4f}s')

        if rate >= OVER_COST:
            print("Exchange tour not found")
        else:
            print(f"Exchange tour of rate {rate : .4f} found", end='')
            if verbose:
                print(': ', tour_to_string(exchange_tour))
            else:
                print('.\n')


if __name__ == '__main__':
    args = init_parameter()
    if not args.n >= 2:
        raise argparse.ArgumentTypeError("N must be at least 2.")
    main(args.i, args.n, tuple(set(args.t)), args.v)

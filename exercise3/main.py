import sys
sys.path.append('../final-project')

from data_structures.graph import Graph
from data_structures.currency import Currency
from exercise3.shortest_paths import compute_shortest_path
from utils import str2bool

import networkx as nx
import matplotlib.pyplot as plt
from iso4217 import Currency as iso_currency
from random import shuffle, choice, uniform
from typing import List, Set, Tuple, Optional
import argparse


def init_parameter():
    """
    usage: main.py [-h] [-n N] [-v V]
    Currencies arbitrage opportunities
    optional arguments:
      -h, --help           show this help message and exit
      -n N                 the number of currencies to insert in the graph(randomly chosen in ISO-4217) (default: 5)
      -v V, --visualize V  if set to true, it draws the graph (default: false)
    :return: input arguments
    """
    parser = argparse.ArgumentParser(description='Currencies arbitrage opportunities')
    parser.add_argument("-n", type=int, default=5, help="the number of currencies to insert in the graph"
                                                        "(randomly chosen in ISO-4217) (default: 5)")
    parser.add_argument("-v", "--visualize", type=str2bool, default=True, metavar='V',
                        help="if set to true, it draws the graph (default: false)")
    return parser.parse_args()


def show_graph(g: Graph):
    vertices = g.vertices()
    edges = g.edges()

    dg = nx.DiGraph()
    dg.add_nodes_from(vertices, label=vertices)
    dg.add_weighted_edges_from([(edge._origin, edge._destination, edge.element()) for edge in edges])

    plt.plot()
    layout = nx.circular_layout(dg)
    nx.draw(dg, layout, with_labels=True)
    labels = nx.get_edge_attributes(dg, "weight")
    for key, weight in labels.items():
        labels[key] = round(labels[key], 2)
    nx.draw_networkx_edge_labels(dg, pos=layout, edge_labels=labels)
    plt.show()


def create_currencies(n: int) -> List[Currency]:
    currencies = [currency for currency in iso_currency]
    codes = [currency.code for currency in currencies]
    shuffle(codes)
    currencies = [Currency(code) for code in codes][:n]
    for currency in currencies:
        try:
            for c in currencies:
                if c != currency:
                    currency.add_change(c._code, uniform(-1, 1))
        except ValueError:
            continue
    return currencies


def create_graph(currencies: Set[Currency]):
    g = Graph(directed=True)
    for currency in currencies:
        if currency._code not in g.vertices():
            g.insert_vertex(currency._code)
        for c in currencies:
            code = c._code
            try:
                change = currency.get_change(code)
                if code not in g.vertices():
                    g.insert_vertex(code)
                g.insert_edge(currency._code, code, round(change, 2))
            except KeyError:
                continue
    return g


def find_negative_cycle(graph: Graph, source: str) -> Tuple[bool, Optional[List[Graph.Edge]]]:
    # Step 1: Find all neighbors outgoing from source
    neighbors = {edge.opposite(source): edge for edge in graph.incident_edges(source, outgoing=True)}

    # Step 2: Find minimum edge weight in the graph
    minimum_edge_weight = min(edge.element() for edge in graph.edges())

    # Step 3: Make all edges positive
    for edge in graph.edges():
        edge._element += abs(minimum_edge_weight)

    # Step 4: Call compute_shortest_path from each vertex in neighbors to source
    paths = {vertex: compute_shortest_path(graph, vertex, source) for vertex in neighbors}

    # Step 5: Restore all edges weights
    for edge in graph.edges():
        edge._element -= abs(minimum_edge_weight)

    # Step 6: Close cycles
    for vertex, path in paths.items():
        if len(path) == 0:
            continue
        path_weight = sum(edge.element() for edge in path)
        first_edge = neighbors[vertex]
        first_weight = first_edge.element()
        cycle_weight = first_weight + path_weight
        cycle = [first_edge] + path
        if cycle_weight < 0:
            return True, cycle

    return False, None


def find_arbitrage_opportunity(c: Set[Currency], s: Currency) -> Tuple[Graph, bool, Optional[List[Graph.Edge]]]:
    if s._code not in [currency._code for currency in c]:
        return False, None, None
    graph = create_graph(c)
    found, cycle = find_negative_cycle(graph, s._code)
    return graph, found, cycle


def print_path(path: List[Graph.Edge]) -> str:
    cycle = "[" + " -> ".join([edge.endpoints()[0] for edge in path] + [path[-1].endpoints()[1]]) + "]"
    cycle_weight = round(sum(edge.element() for edge in path), 2)
    print(f"The cycle {cycle} is an arbitrage opportunity for {path[0].endpoints()[0]} of cost {cycle_weight : .2f}")


def main(n: int, visualize: bool):
    currencies = create_currencies(n)
    s = choice(currencies)
    graph, found, cycle = find_arbitrage_opportunity(currencies, s)
    if found:
        print_path(cycle)
    else:
        print(f"The graph does not contain arbitrage opportunities for {s._code}")
    if visualize:
        show_graph(graph)


if __name__ == '__main__':
    args = init_parameter()
    main(args.n, args.visualize)

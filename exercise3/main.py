import sys
sys.path.append('../final-project')

from data_structures.graph import Graph
from data_structures.currency import Currency
import networkx as nx
import matplotlib.pyplot as plt
from iso4217 import Currency as iso_currency
from random import shuffle, choice, uniform, seed
from typing import List, Set, Tuple

seed(2020)


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
    nx.draw_networkx_edge_labels(dg, pos=layout, edge_labels=labels)
    plt.show()


def create_currencies() -> List[Currency]:
    currencies = [currency for currency in iso_currency]
    codes = [currency.code for currency in currencies]
    shuffle(codes)
    currencies = [Currency(code) for code in codes][:8]
    for currency in currencies:
        try:
            for _ in range(int(0.5 * len(currencies))):
                currency.add_change(choice(currencies)._code, uniform(-1, 1))
        except ValueError:
            continue
    return currencies


def create_graph(currencies: Set[Currency]):
    g = Graph(directed=True)
    for currency in currencies:
        u = g.insert_vertex(currency._code)
        for c in currencies:
            code = c._code
            try:
                change = currency.get_change(code)
                v = Graph.Vertex(code)
                if code not in g.vertices():
                    v = g.insert_vertex(code)
                g.insert_edge(currency._code, code, round(change, 2))
            except KeyError:
                continue
    return g


def get_arbitrage_opportunity(c: Set[Currency], s: Currency) -> Tuple[bool, List[Currency]]:
    if s._code not in [currency._code for currency in c]:
        return None
    g = create_graph(c)
    return g


def main():
    currencies = create_currencies()
    g = get_arbitrage_opportunity(currencies, choice(currencies))
    if g is not None:
        show_graph(g)
    else:
        print("NONE")
    print("OK")


if __name__ == '__main__':
    main()

import sys
sys.path.append('../final-project')

from data_structures.graph import Graph
from data_structures.currency import Currency

from iso4217 import Currency as iso_currency
from random import uniform, shuffle
from typing import Set
import networkx as nx
import matplotlib.pyplot as plt


def create_currencies(n: int) -> Set[Currency]:
    currencies = [currency for currency in iso_currency]
    codes = [currency.code for currency in currencies]
    shuffle(codes)
    currencies = [Currency(code) for code in codes[:n]]
    for i, c1 in enumerate(currencies):
        for c2 in currencies[i + 1:]:
            c1.add_change(c2._code, uniform(0, 1))
    return set(currencies)


def create_graph(currencies: Set[Currency]) -> Graph:
    g = Graph()
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


def show_graph(g: Graph):
    vertices = g.vertices()
    edges = g.edges()

    dg = nx.Graph()
    dg.add_nodes_from(vertices, label=vertices)
    dg.add_weighted_edges_from([(edge._origin, edge._destination, edge.element()) for edge in edges])

    plt.plot()
    layout = nx.circular_layout(dg)
    nx.draw(dg, layout, with_labels=True)
    labels = nx.get_edge_attributes(dg, "weight")
    for key, weight in labels.items():
        labels[key] = round(labels[key], 2)
    nx.draw_networkx_edge_labels(dg, pos=layout, font_color='b', edge_labels=labels, font_size=8)
    plt.show()


def main():
    currencies = create_currencies(5)
    g = create_graph(currencies)
    show_graph(g)


if __name__ == '__main__':
    main()

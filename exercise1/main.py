import sys
sys.path.append('../final-project')

from data_structures.cover_multi_way_search_tree import CoverMultiWaySearchTree
from data_structures.currency import Currency
from data_structures.heap_priority_queue import HeapPriorityQueue
from iso4217 import Currency as cur
from random import shuffle
from typing import Optional, Set
import argparse


def init_parameter():
    """
    Create argument parser.
    usage: main.py [-h] [-k K] [-c1 C1] [-c2 C2]
    (k, c1, c2)-cover for MultiWaySearchTree storing currency codes
    optional arguments:
      -h, --help  show this help message and exit
      -k K        the number of codes to cover at least
      -c1 C1      lower bound for the codes in the cover
      -c2 C2      upper bound for the codes in the cover
    :return: input arguments
    """
    parser = argparse.ArgumentParser(description='(k, c1, c2)-cover for MultiWaySearchTree storing currency codes')
    parser.add_argument("-k", type=int, default=1, help="the number of codes to cover at least")
    parser.add_argument("-c1", type=str, default='AAA', help="lower bound for the codes in the cover")
    parser.add_argument("-c2", type=str, default='ZZZ', help="upper bound for the codes in the cover")
    return parser.parse_args()


def build_tree(n=None) -> CoverMultiWaySearchTree:
    """
    Builds a CoverMultiWaySearchTree of n nodes with all the currency codes in the standard
    :return: a CoverMultiWaySearchTree
    """
    tree = CoverMultiWaySearchTree()
    codes = [currency.code for currency in cur]
    shuffle(codes)
    currencies = [Currency(code) for code in codes]
    if n is None:
        n = len(currencies)
    for currency in currencies[:n]:
        tree[currency._code] = currency
    return tree


def get_number_of_useful_items(nodes, a: str, b: str) -> int:
    """
    Find the number of items in nodes in range [a, b]
    :param nodes: the nodes to search in
    :param a: lower bound
    :param b: upper bound
    :return: the number of items in range [a, b]
    """
    return sum(int(a <= item.key <= b) for node in nodes for item in node.elements)


def compute_cover(tree: CoverMultiWaySearchTree,
                  k: int, c1: str, c2: str) -> Optional[Set[CoverMultiWaySearchTree.Position.Node]]:
    """
    Tries to compute the (k, c1, c2)-cover of tree with the minimum number of nodes.
    It follows a greedy-like appraoch.
    :param tree: the tree to cover
    :param k: the number of codes to cover at least
    :param c1: lower bound for the codes in the cover
    :param c2: upper bound for the codes in the cover
    :return: the (k, c1, c2)-cover of tree found if exists, None otherwise
    """
    # Step 1: Find nodes useful for the (k, c1, c2)-cover
    nodes = tree.find_nodes_in_range(c1, c2)

    # Step 2: Count number of items in range [c1, c2]
    n = get_number_of_useful_items(nodes, c1, c2)

    # Step 3: Compare with k
    if not n >= k:
        return None

    # Step 4: Sort nodes by number of useful items
    pq = HeapPriorityQueue(contents=[(get_number_of_useful_items([node], c1, c2), node) for node in nodes])

    # Step 5: Greedy approach - Use the node with the maximum number of useful items TODO change list into set
    cover = set()
    while k > 0:
        useful_items, node = pq.remove_max()
        k -= useful_items
        cover.add(node)
    return cover


def main(k, c1, c2):
    # Build the tree
    tree = build_tree()

    # Compute cover
    cover = compute_cover(tree, k, c1, c2)
    if cover is None:
        print(f"({k}, {c1}, {c2})-cover does not exist")
        return
    for node in cover:
        print(node, get_number_of_useful_items([node], c1, c2))  # TODO do not print second parameter
    print(f"({k}, {c1}, {c2})-cover is {len(cover)} node{'s' if len(cover) > 1 else ''} long")


if __name__ == '__main__':
    args = init_parameter()
    main(args.k, args.c1.upper(), args.c2.upper())

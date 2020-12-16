from data_structures.multi_way_search_tree import MultiWaySearchTree
from data_structures.currency import Currency
from iso4217 import Currency as cur
from random import shuffle


def main():
    tree = MultiWaySearchTree()
    codes = [currency.code for currency in cur]
    shuffle(codes)
    currencies = [Currency(code) for code in codes]
    for currency in currencies:
        tree[currency._code] = currency
    print(tree)
    print(len(tree))


if __name__ == '__main__':
    main()

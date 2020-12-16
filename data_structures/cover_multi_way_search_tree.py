from data_structures.multi_way_search_tree import MultiWaySearchTree
from typing import Set
from utils import binary_search


class CoverMultiWaySearchTree(MultiWaySearchTree):

    def find_nodes_in_range(self, start: str, stop: str) -> Set[MultiWaySearchTree.Position.Node]:
        retval = set()
        if not self.is_empty():
            if start is None:
                # If start is None, then the first item to yield is the first item of the tree
                p = self.first()
                item = p.elements[0]
            else:
                # Search for the smallest key >= start
                found, p, i = self._subtree_search(self.root(), start)
                if found:
                    item = p.elements[i]
                else:
                    p, item = self._subtree_find_gt(p, start, i)
            while p is not None and (stop is None or item.key <= stop):
                retval.add(p.node)
                _, i = binary_search(p.keys(), item.key)
                p, item = self._subtree_find_gt(p, item.key, i + 1)
        return retval

from math import ceil
from typing import Tuple, List, Optional, Iterator, Set

from .map_base import MapBase
from .tree import Tree

from utils import binary_search


class MultiWaySearchTree(Tree, MapBase):
    """
    Sorted map implementation using a multi-way seach tree, with parametrizable dimensions.
    """

    # ------------------------------- NESTED Position CLASS -------------------------------

    class Position(Tree.Position):
        """
        An abstraction representing the location of a single element within a tree.
        Note that two position instaces may represent the same inherent location in a tree.
        Therefore, users should always rely on syntax 'p == q' rather than 'p is q' when testing
        equivalence of positions.
        """

        # -------------------------- NESTED Node CLASS --------------------------

        class Node:
            """
            Lightweight, nonpublic class for storing a node.
            a is the minimum number of children for each node, thus the minimum number of keys for each node is a - 1
            b is the maximum number of children for each node, thus the maximum number of keys for each node is b - 1
            elements is a list of Item: Item is a (key-value) pair
            parent is the node's parent
            children is a list of _Node, i.e. links to the node's children
            """

            # ------------------------------- NESTED Item CLASS -------------------------------

            class Item(MapBase._Item):
                """Lightweight composite to store key-value pairs as map items."""

                @property
                def key(self):
                    return self._key

                @property
                def value(self):
                    return self._value

                @value.setter
                def value(self, v):
                    self._value = v

                def __repr__(self) -> str:
                    """Returns the string representation of an Item: (key-value)"""
                    return repr({self.key: self.value})

            # -------------------------- Node CLASS CONSTRUCTOR --------------------------

            __slots__ = '_a', '_b', '_elements', '_parent', '_children'

            def __init__(self, a: int, b: int, elements: List[Item], parent=None, children=None):
                if elements is None or not a - 1 <= len(elements) <= b - 1:
                    raise ValueError(f"Size of elements must be in [{a - 1}, {b - 1}]. "
                                     f"Found {len(elements) if elements is not None else None}")
                if parent is not None and not isinstance(parent, type(self)):
                    raise TypeError(f"parent is not of type {type(self)}")
                self._a = a
                self._b = b
                self._elements = elements
                self._parent = parent
                self._children = children if children is not None else [None] * (len(self._elements) + 1)
                for child in self._children:
                    if child is not None:
                        child.parent = self

            @property
            def a(self):
                return self._a

            @property
            def b(self):
                return self._b

            @property
            def elements(self):
                return self._elements

            @property
            def parent(self):
                return self._parent

            @property
            def children(self):
                return self._children

            @elements.setter
            def elements(self, value):
                self._elements = value

            @parent.setter
            def parent(self, value):
                self._parent = value

            def __repr__(self) -> str:
                """Returns the string representation of the Node."""
                return repr(self.elements)

            def __len__(self) -> int:
                """Returns the number of items in this node."""
                return len(self.elements)

        # -------------------------- Position CLASS CONSTRUCTOR --------------------------

        __slots__ = '_container', '_node'

        def __init__(self, container: "MultiWaySearchTree", node: Node):
            """Constructor should not be invoked by user."""
            self._container = container
            self._node = node

        @property
        def container(self):
            return self._container

        @property
        def node(self):
            return self._node

        @property
        def elements(self):
            return self.node.elements

        def element(self) -> List[Node.Item]:
            """Return the element stored at this Position."""
            return self.elements

        def keys(self) -> List[type(Node.Item.key)]:
            """Return key of map's key-value pair."""
            return [item.key for item in self.elements]

        def values(self) -> List[type(Node.Item.value)]:
            """Return value of map's key-value pair."""
            return [item.value for item in self.elements]

        def __eq__(self, other) -> bool:
            """Return True if other is a Position representing the same location."""
            return type(other) is type(self) and other.node is self.node

        def __repr__(self) -> str:
            """Returns the string representation of the Position"""
            return repr(self._node)

        def is_empty(self) -> bool:
            """Returns True if this position contains no elements, False otherwise."""
            return len(self) == 0

        def is_overflow(self) -> bool:
            """Returns True is this position is in overflow, False otherwise."""
            return len(self) > self._node.b - 1

        def is_underflow(self) -> bool:
            """Returns True if this position is in underflow, False otherwise."""
            return len(self) < self._node.a - 1

        def __len__(self) -> int:
            """Returns the number of items in this position."""
            return len(self.elements)

    # ------------------------------- UTILITY METHODS -------------------------------

    def _validate(self, p: Position) -> Position.Node:
        """Return associated node, if position is valid."""
        if not isinstance(p, self.Position):
            raise TypeError('p must be proper Position type')
        if p.container is not self:
            raise ValueError('p does not belong to this container')
        if p.node.parent is p.node:  # convention for deprecated nodes
            raise ValueError('p is no longer valid')
        return p.node

    def _make_position(self, node: Position.Node) -> Position:
        """Return Position instance for given node (or None if no node)."""
        return self.Position(self, node) if node is not None else None

    # ------------------------------- CLASS CONSTRUCTOR -------------------------------

    __slots__ = '_a', '_b', '_root', '_size'

    def __init__(self, a=2, b=8):
        """
        Constructor
        :param a: minimum number of children of each node
        :param b: maximum number of children of each node
        """
        if not 2 <= a <= ceil((b - 1) / 2):
            raise ValueError(f"a must be in [2, {ceil((b - 1) / 2)}]. Found {a}")
        self._a = a
        self._b = b
        self._root = None
        self._size = 0

    # -------------------------- PRIVATE METHODS --------------------------

    def _subtree_iter(self, p: Position) -> Iterator[Position.Node.Item]:
        """Generate an iteration of all elements in the subtree rooted at p."""
        if self.is_leaf(p):
            for e in p.elements:
                yield e
        else:
            for i, child in enumerate(self.children(p)):
                for other in self._subtree_iter(child):
                    yield other
                if i < len(p):
                    yield p.elements[i]

    def _add_root(self, e: Position.Node.Item) -> Optional[Position]:
        """
        Places element e at the root of an empty tree and return new Position.
        Raise ValueError if tree is non-empty.
        """
        if self._root is not None:
            raise ValueError('Root exists')
        self._size = 1
        self._root = self.Position.Node(self._a, self._b, [e])
        return self._make_position(self._root)

    def _subtree_search(self, p: Position, k: type(Position.Node.Item.key)) -> Tuple[bool, Position, int]:
        """
        Searches key k in the subtree rooted at p.
        Returns:
            True if k is found, False otherwise
            Position of p's subtree having key k,
            index of the key k in the keys list of the position,
            or last node and index searched.
        """
        # Validate
        node = self._validate(p)
        # Binary-search k in node p
        found, index = binary_search(p.keys(), k)
        # Successful search
        if found:
            return True, p, index
        # Next position to search in is the child next to p.keys()[index]
        next_position = self._make_position(node.children[index + 1])
        # If this child does not exist, the search is unsuccessful
        if next_position is None:
            return False, p, index + 1
        return self._subtree_search(next_position, k)

    def _subtree_min(self, p: Position) -> Tuple[Position, type(Position.Node.Item.key)]:
        """
        Returns the Position with smallest key in the subtree rooted at p, and the key itself.
        :param p: the root of the subtree
        :return:
            Position with the smallest key in the subtree rooted at p
            The smallest key in the subtree rooted at p
        """
        # Validate
        node = self._validate(p)
        # The smallest key must be in the subtree rooted at the first child of p, if this child exists
        if node.children[0] is not None:
            return self._subtree_min(self._make_position(node.children[0]))
        return p, p.elements[0].key

    def _subtree_max(self, p: Position) -> Tuple[Position, type(Position.Node.Item.key)]:
        """
        Returns the Position with greatest key in the subtree rooted at p, and the key itself.
        :param p: the root of the subtree
        :return:
            Position with the greatest key in the subtree rooted at p
            The greatest key in the subtree rooted at p
        """
        # Validate
        node = self._validate(p)
        # The greatest key must be in the subtree rooted at the last child of p, if this child exists
        if node.children[-1] is not None:
            return self._subtree_max(self._make_position(node.children[-1]))
        return p, p.elements[-1].key

    def _subtree_find_lt(self, p: Position, k: type(Position.Node.Item.key), i: int) ->\
            Tuple[Optional[Position], Optional[Position.Node.Item]]:
        """
        Returns the element with the largest key that is < k in the subtree rooted at p.
        k is supposed to be the i-th key in p.
        """
        # If p is an in internal node
        if not self.is_leaf(p):
            # Then the key less than k is the maximimum in key in the subtree rooted at the child to the left of k
            p, _ = self._subtree_max(self._make_position(p.node.children[i]))
            return p, p.elements[-1]
        else:  # If p is a leaf
            # If k is not the first key in p
            if i > 0:
                # Return the key to the left of k
                return p, p.elements[i - 1]
            # If k is the first key in p, we go up
            walk = p
            # We go up until walk is the first child of its parent (above)
            above = self.parent(walk)
            # We stop when we reach the root
            while above is not None and walk == list(self.children(above))[0]:
                # If none of the two conditions is met yet, keep going up
                walk = above
                above = self.parent(walk)
            # If we reached the root
            if above is None:
                # We have to return a key of root
                _, i = binary_search(walk.keys(), k)
                # If k is not smaller than all the keys in the root
                if i >= 0:
                    # Then return the greatest key smaller than k (easy because of the implementation of binary_search)
                    return walk, walk.elements[i]
                else:
                    # If k is smaller than all the keys in the root, then no "less then" exists
                    return None, None
            # If we didn't reach the root
            _, i = binary_search(above.keys(), k)
            # Just return the greatest key in above smaller than key
            return above, above.elements[i]

    def _subtree_find_gt(self, p: Position, k: type(Position.Node.Item.key), i: int) ->\
            Tuple[Optional[Position], Optional[Position.Node.Item]]:
        """
        Returns the position and the element with the smallest key that is > k in the subtree rooted at p.
        k is supposed to be the i-th key in p.
        """
        # If p is an in internal node
        if not self.is_leaf(p):
            # Then the key greater than k is the minimum in key in the subtree rooted at the child to the right of k
            p, _ = self._subtree_min(self._make_position(p.node.children[i]))
            return p, p.elements[0]
        else:  # If p is a leaf
            # If k is not the last key in p
            if i < len(p):
                # Return the key to the right of k
                return p, p.elements[i]
            # If k is the last key in p, we go up
            walk = p
            # We go up until walk is the last child of its parent (above)
            above = self.parent(walk)
            # We stop when we reach the root
            while above is not None and walk == list(self.children(above))[-1]:
                # If none of the two conditions is met yet, keep going up
                walk = above
                above = self.parent(walk)
            # If we reached the root
            if above is None:
                # We have to return a key of root
                _, i = binary_search(walk.keys(), k)
                # If k is not greater than all the keys in the root
                if i < len(walk) - 1:
                    # Then return the smallest key greater than k (increment the return value of binary_search)
                    return walk, walk.elements[i + 1]
                else:
                    # If k is greater than all the keys in the root, then no "greater then" exists
                    return None, None
            # If we didn't reach the root
            _, i = binary_search(above.keys(), k)
            # Just return the smallest key in above greater than key
            return above, above.elements[i + 1]

    def _subtree_repr(self, p: Position, level: int, children_counter: int) -> str:
        """Returns the string representation of the subtree rooted at p"""
        if self.is_empty():
            return "[]"
        string = ""
        self._validate(p)
        if level == 0:
            num_children = self.num_children(p)
            if num_children == 0:
                string += f"{'  ' * level}level {level}, size {len(p)}:  {p}\n"
            else:
                string += f"{'  ' * level}level {level}, size {len(p)}:  {p}, {num_children} children:\n"
        else:
            num_children = self.num_children(p)
            if num_children == 0:
                string += f"{'  ' * level}level {level}, child {children_counter}, size {len(p)}:  {p}\n"
            else:
                string += f"{'  ' * level}level {level}, child {children_counter}, size {len(p)}:  {p}, " \
                          f"{self.num_children(p)} children:\n"
        children_counter = 0
        for child in self.children(p):
            string += self._subtree_repr(child, level + 1, children_counter)
            children_counter += 1
        return string

    def _split(self, p: Position) -> Tuple[Position.Node, Position.Node.Item, Position.Node]:
        """
        Splits p in smaller node, median item and bigger node
        :param p: position to split
        :return:
            smaller node: Node: position with keys smaller than median key
            median item: Item: item with median key and value
            bigger node: Node: position with keys bigger than median key
        """
        # Validate
        node = self._validate(p)
        # Consider the keys and the values saved in node p
        keys, values = p.keys()[:], p.values()[:]
        # We split keys and values in three parts:
        #   the median key (km) and median value (vm),
        #   keys and values smaller than the km and vm (ks and vs),
        #   and keys and values larger than the km and vm (kb and vb)
        median = len(keys) // 2
        km, vm = keys[median], values[median]
        ks, vs = keys[:median], values[:median]
        kb, vb = keys[median + 1:], values[median + 1:]
        # With ks and vs we create a new node
        smaller_node = self.Position.Node(self._a, self._b, [self.Position.Node.Item(k, v) for k, v in zip(ks, vs)])
        # smaller_node must keep all the children of p from index 0 to median
        for j in range(median + 1):  # j parses all children of smaller_node: they are median + 1
            smaller_node.children[j] = node.children[j]
            if node.children[j] is not None:
                node.children[j].parent = smaller_node
        # With kb and vb we create a new node
        bigger_node = self.Position.Node(self._a, self._b, [self.Position.Node.Item(k, v) for k, v in zip(kb, vb)])
        # bigger_node must keep all the children of p from index median + 1
        for j in range(median):  # j parses all children of bigger_node: they are median
            bigger_node.children[j] = node.children[median + 1 + j]
            if node.children[median + 1 + j] is not None:
                node.children[median + 1 + j].parent = bigger_node
        return smaller_node, self.Position.Node.Item(km, vm), bigger_node

    def _left_transfer(self, v: Position, w: Position) -> None:
        """
        Resolves v's underflow with a transfer with the left sibling of v, i.e. w
        :param v: the Position of the node in underflow
        :param w: the left sibling of v
        :return: None
        """
        # Validate
        v_node = self._validate(v)
        w_node = self._validate(w)
        # Let k' be the key saved in the parent p that is between the keys contained in w and v
        p = self.parent(v)
        # Since w is the left sibling of v, the binary search will return the index of the key to the left of k'
        _, index = binary_search(p.keys(), w_node.elements[0].key)
        # So, we increment index
        index = index + 1
        # Let new_item be the Item in p with key k'
        new_item = p.elements[index]
        # Let k'' be the largest key saved in w
        # Let rightmost_item be the item in w with key k''
        rightmost_item = w_node.elements[-1]
        # Let rightmost_child be the node child of w to the right of k''
        rightmost_child = w_node.children[-1]
        # Add k' in v
        v_node.elements = [new_item] + v_node.elements
        # w transfered rightmost_item to v, so v keeps rightmost_child to its left, since w is the left sibling of v
        v_node._children = [rightmost_child] + v_node.children
        if rightmost_child is not None:
            rightmost_child.parent = v_node
        # Delete k'' from w
        w_node.elements.pop()
        # Also delete the rightmost child
        w_node.children.pop()
        # Replace k' with k'' in p
        p.elements[index] = rightmost_item

    def _right_transfer(self, v: Position, w: Position) -> None:
        """
        Resolves v's underflow with a transfer with the right sibling of v, i.e. w
        :param v: the Position of the node in underflow
        :param w: the right sibling of v
        :return: None
        """
        # Validate
        v_node = self._validate(v)
        w_node = self._validate(w)
        # Let k' be the key saved in the parent p that is between the keys contained in w and v
        p = self.parent(v)
        # Since w is the right sibling of v, the binary search will return the index of k'
        _, index = binary_search(p.keys(), w_node.elements[0].key)
        # Let new_item be the Item in p with key k'
        new_item = p.elements[index]
        # Let k'' be the smallest key saved in w
        # Let leftmost_item be the item in w with key k''
        leftmost_item = w_node.elements[0]
        # Let leftmost_child be the node child of w to the left of k''
        leftmost_child = w_node.children[0]
        # Delete k from v, and add k' in v
        v_node._elements = v_node.elements + [new_item]
        # w transfered leftmost_child to v, so v keeps leftmost_child to its right, since w is the right sibling of v
        v_node._children = v_node.children + [leftmost_child]
        if leftmost_child is not None:
            leftmost_child.parent = v_node
        # Delete k'' from w
        w_node.elements.pop(0)
        # Also delete the leftmost child
        w_node.children.pop(0)
        # Replace k' with k'' in p
        p.elements[index] = leftmost_item

    def _transfer(self, v: Position, w: Position, left=True) -> None:
        """
        Resolves v's underflow with a transfer with the sibling of v, i.e. w
        :param v: the Position of the node in underflow
        :param w: the sibling of v
        :param left: Whether w is the left sibling of v (default True)
        :return: None
        """
        # Validate
        self._validate(v)
        self._validate(w)
        # Perform the correct transfer
        self._left_transfer(v, w) if left else self._right_transfer(v, w)

    def _fusion(self, v: Position, w: Position, left=True) -> Position:
        """
        Resolves v's underflow with a fusion with the sibling of v, i.e. w
        :param v: the Posiion of the node in underflow
        :param w: the sibling of v
        :param left: Whether w is the left sibling of v (default True)
        :return: the new node as the result of the fusion between v and w
        """
        # Validate
        v_node = self._validate(v)
        w_node = self._validate(w)
        # Let p be the parent of v and w
        p = self.parent(v)
        # Let k' be the key saved in p in between the keys of v and w
        _, index = binary_search(p.keys(), w_node.elements[0].key)
        # If w is the left sibling of v, the binary search will return the index of the key to the left of k'
        if left:
            index = index + 1
        # Let new_item be the Item in p with key k'
        new_item = p.elements[index]
        # Create a new node containing all keys of v except k, all keys of w and key k'
        new_node = self.Position.Node(self._a, self._b,
                                      w_node.elements + [new_item] + v_node.elements if left else
                                      v_node.elements + [new_item] + w_node.elements,
                                      parent=p.node,
                                      children=w_node.children + v_node.children if left else
                                      v_node.children + w_node.children)
        # Remove new_item from p
        p.elements.pop(index)
        # Also remove the child to the right of k'
        p.node.children.pop(index)
        # Substitute that child with new_node
        p.node.children[index] = new_node
        # v and w do not belong to the tree anymore
        v = w = None
        return self._make_position(new_node)

    # -------------------------- PUBLIC METHODS --------------------------

    # -------------------------- ADT TREE INTERFACE METHODS --------------------------

    # -------------------------- ACCESS METHODS --------------------------

    def root(self) -> Optional[Position]:
        """Return the root Position of the tree (or None if tree is empty)."""
        return self._make_position(self._root)

    def parent(self, p: Position) -> Optional[Position]:
        """Return the Position of p's parent (or None if p is root)."""
        node = self._validate(p)
        return self._make_position(node.parent)

    def children(self, p: Position) -> Iterator[Position]:
        """Generate an iteration of Positions representing p's children."""
        node = self._validate(p)
        for child in node.children:
            if child is not None:
                yield self._make_position(child)

    def num_children(self, p: Position) -> int:
        """Return the number of children that Position p has."""
        self._validate(p)
        return len(list(self.children(p)))

    def first(self) -> Optional[Position]:
        """Returns the first postion in the tree (or None if the tree is empty)."""
        return self._subtree_min(self.root())[0] if not self.is_empty() else None

    def last(self) -> Optional[Position]:
        """Returns the last position in the tree (or None if the tree is empty)."""
        return self._subtree_max(self.root())[0] if not self.is_empty() else None

    def left_sibling(self, p: Position, k: type(Position.Node.Item.key) = None) -> Optional[Position]:
        """Returns the Position of the node to the left of p"""
        # Validate
        self._validate(p)
        # Let parent be the parent of p
        parent = self.parent(p)
        if k is None:
            k = p.elements[0].key
        _, i = binary_search(parent.keys(), k)
        if i < 0:  # p is the leftmost child of parent
            return None  # left sibling of p does not exist
        return self._make_position(parent.node.children[i])

    def right_sibling(self, p: Position, k: type(Position.Node.Item.key) = None) -> Optional[Position]:
        """Returns the Position of the node to the right of p"""
        # Validate
        self._validate(p)
        # Let parent be the parent of p
        parent = self.parent(p)
        if k is None:
            k = p.elements[0].key
        _, i = binary_search(parent.keys(), k)
        if i >= len(parent) - 1:  # p is the rightmost child of parent
            return None  # right sibling of p does not exist
        return self._make_position(parent.node.children[i + 2])

    # -------------------------- GENERIC METHODS --------------------------

    def __len__(self) -> int:
        """Return the total number of elements in the tree."""
        return self._size

    def __iter__(self) -> Iterator[Position.Node.Item]:
        """Generate an inorder iteration of the tree's elements."""
        if not self.is_empty():
            return self._subtree_iter(self.root())

    def __repr__(self) -> str:
        """Returns the string representation of the tree, level by level."""
        return self._subtree_repr(self.root(), 0, 0)

    # -------------------------- ADT MAP INTERFACE METHODS --------------------------

    def __getitem__(self, k: type(Position.Node.Item.key)) -> type(Position.Node.Item.value):
        """Return value associated with key k (raise KeyError if not found)."""
        # If the tree is empty, k is not in the tree
        if self.is_empty():
            raise KeyError('Key Error: ' + repr(k))
        else:
            # Search for the node p that should contain k
            found, p, i = self._subtree_search(self.root(), k)
            # If no node is found, k is not in the tree
            if not found:
                raise KeyError('Key Error: ' + repr(k))
            return p.elements[i].value

    def __setitem__(self, k: type(Position.Node.Item.key), v: type(Position.Node.Item.value)) -> None:
        """
        Inserts a new (key-value) item in the tree
        :param k: the key of the item to insert
        :param v: the value of the item to insert
        :return: None
        """
        if self.is_empty():
            # If the tree is empty, we add a root
            leaf = self._add_root(self.Position.Node.Item(k, v))
        else:
            # Search for the node p that should contain k
            found, p, i = self._subtree_search(self.root(), k)
            if not found:  # k is not in the tree, insert (k,v) in the tree
                # Pointer to the left split of p (it'll stay None if p is a leaf)
                smaller_node = None
                # Pointer to the right split of p (it'll stay None if p is a leaf)
                bigger_node = None
                # Check if we reached the root
                while p is not None:
                    node = p.node
                    # To mantain p keys ordered, we have to move keys from index i
                    node.elements = node.elements[:i] + [self.Position.Node.Item(k, v)] + node.elements[i:]
                    # We also have to move the children from index i + 1, adding the result of the split
                    node._children = node.children[:i] + [smaller_node, bigger_node] + node.children[i + 1:]
                    # After the insert, an overflow can occurr
                    if p.is_overflow():
                        # Split p, solving its overflow
                        smaller_node, median_item, bigger_node = self._split(p)
                        # We have to insert median_item in the parent of p, so we prepare k, v for a new operation
                        k, v = median_item.key, median_item.value
                        # We move to the parent: it could experience another overflow itself
                        p = self.parent(p)
                        # Check if we reached the root
                        if p is None:
                            # A new root is created
                            self._root = self.Position.Node(self._a, self._b, [self.Position.Node.Item(k, v)])
                            root = self._make_position(self._root)
                            # the left child of the new root is smaller_node
                            root.node.children[0] = smaller_node
                            smaller_node.parent = self._root
                            # the right child of the new root is bigger_node
                            root.node.children[1] = bigger_node
                            bigger_node._parent = self._root
                        else:
                            # If parent of p exists, we have to perform another insert
                            smaller_node.parent = p.node
                            bigger_node.parent = p.node
                            # Search where to insert k in p
                            _, i = binary_search(p.keys(), k)
                            i += 1
                    else:
                        # p is not in overflow, insertion completed
                        break
                # Increment the tree size
                self._size += 1
            else:
                # k is in p at index i, substitute old value with v
                p.elements[i].value = v

    def __delitem__(self, k: type(Position.Node.Item.key)) -> None:
        """Remove item associated with key k (raise KeyError if not found)."""
        # If the tree is empty, k is not in the tree
        if not self.is_empty():
            # Search for the node p that should contain k
            found, p, i = self._subtree_search(self.root(), k)
            # If no node is found, k is not in the tree
            if found:
                # If the tree consists in the root only
                if self.is_leaf(self.root()):
                    # Then we can remove k
                    self.root().elements.pop(i)
                    # Also remove the child to the right of k
                    self._root.children.pop(i)
                    # Remember to reduce the size
                    self._size -= 1
                    # Now the tree could be empty
                    if self.is_empty():
                        # The root does not exist anymore
                        self._root = None
                    # The deletion ends
                    return
                # Since underflow can propagate upwards, we perform a while cycle
                while True:
                    # If p is not in underflow, we can delete k safely
                    if not p.is_underflow():
                        # If p is a leaf, we can remove k directly from p itself
                        if self.is_leaf(p):
                            # Delete the item at index i
                            p.elements.pop(i)
                            # Delete the corresponding child to the right of k
                            p.node.children.pop(i + 1)
                            # If we didn't cause an underflow with the deletion, the cycle stops
                            if not p.is_underflow():
                                break
                        else:  # If p is not a leaf, we swap k with a key in a leaf
                            # Let ps be the position with smallest key in the subtree to the right of k
                            ps, k = self._subtree_min(self._make_position(p.node.children[i + 1]))
                            # Replace the item with key k with the first item of ps
                            temp = p.elements[i]
                            p.elements[i] = ps.elements[0]
                            ps.elements[0] = temp
                            # Delete the first item of ps
                            p = ps
                            i = 0
                    else:
                        # If the node w on the left of v has more than a - 1 items, then perform a left-transfer
                        w = self.left_sibling(p, k)
                        if w is not None and len(w) > self._a - 1:
                            self._transfer(p, w, left=True)
                            break
                        # If the node w on the right of v has more than a - 1 items, then perform a right-transfer
                        w = self.right_sibling(p, k)
                        if w is not None and len(w) > self._a - 1:
                            self._transfer(p, w, left=False)
                            break
                        # Otherwise perform a fusion
                        # Let w be the node on the left (or on the right) of v
                        w = self.left_sibling(p, k)
                        if w is not None:
                            # Let f be the result of the fusion between v and w
                            f = self._fusion(p, w, left=True)
                        else:
                            w = self.right_sibling(p, k)
                            f = self._fusion(p, w, left=False)
                        # Since we can cause an underflow upwards, continue the cycle with the parent of f
                        p = self.parent(f)
                        # If another underflow does not occur, we can stop
                        if not p.is_underflow():
                            break
                        # If we ended up to the root, and the root itself is in underflow, then f is the new root!
                        if self.is_root(p) and p.is_underflow():
                            self._root = f.node
                            break
                # Decrement the tree size
                self._size -= 1
                return
        raise KeyError('Key Error: ' + repr(k))

    def clear(self) -> None:
        """Removes all the pairs key-value present in the tree."""
        self._root = None
        self._size = 0

    def get(self, k: type(Position.Node.Item.key),
            d: type(Position.Node.Item.value) = None) -> type(Position.Node.Item.value):
        """Returns the value associated to key k if present, otherwise it returns d."""
        try:
            return self[k]
        except KeyError:
            return d

    def setdefault(self, k: type(Position.Node.Item.key),
                   d: type(Position.Node.Item.value) = None) -> type(Position.Node.Item.value):
        """Returns the value associated to key if present, otherwise it makes self[k]=d and returns d."""
        try:
            return self[k]
        except KeyError:
            self[k] = d
            return d

    def pop(self, k: type(Position.Node.Item.key),
            d: type(Position.Node.Item.value) = None) -> type(Position.Node.Item.value):
        """Returns self[k] and deletes the pair if present, otherwise it returns d."""
        found, p, i = self._subtree_search(self.root(), k)
        if found:
            v = p.elements[i]
            del self[k]
            return v
        else:
            return d

    def popitem(self) -> Position.Node.Item:
        """Returns an arbitrary pair (k, v) and deletes it from the map. It throws an exception if the tree is empty."""
        item = self.last().elements[-1]
        k = item.key
        if k is None:
            raise Exception("Tree is empty")
        del self[k]
        return item

    def keys(self) -> Set[type(Position.Node.Item.key)]:
        """Returns a set-like view of all keys in the tree."""
        s = set()
        for item in self:
            s.add(item.key)
        return s

    def values(self) -> Set[type(Position.Node.Item.value)]:
        """Returns a set-like view of all values in the tree."""
        s = set()
        for item in self:
            s.add(item.value)
        return s

    def items(self) -> Set[Position.Node.Item]:
        """Returns a set-like view of all the (k, v) tuples in the tree."""
        s = set()
        for item in self:
            s.add((item.key, item.value))
        return s

    def __eq__(self, other) -> bool:
        """Returns True if the tree contains same pairs as other."""
        if not isinstance(other, type(self)):
            raise TypeError(f"other is not of type {type(self)}")
        for s, o in zip(self, other):
            if s.key != o.key or s.value != o.value:
                return False
        return True

    def __ne__(self, other) -> bool:
        """Returns True if the tree does not contain same pairs as other."""
        return not self == other

    def update(self, other, **kwargs) -> None:
        """For each pairs (k, v) in other sets self[k] = v."""
        if not isinstance(other, type(self)):
            raise TypeError(f"other is not of type {type(self)}")
        for item in other:
            self[item.key] = item.value

    # -------------------------- ADT SORTED MAP INTERFACE METHODS --------------------------

    def find_min(self) -> Optional[Position.Node.Item]:
        """Returns the element with the smallest key."""
        return self._subtree_min(self.root())[0].elements[0] if not self.is_empty() else None

    def find_max(self) -> Optional[Position.Node.Item]:
        """Returns the element with the greatest key."""
        return self._subtree_max(self.root())[0].elements[-1] if not self.is_empty() else None

    def find_lt(self, k: type(Position.Node.Item.key)) -> Optional[Position.Node.Item]:
        """Returns the element with the largest key that is < k."""
        if self.is_empty():
            return None
        found, p, i = self._subtree_search(self.root(), k)
        return self._subtree_find_lt(p, k, i)[1]

    def find_le(self, k: type(Position.Node.Item.key)) -> Optional[Position.Node.Item]:
        """Returns the element with the largest key that is <= k."""
        if self.is_empty():
            return None
        found, p, i = self._subtree_search(self.root(), k)
        # If k is found, we need to search in the child of p to the left of k
        if found:
            return p.elements[i]
        return self._subtree_find_lt(p, k, i)[1]

    def find_gt(self, k: type(Position.Node.Item.key)) -> Optional[Position.Node.Item]:
        """Returns the element with the smallest key that is > k."""
        if self.is_empty():
            return None
        found, p, i = self._subtree_search(self.root(), k)
        # If k is found, we need to search in the child of p to the right of k
        if found:
            i += 1
        return self._subtree_find_gt(p, k, i)[1]

    def find_ge(self, k: type(Position.Node.Item.key)) -> Optional[Position.Node.Item]:
        """Returns the element with the smallest key that is >= k."""
        if self.is_empty():
            return None
        found, p, i = self._subtree_search(self.root(), k)
        if found:
            return p.elements[i]
        return self._subtree_find_gt(p, k, i)[1]

    def find_range(self, start: type(Position.Node.Item.key) = None,
                   stop: type(Position.Node.Item.key) = None) -> Iterator[Position.Node.Item]:
        """Returns all the elements with (key, value) such that start <= key < stop."""
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
            while p is not None and (stop is None or item.key < stop):
                yield item
                _, i = binary_search(p.keys(), item.key)
                p, item = self._subtree_find_gt(p, item.key, i + 1)

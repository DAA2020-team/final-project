from .hash_map_base import HashMapBase
from .map_base import MapBase

from utils import bitify, load_primes, binary_search


class DoubleHashingHashMap(HashMapBase):

    __slots__ = '_z', '_q', '_load_factor', '_collision_counter', '_count_collisions', '_is_resizing'

    _AVAIL = object()  # sentinal marks locations of previous deletions
    _MIN_CAPACITY = 17

    # --------------- NESTED _Item CLASS ---------------

    class _Item(MapBase._Item):

        def __repr__(self):
            """
            Returns the string representation of the item.
            :return: string representation of the item
            """
            return "{%s: %s}" % (self._key, self._value)

    # --------------- CONSTRUCTOR ---------------

    def __init__(self, cap=_MIN_CAPACITY, z=92821, p=109345121, q=13, load_factor_range=(0.2, 0.5)):
        """
        Constructor.
        :param cap: Initial capacity of the HashMap
        :param z: Positive prime used for string hashing (default 92821)
        :param p: Positive prime used for MAD (default 109345121)
        :param q: Positive prime used for secondary hash function compression (default 13)
        """
        super().__init__(cap=cap, p=p)
        self._z = z
        self._q = q
        self._load_factor = load_factor_range
        self._collision_counter = 0
        self._count_collisions = False
        self._is_resizing = False

    # --------------- UTILITY METHODS ---------------

    def _hash_code(self, x):
        """
        Returns the polynomial hash code for string x
        :param x: string to hash
        :return: hash code of x
        """
        return sum(int(c) * self._z**k for k, c in enumerate(bitify(x)))

    def _h(self, x):
        """
        Primary hash function. Implements MAD compression
        :param x: key to hash
        :return: compressed primary hash code of x in [0, N - 1]
        """
        return (self._hash_code(x) * self._scale + self._shift) % self._prime % self.capacity()

    def _d(self, x):
        """
        Secondary hash function.
        :param x: key to hash
        :return: compressed secondary hash code of x in [1, q - 1]
        """
        return self._q - self._hash_code(x) % self._q

    # --------------- PUBLIC METHODS ---------------

    def __getitem__(self, k):
        """
        Returns the value associated to key k if it exists, otherwise it throws an exception.
        :param k: key to search
        :return: value associated to k
        """
        self._count_collisions = False
        j = self._h(k)
        return self._bucket_getitem(j, k)  # may raise KeyError

    def __setitem__(self, k, v):
        """
        Assigns value v to key k, overwriting the old value if k is already present.
        :param k: key to insert
        :param v: value associated to k
        :return: None
        """
        self._count_collisions = not self._is_resizing
        j = self._h(k)
        self._bucket_setitem(j, k, v)  # subroutine maintains self._n
        if self._n > self._load_factor[-1] * self.capacity():  # keep maximum load factor
            new_maximum_capacity = self.capacity() * self._load_factor[-1] / self._load_factor[0]
            new_capacity = (self.capacity() + new_maximum_capacity) // 2
            primes = load_primes()
            _, index = binary_search(primes, new_capacity)
            self._resize(primes[index])

    def __delitem__(self, k):
        """
        If k exists, deletes both key k and its value, otherwise it throws and exception.
        :param k: key to delete
        :return: None
        """
        self._count_collisions = False
        j = self._h(k)
        self._bucket_delitem(j, k)  # may raise KeyError
        self._n -= 1
        # keep minimum load factor
        if self._n < self._load_factor[0] * self.capacity() and self.capacity() > DoubleHashingHashMap._MIN_CAPACITY:
            new_minimum_capacity = self.capacity() * self._load_factor[0] / self._load_factor[-1]
            new_capacity = (self.capacity() + new_minimum_capacity) // 2
            primes = load_primes()
            _, index = binary_search(primes, new_capacity)
            self._resize(max(primes[index], DoubleHashingHashMap._MIN_CAPACITY))

    def clear(self):
        """
        Removes all the pairs key-value present.
        :return: None
        """
        self._table = DoubleHashingHashMap._MIN_CAPACITY * [None]
        self._n = 0
        self._collision_counter = 0

    def get(self, k, d=None):
        """
        Returns the value associated to key k if present, otherwise it returns d.
        :param k: key to search
        :param d: arbitrary value
        :return: value associated to k if present, otherwise d
        """
        try:
            return self[k]
        except KeyError:
            return d

    def setdefault(self, k, d=None):
        """
        Returns the value associated to key k if present, otherwise it makes self[k]=d and returns d.
        :param k: key to insert
        :param d: arbitrary value
        :return: value associated to k if present, otherwise d
        """
        try:
            return self[k]
        except KeyError:
            self[k] = d
            return d

    def pop(self, k, d=None):
        """
        Returns self[k] and deletes the pair if present, otherwise it returns d.
        :param k: key to delete
        :param d: arbitrary value
        :return: value associated to k if present, otherwise d
        """
        try:
            v = self[k]
            del self[k]
            return v
        except KeyError:
            return d

    def popitem(self):
        """
        Returns an arbitrary pair (k, v) and deletes it. It throws an exception if the map is empty.
        :return: arbitrary pair (k, v)
        """
        if self.is_empty():
            raise Exception("The map is empty!")
        for j in range(len(self._table)):  # scan entire table
            if not self._is_available(j):
                k, v = self._table[j]._key, self._table[j]._value
                self._table[j] = DoubleHashingHashMap._AVAIL
                self._n -= 1
                return k, v

    def __iter__(self):
        """
        Generates a sequence of keys.
        :return: a generator of all keys in the map
        """
        for j in range(len(self._table)):  # scan entire table
            if not self._is_available(j):
                yield self._table[j]._key

    def keys(self):
        """
        Returns a set-like view of all keys in the map.
        :return:  set-like view of all keys in the map
        """
        return set(self)

    def values(self):
        """
        Returns a set-like view of all values in the map.
        :return: set-like view of all values in the map
        """
        s = set()
        for key in self:
            s.add(self[key])
        return s

    def items(self):
        """
        Returns a set-like view of all (k, v) tuples in the map.
        :return: set-like view of all (k, v) tuples in the map
        """
        s = set()
        for key in self:
            s.add((key, self[key]))
        return s

    def __eq__(self, other):
        """
        Returns True if self contains the same pairs as other.
        :param other: another DoubleHashingHashMap
        :return: True if self contains the same pairs as other, False otherwise
        """
        return self.items() == other.items()

    def __ne__(self, other):
        """
        Returns True if self does not contain the same pairs as other.
        :param other: another DoubleHashingHashMap
        :return: True if self does not contain the same pairs as other, False otherwise
        """
        return not self == other

    def update(self, other, **kwargs):
        """
        For each pair (k, v) in other sets self[k] = v.
        :param other: another DoubleHashingHashMap
        :return: None
        """
        for k, v in other.items():
            self[k] = v

    def __repr__(self):
        """
        Returns the string representation of the map.
        :return: string representation of the map
        """
        return repr(self.items())

    def capacity(self):
        """
        Returns the current capacity of the table.
        :return: current capacity of the table
        """
        return len(self._table)

    def get_collisions(self):
        """
        Returns the number of collisions found during the lifetime of the map.
        :return: number of collisions found during the lifetime of the map
        """
        return self._collision_counter

    def is_empty(self):
        """
        Returns True if the map does not contain any key.
        :return: True if the map does not contain any key, False otherwise
        """
        return len(self) == 0

    # --------------- PRIVATE METHODS ---------------

    def _is_available(self, j):
        """Return True if index j is available in table."""
        return self._table[j] is None or self._table[j] is DoubleHashingHashMap._AVAIL

    def _find_slot(self, j, k):
        """Search for key k in bucket at index j.

        Return (success, index) tuple, described as follows:
        If match was found, success is True and index denotes its location.
        If no match found, success is False and index denotes first available slot.
        """
        previous_collisions = self._collision_counter
        firstAvail = None
        while True:
            if self._is_available(j):
                self._count_collisions = False
                if firstAvail is None:
                    firstAvail = j  # mark this as first avail
                if self._table[j] is None:
                    return False, firstAvail  # search has failed
            elif k == self._table[j]._key:
                self._collision_counter = previous_collisions
                return True, j  # found a match
            j = (j + self._d(k)) % self.capacity()  # keep looking (cyclically)
            if self._count_collisions:
                self._collision_counter += 1  # collision found. increment counter

    def _bucket_getitem(self, j, k):
        """
        Search for key k in bucket at index j and returns the value associated to k.
        :param j: index of the bucket
        :param k: key to search
        :return: value associated to k
        """
        found, s = self._find_slot(j, k)
        if not found:
            raise KeyError('Key Error: ' + repr(k))  # no match found
        return self._table[s]._value

    def _bucket_setitem(self, j, k, v):
        """
        Search for key k in bucket at index j and sets v as value associated to k.
        :param j: index of the bucket
        :param k: key to insert
        :param v: value associated to k
        :return: None
        """
        found, s = self._find_slot(j, k)
        if not found:
            self._table[s] = self._Item(k, v)  # insert new item
            self._n += 1  # size has increased
        else:
            self._table[s]._value = v  # overwrite existing

    def _bucket_delitem(self, j, k):
        """
        Search for key k in bucket at index j and deletes k.
        :param j: index of the bucket
        :param k: key to delete
        :return: None
        """
        found, s = self._find_slot(j, k)
        if not found:
            raise KeyError('Key Error: ' + repr(k))  # no match found
        self._table[s] = DoubleHashingHashMap._AVAIL  # mark as vacated

    def _resize(self, c):
        self._is_resizing = True
        super()._resize(c)
        self._is_resizing = False

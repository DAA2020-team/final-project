from data_structures.avl_tree import AVLTreeMap
from data_structures.double_hashing_hash_map import DoubleHashingHashMap
import utils as utils

from iso4217 import Currency as cur


class Currency:
    __slots__ = '_code', '_denominations', '_changes'

    def __init__(self, code):
        if utils.validate_iso_code(code) is False:
            raise ValueError("code is not a valid ISO4217 code")

        self._code = code
        self._denominations = AVLTreeMap()
        self._changes = DoubleHashingHashMap()

    def __repr__(self):
        return repr(self._denominations)

    @staticmethod
    def _raise_ex_if_code_not_valid(c):
        if utils.validate_iso_code(c) is False:
            raise ValueError("code is not a valid ISO4217 code")

    @staticmethod
    def _raise_ex_if_value_not_int_or_float(v):
        if type(v) is not float and type(v) is not int:
            raise ValueError("Value must be a float or integer and greater than 0, " + str(type(v)) + " was provided")

    def _raise_ex_if_den_empty(self):
        if self._denominations.is_empty():
            raise ValueError("No denomination present")

    def get_change(self, currency_code):
        self._raise_ex_if_code_not_valid(currency_code)
        return self._changes[currency_code]

    def add_denomination(self, value):
        """
        Add value in the Denominations map. It raises an exception
        if value is already present
        :param value: the denomimnation to add
        :return: None
        :raises ValueError: if denomination is already present
        :raises ValueError: if denomination is not an integer or a float
        """
        self._raise_ex_if_value_not_int_or_float(value)
        try:
            _ = self._denominations[value]
        except KeyError:
            self._denominations[value] = value
            return
        raise ValueError(str(value) + " is already present")

    def del_denomination(self, value):
        """
        Remove value from the Denominations map. It raises an
        exception if value is not present
        :param value: denomination to remove
        :return: None
        :raises KeyError: if denominations is not present
        :raises ValueError: if denomination is not an integer or a float
        """
        self._raise_ex_if_value_not_int_or_float(value)
        del self._denominations[value]

    def min_denomination(self, value=None):
        """
        The parameter value is optional. If it is not given, it returns
        the minimum denomination (it raises an exception if no denomination exists), otherwise
        it returns the minimum denomination larger than value (it raises an exception if no
        denomination exists larger than value)
        :param value: see return
        :return: the smaller denomination greater than the given denomination, if provided,
            else the smaller denomination
        :raises ValueError: if there isn't such value or map is empty
        """
        self._raise_ex_if_den_empty()
        if value is None:
            return self._denominations.find_min()[0]
        v = self._denominations.find_gt(value)
        if v is None:
            raise ValueError("No denomination greater than " + str(value) + " present")
        return v[0]

    def max_denomination(self, value=None):
        """
        The parameter value is optional. If it is not given, it returns
        the maximum denomination (it raises an exception if no denomination exists), otherwise
        it returns the maximum denomination smaller than value (it raises an exception if no
        denomination exists larger than value)
        :param value: see return
        :return: the greater denomination smaller than the given denomination, if provided,
            else the greater denomination
        :raises ValueError: if there isn't such value or map is empty
        """
        self._raise_ex_if_den_empty()
        if value is None:
            return self._denominations.find_max()[0]
        v = self._denominations.find_lt(value)
        if v is None:
            raise ValueError("No denomination smaller than " + str(value) + " present")
        return v[0]

    def next_denomination(self, value):
        """
        Returns the denomination that follows value, if it exists,
        None otherwise. If value is not a denomination it raises an exception;
        :param value: denomination from where the search operation starts
        :return: the denomination that follows the parameter value, if it exists, None otherwise.
        :raises ValueError: if such denomination does not exists or map is empty
        """
        self._raise_ex_if_den_empty()
        try:
            _ = self._denominations[value]
            t = self._denominations.find_gt(value)
            return t[0] if t is not None else None
        except KeyError as e:
            raise ValueError(str(value) + " is not a denomination") from e

    def prev_denomination(self, value):
        """
        Returns the denomination that precedes value, if it exists,
        None otherwise. If value is not a denomination it raises an exception;
        :param value: denomination from where the search operation starts
        :return: the denomination that precedes the parameter value, if it exists, None otherwise.
        :raises ValueError: if such denomination does not exists or map is empty
        """
        self._raise_ex_if_den_empty()
        try:
            _ = self._denominations[value]
            t = self._denominations.find_lt(value)
            return t[0] if t is not None else None
        except KeyError as e:
            raise ValueError(str(value) + " is not a denomination") from e

    def has_denominations(self):
        """
        Returns true if the Denominations map is not empty
        :return: true if the Denominations map is not empty
        """
        return not self._denominations.is_empty()

    def num_denominations(self):
        """
        Returns the number of elements in the Denominations map
        :return: Returns the number of elements in the Denominations map
        """
        return len(self._denominations)

    def clear_denominations(self):
        """
        Remove all elements from the Denominations map. Note that this method creates a new denomination
        map. The old one will be deleted by the garbage collector. The final effect for the user is the same
        :return: None
        """
        self._denominations = AVLTreeMap()

    def iter_denominations(self, reverse=False):
        """
        Returns an iterator over the Denominations map. If
        reverse is false (default value), the iterator must iterate from the smaller to the larger
        denomination, otherwise it must iterate from the larger to the smaller denomination
        :param reverse: If True, the iterator iters in descending order
        :return: a denominations iterator, the order is defined by the parameter
        """
        if reverse:
            g = self._denominations.__reversed__()
        else:
            g = self._denominations.__iter__()
        for i in g:
            yield i

    def add_change(self, currency_code, change):
        """
        Add an entry in the Changes hash map, whose key
        is currencycode and whose value is change. It raises an exception if the key
        currencycode is already present
        :param currency_code: the currency code that will be used as key for the change
        :param change: the change between the current currency and the one provided as parameter
        :return: None
        :raises ValueError: if the currency code is already present, if the change is not valid or the currency code
        does not follow the ISO4217 format
        """
        if currency_code == self._code:
            raise ValueError("Cannot add a change of the same currency.")
        self._raise_ex_if_value_not_int_or_float(change)
        self._raise_ex_if_code_not_valid(currency_code)

        try:
            _ = self._changes[currency_code]
        except KeyError:
            self._changes[currency_code] = change
            return
        raise ValueError(str(currency_code) + " is already present.")

    def remove_change(self, currency_code):
        """
        Remove the entry with key currencycode from the
        Changes hash map. It raises an exception if the key currencycode is not present
        :param currency_code: the currency code whose change must be removed
        :return: None
        :raises KeyError: if the currency is not present
        :raises ValueError: if the code does not follow the ISO4217 format
        """
        self._raise_ex_if_code_not_valid(currency_code)
        try:
            del self._changes[currency_code]
        except KeyError as error:
            raise KeyError("Currency " + str(currency_code) + " not present.") from error

    def update_change(self, currency_code, change):
        """
        Updates the value associated with key
        currencycode to change. If the key currencycode does not exist, it will be inserted in
        the Changes hash map
        :param currency_code: key of the currency to update
        :param change: the new change rate for the two currencies
        :return: None
        :raises ValueError: if the change is not valid or if the code does not follow the ISO4217 format
        """
        if currency_code == self._code:
            raise ValueError("Cannot update a change of the same currency.")
        self._raise_ex_if_value_not_int_or_float(change)
        self._raise_ex_if_code_not_valid(currency_code)
        self._changes[currency_code] = change

    def copy(self):
        """
        Create a new object Currency whose attributes are equivalent to the ones of the
        current currency
        :return: the copied object whose attribute are identical to the original object
        """
        t = Currency(self._code)
        t._denominations = self._denominations
        t._changes = self._changes
        return t

    def deep_copy(self):
        """
        Create a new object Currency whose attributes are equivalent and not
        identical to the ones of the current currency.
        :return: the copied object whose attribute are equivalent but not identical to the original object
        """

        # workaround, since strings in Python are immutable and two identical strings refers to the same memory area
        temp_code = (self._code + '.')[:-1]
        c = Currency(temp_code)
        for e in self._denominations.breadthfirst():
            c._denominations[e.key()] = e.value()
        # there are only float or int in the map as values and string as keys, so this copy is sufficient and does
        # not require recursive deep copies
        for i, e in enumerate(self._changes._table):
            if isinstance(e, DoubleHashingHashMap._Item):
                c._changes._table[i] = DoubleHashingHashMap._Item((e._key + '.')[:-1], e._value)
            else:
                c._changes._table[i] = e

        c._changes._n = self._changes._n

        # a copy needs to be equivalent, this two values are random during the initialization
        c._changes._scale = self._changes._scale
        c._changes._shift = self._changes._shift

        # this value changes every time there is a collision, so it must be copied
        c._changes._collision_counter = self._changes._collision_counter
        # the other attribute are "constant" attribute, so a copy is not needed since they are the same
        return c

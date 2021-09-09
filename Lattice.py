from itertools import chain, combinations


# lattice functions for numbers
numbers_join = lambda x1, x2: max(x1, x2)
numbers_meet = lambda x1, x2: min(x1, x2)
numbers_order = lambda x1, x2: x1 <= x2    # order(x1, x2)->Boolean, returns true iff x1 <= x2
numbers_comp = lambda m, x: m - x
numbers_val = lambda x: int(x)
numbers_str = lambda x: str(x)

# lattice functions for sets
sets_join = lambda x1, x2: x1.union(x2)
sets_meet = lambda x1, x2: x1.intersection(x2)
sets_order = lambda x1, x2: x1.issubset(x2)
sets_comp = lambda m, x: m.difference(x)
sets_val = lambda y: set(list(map(lambda x: int(x), set(y[1:-1].split(",")) if len(y) > 2 else set())))
sets_str = lambda x: str(x) if x != set() else "{}"

# lattice functions for pairs
pairs_join = lambda x1, x2: (max(x1[0], x2[0]), max(x1[1], x2[1]))
pairs_meet = lambda x1, x2: (min(x1[0], x2[0]), min(x1[1], x2[1]))
pairs_order = lambda x1, x2: (x1[0] <= x2[0] and x1[1] < x2[1]) or (x1[0] < x2[0] and x1[1] <= x2[1])
pairs_comp = lambda m, x: (m[0] - x[0], m[1], x[1])
pairs_val = lambda y: (int(y[1:-1].split(",")[0]), int(y[1:-1].split(",")[1]))
pairs_str = lambda x: str(x) if x != set() else "{}"

class Lattice:

    # join(x1,x2)->x3, returns join b/w the element (for example join(2,3)=3)
    # meet(x1,x2)->x3, returns meet b/w the element (for example meet(2,3)=2)
    # val(s)->x, returns the val of a string
    # order(x1, x2)->x1<=x2
    def __init__(self, lattice_set, order, join, meet, comp, val=None, lat_str=None):
        self.lattice_set = lattice_set
        self.order = order
        self.join = join
        self.meet = meet
        self.comp = comp
        self.val = val
        self.lat_str = lat_str
        self.min_element = self.find_min()
        self.max_element = self.find_max()

    def find_min(self):
        _min = self.lattice_set[0]
        for element in self.lattice_set:
            if self.order(element, _min):
                _min = element
        return _min

    def find_max(self):
        _max = self.lattice_set[0]
        for element in self.lattice_set:
            if self.order(_max, element):
                _max = element
        return _max

    def get_min(self):
        return self.min_element

    def get_max(self):
        return self.max_element

    def complement(self, l):
        return self.comp(self.get_max(), l)

    @classmethod
    def numbers_lattice(cls, numbers):
        return Lattice(numbers, numbers_order, numbers_join, numbers_meet, numbers_comp, numbers_val, numbers_str)

    @classmethod
    def sets_lattice(cls, sets):
        return Lattice(sets, sets_order, sets_join, sets_meet, sets_comp, sets_val, sets_str)

    @classmethod
    def pairs_lattice(cls, pairs):
        return Lattice(pairs, pairs_order, pairs_join, pairs_meet, pairs_comp, pairs_val, pairs_str)

    @classmethod
    def power_set(cls, s):
        l = list(chain.from_iterable(combinations(s, r)for r in range(len(s) + 1)))
        return list(map(lambda x: set(list(x)), l))

    def find_max_lattice(self, pred):
        cur_max = self.get_min()
        for lat in self.lattice_set:
            if self.order(cur_max, lat) and pred(lat):
                cur_max = lat
        return cur_max

    def find_min_lattice(self, pred):
        cur_min = self.get_max()
        for lat in self.lattice_set:
            if self.order(lat, cur_min) and pred(lat):
                cur_min = lat
        return cur_min

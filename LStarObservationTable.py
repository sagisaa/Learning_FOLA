import LDFA
from termcolor import colored
import itertools


class LStarObservationTable:

    # oracle holds 2 functions:
    # vq is a function (word)->value
    def __init__(self, lattice, alphabet, oracle):
        self.alphabet = alphabet
        self.oracle = oracle
        self.lattice = lattice
        self.states = ['']
        self.S = ['']
        self.E = ['']
        self.T = {'': oracle.vq("")}
        self.state_val = {'': oracle.vq("")}  # The value of the eps state is the value of the eps value
        self.isLike = {'': ''}
        self.paths = {'': self.lattice.get_max()}
        self.table_init()

    def table_init(self):
        """Init the table of the words values (The T table)
           Once initialized, the table will include a column for the empty word (epsilon),
           a column for each letter in the alphabet, and rows as well.
        """
        for sigma in self.alphabet:
            self.add_col(sigma)
        for sigma in self.alphabet:
            self.add_row(sigma)

    def close(self):
        """
        close the table.
        This is the main method for the algorithm.
        For every unique state (that is in states) we make sure that
        state + sigma is in the table (as a row)
        """
        # Init the likes data structure and the unique states
        # (each time we close the table we start over)
        self.isLike = {'': ''}
        self.states = ['']
        closed = False
        while not closed:
            closed = self.add_closure()
            self.find_equivs()

    def find_equivs(self):
        """
        Update the states' statuses, in terms of equivalency.
        """
        for s in self.S:
            if s not in self.isLike:
                for state in self.states:
                    if self.equiv_rows(state, s):
                        self.isLike[s] = state
                        break
            if s not in self.isLike:
                self.isLike[s] = s
                self.states.append(s)

    def add_closure(self):
        """
        Add some row to the table in order to close it.
        This method returns true if found one, false otherwise.
        """
        closed = True
        prev_s = list(self.states)
        for s in prev_s:
            for a in self.alphabet:
                self.add_row(s + a)
                if self.is_unique(s + a):
                    self.states.append(s + a)
                    closed = False
        return closed

    def add_col(self, e):
        """
        Insert a new column to the table.
        Update the state value that each row holds according to it.
        """
        if e not in self.E:
            for s in self.S:
                self.T[s + e] = self.oracle.vq(s + e)
                self.resolve_state_val(s)
                if self.is_unique(s):
                    self.states.append(s)
            self.E.append(e)

    def add_row(self, s):
        """
        Insert a new row @s to the table.
        Update the state value that this row holds.
        """
        if s not in self.S:
            self.S.append(s)
            for e in self.E:
                self.T[s + e] = self.oracle.vq(s + e)
            self.resolve_state_val(s)

    def add_counter_example(self, word):
        """
        Add counter example to the table (rows and columns)
        """
        for i in range(len(word)):
            suffix = word[i:len(word)]
            if suffix not in self.E:
                self.add_col(suffix)

    def resolve_state_val(self, s):
        """
        Find the state value according to a possible contradiction found in the row s, with col e
        """
        self.state_val[s] = self.T[s]

    def get_all_like(self, row):
        row = self.isLike[row]
        like = []
        for s in self.S:
            if s in self.isLike and self.isLike[s] == row:
                like.append(s)
        return like

    def meet_state_vals(self, lines):
        lat = self.lattice.get_max()
        for line in lines:
            lat = self.lattice.meet(self.state_val[line], lat)
        return lat

    def get_full_state_val(self, s):
        return self.T[s]

    def equiv_rows(self, s1, s2):
        """
        Decide if s2 is equivalent to s1
        This also means that s2 has to be equivalent to all rows
        that are already equivalent to s1.
        """
        return self.equal_rows(s1, s2)

    def equal_rows(self, s1, s2):
        for e in self.E:
            if self.T[s1 + e] != self.T[s2 + e]:
                return False
        return True

    def is_unique(self, s):
        if s in self.states:
            self.isLike[s] = s
            return False
        for row in self.states:
            if self.equiv_rows(row, s):
                self.isLike[s] = row
                return False
        self.isLike[s] = s
        return True


    # The input is a unique state, and we join the values of all the states equiv to it,
    # when reading sigma.
    def find_trans_val(self, state, sigma):
        return self.lattice.get_max()

    def check_consistency(self, automaton):
        for w in self.T:
            if self.T[w] != automaton.run_word(w):
                # print("not consistent with", w)
                return w

    def create_automaton(self):
        q_0 = lambda q: self.lattice.get_max() if q == "e" else self.lattice.get_min()
        #f = lambda q: self.lattice.get_max()  # default
        f = lambda q: self.get_full_state_val(q)
        automaton = LDFA.LDFA(self.alphabet, self.lattice, q_0, f)
        for state in self.states:
            state_name = state if state != "" else "e"
            automaton.add_state(state_name, f(state))  # Adding the unique state, 'e' if it's empty
            for sigma in self.alphabet:
                next = state + sigma
                next_name = next if next != "" else "e"
                # trans_value = self.T[(next, "")] # trying something different
                trans_value = self.find_trans_val(state, sigma)
                # join bw all equiv rows e.
                if next not in self.states:
                    next = self.isLike[next]
                    next_name = next if next != "" else "e"
                automaton.add_transition(state_name, sigma, next_name, trans_value)
        return automaton

    def print_table(self, file=None):
        if file is None:
            self.print_main_table()
        else:
            self.file_print(file)

    def file_print(self, file):
        e_s = "\t\t\t\t\t\t"
        for e in self.E:
            e = "e" if e == "" else e
            e_s = e_s + '{:8}'.format(e)
        file.write(e_s + "\n")
        for s in self.S:
            s_val = '{:8}'.format(str(".").replace(" ", ""))
            s_s = '{:8}'.format(" *" if s in self.states else " [" + "." + "]")
            _s = "e" if s == "" else s
            s_s = s_val + s_s + '{:8}'.format(_s)
            file.write(s_s)
            s_s = ""
            for e in self.E:
                val = str(self.T[s + e]).replace(" ", "")
                s_s = s_s + '{:8}'.format(val)
            file.write(s_s + "\n")

    def print_main_table(self):
        print(colored("Main Table", 'magenta'))
        to_print = [2 * [""] + self.E]  # one for s, one for the class
        for s in self.S:
            values = [self.T[s + e] for e in self.E]
            to_print.append([s] + values)
        print('\n'.join([''.join(['{:6}'.format(item) for item in row])
                         for row in to_print]))
        print()
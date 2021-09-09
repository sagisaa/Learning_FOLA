from LatticeMinimization import find_minimal_partition
import LDFA
from termcolor import colored


class FOLStarObservationTable:

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
        self.TL = {l: {s + e: 1 if self.lattice.order(l, self.T[s + e]) else 0
                       for s in self.S for e in self.E} for l in self.lattice.lattice_set}
        self.add_col("a")
        self.add_col("b")

    def add_col(self, e):
        if e not in self.E:
            self.E.append(e)
            for s in self.S:
                self.T[s + e] = self.oracle.vq(s + e)
                for l in self.lattice.lattice_set:
                    self.TL[l][s + e] = 1 if self.lattice.order(l, self.T[s + e]) else 0
            return True
        return False

    def add_row(self, s):
        if s not in self.S:
            self.S.append(s)
            for e in self.E:
                self.T[s + e] = self.oracle.vq(s + e)
                for l in self.lattice.lattice_set:
                    self.TL[l][s + e] = 1 if self.lattice.order(l, self.T[s + e]) else 0
            return True
        return False

    def add_counter_example(self, counter_example):
        added = False
        for i in range(len(counter_example)):
            if self.add_col(counter_example[i:]):
                added = True
        return added

    def equivalent_rows(self, s1, s2, l):
        # return self.equal_rows(s1, s2, l) and all(self.equal_rows(s1 + sigma, s2 + sigma, l) for sigma in self.alphabet)
        return all([self.TL[l][s1 + e] == self.TL[l][s2 + e] for e in self.E])

    def equal_rows(self, s1, s2, l):
        T_s1 = {e: self.oracle.vq(s1 + e) if s1 + e not in self.TL[l] else self.TL[l][s1 + e] for e in self.E}
        T_s2 = {e: self.oracle.vq(s2 + e) if s2 + e not in self.TL[l] else self.TL[l][s2 + e] for e in self.E}
        TL_s1 = {e: 1 if self.lattice.order(l, T_s1[e]) else 0 for e in self.E}
        TL_s2 = {e: 1 if self.lattice.order(l, T_s2[e]) else 0 for e in self.E}
        return all([TL_s1[e] == TL_s2[e] for e in self.E])

    def equivalence_classes_in_l(self, l):
        # the problem is here
        classes = {}
        states = set()
        for s in self.S:
            found = False
            if self.zero_line(s, l):
                continue
            for state in states:
                if self.equivalent_rows(s, state, l):
                    classes[state].add(s)
                    found = True
                    break
            if not found:
                states.add(s)
                classes[s] = {s}
        partition = list(classes.values())
        return partition
    
    def next_consistent(self, s1, s2, partitions):
        for sigma in self.alphabet:
            s1_s = s1 + sigma
            s2_s = s2 + sigma
            for partition in partitions:
                part_s1 = list(filter(lambda p: s1_s in p, partition))
                part_s2 = list(filter(lambda p: s2_s in p, partition))
                if part_s1 != [] and part_s2 != [] and part_s1 != part_s2:
                    return False
        return True

    def consistency_partition(self, partitions):
        partition = []
        for s1 in self.S:
            added = False
            if not all(s1 + sigma in self.S for sigma in self.alphabet):
                continue
            for part in partition:
                if self.next_consistent(part[0], s1, partitions):
                    part.append(s1)
                    added = True
                    break
            if not added:
                partition.append([s1])
        return [set(p) for p in partition]

    def equivalence_partition(self):
        partitions = [self.equivalence_classes_in_l(l) for l in self.lattice.lattice_set]
        partitions = [part for part in partitions if part]
        # cons_partition = self.consistency_partition(partitions)
        # print("-------------------")
        # print("all", partitions)
        # partitions.append(cons_partition)
        minimal_partition = find_minimal_partition(set(self.S), partitions)
        # minimal_partition = find_minimal_partition_with_bonus(set(self.S), partitions, cons_partition)
        # print("cons", cons_partition)
        # print("res:", minimal_partition)
        # print("-------------------")

        return minimal_partition

    def row_closed(self, s):
        return all([s + sigma in self.S for sigma in self.alphabet])

    def representative_states(self):
        minimal_partition = self.equivalence_partition()
        row_to_state = {}
        for part in minimal_partition:
            # part = sorted(part)
            if '' in part:
                rep = ''
            else:
                rep = next(iter(part))  # [s for s in states if s in part][0]
                max_potential = self.row_potential(rep)
                for s in part:
                    s_potential = self.row_potential(s)
                    if s_potential > max_potential or (s_potential == max_potential and self.row_closed(s))\
                            or (s_potential == max_potential and rep.startswith(s)):
                        rep, max_potential = s, s_potential
            row_to_state.update({s: rep for s in part})
        return row_to_state

    def close(self):
        closed = False
        while not closed:
            closed = True
            rows_to_states = self.representative_states()
            states = set(rows_to_states.values())
            if any([self.add_row(state + sigma) for state in states for sigma in self.alphabet]):
                closed = False

    def state_name(self, s):
        return s if s != '' else 'e'

    def max_e(self, s):
        cur_max = '', self.T[s]
        for e in self.E:
            if cur_max[1] < self.T[s + e]:
                cur_max = e, self.T[s + e]
        return cur_max[0]

    def row_potential(self, s):
        max_e = self.max_e(s)
        return self.T[s + max_e]

    def zero_line(self, s, l):
        return not any([self.TL[l][s + e] for e in self.E])

    def trans_value(self, state, sigma):
        return self.row_potential(state + sigma)

    def find_next_state(self, state, sigma, reps):
        max_potential, cur_next = self.row_potential(state + sigma), reps[state + sigma]
        for s in reps:
            if reps[s] == state:
                if s + sigma in self.S and self.row_potential(s + sigma) > max_potential:
                    max_potential, cur_next = self.row_potential(s + sigma), reps[s + sigma]
        return max_potential, cur_next


    def create_automaton(self):
        row_to_state = self.representative_states()
        states = set(row_to_state.values())

        q_0 = lambda q: self.lattice.get_max() if self.state_name(q) == 'e' else self.lattice.get_min()
        f = lambda q: self.lattice.find_max_lattice(lambda l: self.TL[l][q] == 1)

        automaton = LDFA.LDFA(self.alphabet, self.lattice, q_0, f)

        for state in states:
            automaton.add_state(self.state_name(state), f(state))
            for sigma in self.alphabet:
                trans_val, next_state = self.find_next_state(state, sigma, row_to_state)
                automaton.add_transition(self.state_name(state), sigma, self.state_name(next_state), trans_val)
        return automaton

    def resolve_conflict(self):
        for s1 in self.S:
            for s2 in self.S:
                if s1 != s2:
                    if s2.startswith(s1) and self.row_potential(s1) < self.row_potential(s2):
                        conflicting_w = s2 + self.max_e(s2)
                        if self.add_col(conflicting_w[len(s1):]):
                            return True
        return False

    def check_consistency(self, automaton):
        for w in self.T:
            if self.T[w] != automaton.run_word(w):
                # print("not consistent with", w)
                return w

    def print_table(self, file=None):
        if file is None:
            print(str(self.equivalence_partition()) + "\n")
            self.print_main_table()
            ps = [self.equivalence_classes_in_l(l) for l in self.lattice.lattice_set]
            p = self.equivalence_partition()
            c = self.consistency_partition(p)
            print("All: \n" + str("\n".join([str(a) for a in ps])) + "\n")
            print("Consistency: " + str(c) + "\n")
            print("Result: " + str(p) + "\n")
        else:
            ps = [self.equivalence_classes_in_l(l) for l in self.lattice.lattice_set]
            p = self.equivalence_partition()
            c = self.consistency_partition(p)
            file.write("All: \n" + str("\n".join([str(a) for a in ps])) + "\n")
            file.write("Consistency: " + str(c) + "\n")
            file.write("Result: " + str(p) + "\n")
            self.file_print(file)


    def file_print(self, file):
        reps = self.representative_states()

        e_s = "\t\t\t\t\t\t"
        for e in self.E:
            e = "e" if e == "" else e
            e_s = e_s + '{:8}'.format(e)
        file.write(e_s + "\n")
        for s in self.S:
            s_val = '{:8}'.format(str(".").replace(" ", ""))
            s_s = '{:8}'.format(" *" if s in reps.values() else " [" + str(reps[s]) + "]")
            _s = "e" if s == "" else s
            s_s = s_val + s_s + '{:8}'.format(_s)
            file.write(s_s)
            s_s = ""
            for e in self.E:
                val = str(self.T[s + e]).replace(" ", "")
                s_s = s_s + '{:8}'.format(val)
            file.write(s_s + "\n")

    def print_table_for_l(self, l, file=None):
        if not file:
            print(colored("l = " + str(l), 'magenta'))
        else:
            file.write("l = " + str(l))
        T_l = self.TL[l]
        to_print = [2 * [""] + self.E]  # one for s, one for the class
        for s in self.S:
            if not self.zero_line(s, l):
                values = [T_l[s + e] for e in self.E]
                to_print.append([s] + values)

        if file:
            file.write('\n'.join([''.join(['{:6}'.format(item) for item in row])
                         for row in to_print]))
            # print(self.partition_by_l(l, classes))
            file.write("\n")
        else:
            print('\n'.join([''.join(['{:6}'.format(item) for item in row])
                             for row in to_print]))
            # print(self.partition_by_l(l, classes))
            print()

    def print_main_table(self):
        print(colored("Main Table", 'magenta'))
        reps = self.representative_states()

        e_s = "\t\t\t\t\t\t"
        for e in self.E:
            e = "e" if e == "" else e
            e_s = e_s + '{:8}'.format(e)
        print(e_s)
        for s in self.S:
            s_val = '{:8}'.format(str(".").replace(" ", ""))
            s_s = '{:8}'.format(" *" if s in reps.values() else " [" + str(reps[s]) + "]")
            _s = "e" if s == "" else s
            s_s = s_val + s_s + '{:8}'.format(_s)
            print(s_s, end="")
            s_s = ""
            for e in self.E:
                val = str(self.T[s + e]).replace(" ", "")
                s_s = s_s + '{:8}'.format(val)
            print(s_s)

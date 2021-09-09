import random
import State
import itertools


class LDFA:

    def __init__(self, alphabet, lattice, q_0=None, f=None):
        self.alphabet = alphabet
        self.lattice = lattice
        if q_0 is not None:
            self.q_0 = q_0
        if f is not None:
            self.f = f
        self.states = {}  # {"g": State.State("g", lattice.get_min())}
        self.n = 0

    def add_state(self, title, val):
        state = State.State(title, val)
        self.states[title] = state
        self.n += 1

    def set_transition_value(self, source, sigma, l):
        state = self.states[source]
        state.set_transition_value(sigma, l)

    def set_state_value(self, state, value):
        state = self.states[state]
        state.set_state_value(value)

    def add_transition(self, source, letter, dest, value):
        if not self.verify_input(value=value, letter=letter):
            return
        else:
            self.states[source].add_only_transition(letter, value, dest)

    def run_word(self, word, for_state=False):
        """
        run a word on the LDFA, this returns the value of the word,
        or, if specified, the state in which the run ended.
        :param word: the word to run on the LDFA
        :param for_state: if True, the run will return the state on which it ended.
        else, it will return the value of that word.
        :return: the value of the word or the state on which it ended.
        """
        cur_state = self.initial_state()
        val = self.q_0(cur_state)
        for letter in word:
            if not self.verify_input(value=None, letter=letter):
                return
            next_state = self.states[cur_state].next_states(letter)
            if len(next_state) > 1:
                return -1  # This should be deterministic
            if len(next_state) < 1:
                return self.lattice.get_min()
            next_state = next_state[0]
            trans_val, n_title = next_state
            val = self.lattice.meet(val, trans_val)
            cur_state = n_title
        return self.lattice.meet(val, self.states[cur_state].value) if not for_state else cur_state

    def initial_state(self):
        """
        find the initial state of the LDFA
        :return: the initial state if found one (there must be exactly one)
        if no initial state was found, return "-1".
        """
        for state in self.states.keys():
            if self.q_0(state) > self.lattice.get_min():
                return state
        return "-1"

    def verify_input(self, value=None, letter=None):
        """
        :param value: verify that the value is an element in the lattice.
        :param letter: verify that the letter is a part of the alphabet.
        :return: True if both are verified, False otherwise.
        """
        good = True
        if value is not None:
            good = value in self.lattice.lattice_set
        if letter is not None:
            good &= letter in self.alphabet
        if not good:
            print("Input is invalid")
        return good

    def print_automaton(self, file=None):
        """
        print the automaton in the following pattern:
        e=>
        e$3: 2|1->q 1|2->e 3|3->q
        q$2: 1|2->e 2|2->e 3|2->e
        :param file: if not None, the print will be performed to the file.
        :return: None
        """
        if file is None:
            print('{}=>'.format(self.initial_state()))
            for state in self.states.values():
                state.print_det_state()
        else:
            file.write('{}=>\n'.format(self.initial_state()))
            for state in self.states.values():
                state.print_det_state(file)

    def get_state(self, q):
        return self.states[q]

    @classmethod
    def create_by_input(cls, alphabet, lattice, file_name):
        file = open(file_name)
        start = file.readline()[:-1]
        q_0 = lambda q: lattice.get_max() if q == start else lattice.get_min()
        automaton = LDFA(alphabet, lattice, q_0)
        for s_state in file:
            s_state = s_state[:-1]
            state_itself, s_transitions = s_state.split(": ")
            state_name, state_val = state_itself.split("$")
            automaton.add_state(state_name, lattice.val(state_val))
            transitions = s_transitions.split(" ")
            for trans in transitions:
                [letter, val] = trans.split("|")
                trans_val, dest = val.split("->")
                value = lattice.val(trans_val)
                automaton.add_transition(state_name, letter, dest, value)
        f = lambda q: automaton.states[q].val
        automaton.f = f
        return automaton

    @classmethod
    def create_by_input_new(cls, alphabet, lattice, file_name):
        with open(file_name, 'r') as file:
            start = file.readline()[0]
            q_0 = lambda q: lattice.get_max() if q == start else lattice.get_min()
            automaton = LDFA(alphabet, lattice, q_0)
            for s_state in file:
                if not s_state:
                    break
                s_state = s_state[:-1]
                state_itself, s_transitions = s_state.split(": ")
                state_name, state_val = state_itself.split("$")
                automaton.add_state(state_name, lattice.val(state_val))
                transitions = s_transitions.split()
                for trans in transitions:
                    [letter, val] = trans.split("|")
                    trans_val, dest = val.split("->")
                    value = lattice.val(trans_val)
                    automaton.add_transition(state_name, letter, dest, value)
            f = lambda q: automaton.states[q].val
            automaton.f = f
            return automaton

    def trim(self):
        cur = self.initial_state()
        reached = [cur]
        to_reach = [cur]
        while to_reach:
            cur = to_reach.pop(0)
            for sigma in self.alphabet:
                nexts = self.states[cur].next_states(sigma)
                if nexts:
                    _, next_state = nexts[0]
                    if next_state not in reached:
                        reached.append(next_state)
                        to_reach.append(next_state)

        automaton = LDFA(self.alphabet, self.lattice, self.q_0, self.f)
        for state in self.states:
            if state in reached:
                automaton.states[state] = self.states[state]

        return automaton

    def simplify(self):
        lattice = self.lattice
        alphabet = self.alphabet
        initial = self.initial_state()
        states = ["{}*{}".format(q, self.lattice.lat_str(l)) for q in self.states.keys() for l in
                  self.lattice.lattice_set]
        values = {s: self.get_state(s).value for s in self.states.keys()}
        q_0 = lambda q: lattice.get_max() \
            if q == (initial + "*" + str(lattice.get_max())) \
            else lattice.get_min()
        f = lambda q: lattice.meet(lattice.val(q.split("*")[1]), values[q.split("*")[0]])
        automaton = LDFA(alphabet, lattice, q_0, f)
        for state in states:
            automaton.add_state(state, f(state))
        for state in self.states.values():
            for sigma in state.transitions.keys():
                for (value, dest) in state.transitions[sigma]:
                    for l in lattice.lattice_set:
                        automaton.add_transition("{}*{}".format(state.title, lattice.lat_str(l)),
                                                 sigma,
                                                 "{}*{}".format(dest, lattice.lat_str(lattice.meet(l, value))),
                                                 lattice.get_max())
        return automaton

    @classmethod
    def equivalent(cls, a1, a2):
        """
        This will return a distinguishing word if a1 and a2 aren't equivalent,
        Else, it will return None
        :param a1: LDFA a1
        :param a2: LDFA a2
        :return: a distinguishing word if not equivalent, or None if a1 and a2 are.
        """
        # we can start from e, then its neighbors, and see if there is a difference
        alphabet = a1.alphabet
        a1 = a1.simplify().trim()
        a2 = a2.simplify().trim()

        managed_pairs = []
        eq_ch_pairs = [(a1.initial_state(), a2.initial_state(), "")]
        while len(eq_ch_pairs) > 0:
            q_1, r_1, w = eq_ch_pairs.pop()
            for sigma in alphabet:
                q_2 = a1.get_state(q_1).next_states(sigma)[0][1]  # getting the state title only
                r_2 = a2.get_state(r_1).next_states(sigma)[0][1]
                if (q_2, r_2) not in managed_pairs:
                    if a1.get_state(q_2).value != a2.get_state(r_2).value:
                        return w + sigma
                        # return False
                    elif (q_2, r_2, w + sigma) not in eq_ch_pairs:
                        eq_ch_pairs.append((q_2, r_2, w + sigma))
            managed_pairs.append((q_1, r_1))
        # return True
        return None

    def find_CS(self):
        paths = self.max_paths()
        q0 = self.initial_state()
        S = [t[1] for t in paths[q0].values()]
        S_sigma = [s + sigma for s in S for sigma in self.alphabet]
        E = {''}
        M = set([t[1] for q in paths.values() for t in q.values()])

        for q1, q2 in itertools.product(S, S):
            if q1 != q2:
                for _ in range(10):
                    if not self.distinguished_states(q1, q2, E):
                        E.add(self.word_generator(self.alphabet, 4))
                    else:
                        break

        E_M = E.union(M)

        # print("S", S)
        # print("S_", S_sigma)
        # print("E", E)
        words = [s + e for s in S + S_sigma for e in E_M]
        sample = {w: self.run_word(w) for w in words}
        return sample


    def distinguished_states(self, q1, q2, E):
        row_q1 = [self.run_word(q1 + e) for e in E]
        row_q2 = [self.run_word(q2 + e) for e in E]
        for l in self.lattice.lattice_set:
            row_q1_l = [1 if self.lattice.order(l, v) else 0 for v in row_q1]
            row_q2_l = [1 if self.lattice.order(l, v) else 0 for v in row_q2]
            if row_q1_l != row_q2_l and row_q1_l != [0] * len(E) and row_q2_l != [0] * len(E):
                return True
        return False



    def max_paths(self):
        """
        Find the maximum value of a path from all states to all states.
        :return: A dictionary d for which for all q1,q2 in states,
        d[q1][q2] = l, w whereas l is the value of the maximal path from q1 to q2,
        and w is the word that leads to it.
        """
        d = {q1:
                 {q2: (self.lattice.get_min() if q1 != q2 else self.lattice.get_max(), '')
                  for q2 in self.states.keys()}
             for q1 in self.states.keys()}
        for q in self.states.keys():
            self.find_paths_from_state(d, q)
        return d

    def find_paths_from_state(self, d, q):
        to_relax = [(q, '')]
        relaxed = []
        while to_relax:
            cur_state, cur_word = to_relax.pop(0)
            transitions = self.maximal_transitions_from_state(cur_state)
            for next_state in transitions:
                trans_value, sigma = transitions[next_state]
                if d[q][next_state][0] < self.lattice.meet(d[q][cur_state][0], trans_value):
                    d[q][next_state] = self.lattice.meet(d[q][cur_state][0], trans_value), cur_word + sigma
                if next_state not in relaxed:
                    to_relax.append((next_state, cur_word + sigma))
            relaxed.append(cur_state)

    def maximal_transitions_from_state(self, q):
        transitions = {}
        for sigma in self.alphabet:
            nexts = self.states[q].next_states(sigma)
            if nexts:
                trans_value, next_state = nexts[0]
                transitions[next_state] = (trans_value, sigma) if (next_state not in transitions or self.lattice.order(transitions[next_state][0], trans_value)) else (transitions[next_state])
        return transitions

    @classmethod
    def word_generator(cls, letters, word_len=12):
        return ''.join(random.choice(letters) for _ in range(word_len))

    # a1 is the vqship function of the original automaton
    @classmethod
    def random_equivalent(cls, alphabet, a1, a2):
        N = 4000
        for i in range(N):
            word = cls.word_generator(alphabet, random.randint(1, 10))
            v1 = a1(word)
            v2 = a2.run_word(word)
            if v1 != v2:
                return word
        return None

    # not random :)
    @classmethod
    def equivalent_by_words(cls, alphabet, a1, a2, N=12):
        for i in range(N):
            all_options = [''.join(l) for l in list(itertools.product(alphabet, repeat=i))]
            for word in all_options:
                v1 = a1(word)
                v2 = a2.run_word(word)
                if v1 != v2:
                    # print('Not equivalent on the word: {} (org={}, new={})'.format(word, v1, v2))
                    return word
        # print('It seems correct!')
        return None

    def num_of_states(self):
        return len(self.states)

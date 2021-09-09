import random
import State
import itertools
import functools


class NDFA:

    def __init__(self, alphabet, lattice, q_0):
        self.alphabet = alphabet
        self.lattice = lattice
        self.q_0 = q_0
        self.states = {}

    def add_state(self, title, value):
        state = State.State(title, value)
        self.states[title] = state

    def set_state_value(self, state, value):
        state = self.states[state]
        state.set_state_value(value)

    def add_transition(self, source, letter, dest, value):
        if not self.verify_input(value=value, letter=letter):
            return
        else:
            self.states[source].add_transition(letter, value, dest)

    def run_word(self, word):
        """
        run a word on the NDFA, this returns the value of the word.
        :param word: the word to run on the NDFA
        :return: the value of the word.
        """
        initials = self.initial_states()
        max_run = self.lattice.get_min()
        for initial in initials:
            run_value = self.run_word_from_state(word, initial)
            max_run = self.lattice.join(max_run, run_value)
        return max_run

    def run_word_from_state(self, word, initial):
        if word == '':
            return self.states[initial].value
        else:
            nexts = self.states[initial].next_states(word[0])  # [(value, state_title)...]
            max_value = self.lattice.get_min()
            if len(nexts) == 0:
                return self.lattice.get_min()
            for value, next_state in nexts:
                run_val = self.lattice.meet(value, self.run_word_from_state(word[1:], next_state))
                max_value = self.lattice.join(max_value, run_val)
            return max_value

    def initial_states(self):
        """
        find the initial states of the NDFA
        :return: the initial states if found one (there must be at least one)
        if no initial state was found, return [].
        """
        initials = []
        for state in self.states.keys():
            if self.q_0(state) > self.lattice.get_min():
                initials.append(state)
        return initials

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
            print('{}=>'.format(self.initial_states()))
            for state in self.states.values():
                state.print_det_state()
        else:
            file.write('{}=>\n'.format(self.initial_states()))
            for state in self.states.values():
                state.print_det_state(file)

    def existing_transition_value(self, transitions, source, letter, next_state):
        max_value = -1
        for src, sigma, dst, trans_value in transitions:
            if src == source and dst == next_state and sigma == letter:
                max_value = self.lattice.join(max_value, trans_value)
        return max_value

    # q2 wants to merge with q1 (q2 > q1 in lexicographic order)
    def merge_states(self, q1: str, q2: str):
        q_0 = lambda q: self.q_0(q) if q not in [q1, q2] else self.lattice.join(self.q_0(q1), self.q_0(q2))
        automaton = NDFA(self.alphabet, self.lattice, q_0)

        new_transitions = []

        for state in self.states.keys():
            if state != q2:
                prev_state: State.State = self.states[state]
                if state != q1:
                    automaton.add_state(state, prev_state.value)
                    for sigma in prev_state.transitions.keys():
                        for trans_value, next_state in prev_state.transitions[sigma]:
                            next_state = q1 if next_state == q2 else next_state
                            cur_trans_value = self.existing_transition_value(new_transitions, state, sigma, next_state)
                            if cur_trans_value != -1:
                                if cur_trans_value < trans_value:
                                    new_transitions.remove((state, sigma, next_state, cur_trans_value))
                                    new_transitions.append((state, sigma, next_state, trans_value))
                            else:
                                new_transitions.append((state, sigma, next_state, trans_value))
                            # automaton.add_transition(state, sigma, next_state, trans_value)

        prev_q1 = self.states[q1]
        prev_q2 = self.states[q2]

        automaton.add_state(q1, self.lattice.join(prev_q1.value, prev_q2.value))

        for sigma in self.alphabet:
            q1_transes = prev_q1.transitions[sigma] if sigma in prev_q1.transitions else []
            q2_transes = prev_q2.transitions[sigma] if sigma in prev_q2.transitions else []

            for trans_value, next_state in q1_transes + q2_transes:
                next_state = q1 if next_state == q2 else next_state
                cur_trans_value = self.existing_transition_value(new_transitions, q1, sigma, next_state)
                if cur_trans_value != -1:
                    if cur_trans_value < trans_value:
                        new_transitions.remove((q1, sigma, next_state, cur_trans_value))
                        new_transitions.append((q1, sigma, next_state, trans_value))
                else:
                    new_transitions.append((q1, sigma, next_state, trans_value))

        for c in new_transitions:
            automaton.add_transition(*c)
            # print(new_transitions)
        return automaton

    def get_state(self, q):
        return self.states[q]

    @classmethod
    def create_by_input(cls, alphabet, lattice, file_name):
        file = open(file_name)
        start = file.readline()[:-1]
        q_0 = lambda q: lattice.get_max() if q == start else lattice.get_min()
        automaton = NDFA(alphabet, lattice, q_0)
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

    def num_of_states(self):
        return len(self.states)

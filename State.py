from termcolor import colored


class State:

    # transitions:
    # {sigma1: [(v1, next_s1), (v2, next_s2)], sigma1: [(v1, next_s1), (v2, next_s2)]}
    def __init__(self, title, value):
        self.title = title
        self.transitions = {}
        self.value = value

    def add_transition(self, letter, value, dst):
        if letter not in self.transitions.keys():
            self.transitions[letter] = []
        self.transitions[letter].append((value, dst))

    def add_only_transition(self, letter, value, dst):
        self.transitions[letter] = [(value, dst)]

    def set_transition_value(self, letter, value):
        _, prev_dst = self.transitions[letter][0]
        self.transitions[letter] = [(value, prev_dst)]

    def set_state_value(self, value):
        self.value = value

    # if this is a deterministic automaton, this will return only one state.
    def next_states(self, letter):
        possible = []
        # for each transition possible with this letter
        if letter not in self.transitions:
            return []
        for (value, state_title) in self.transitions[letter]:
            # if value != lattice.get_min():
            possible.append((value, state_title))
        return possible

    def print_det_state(self, file=None):
        # print(self.title, self.value, self.transitions)
        if file is None:
            s = '{:14}'.format('{}${}: '.format(self.title, self.value).replace(" ", ""))
            print(colored(s, 'magenta'), end="")
            s = ""
            for trans in self.transitions.items():
                s += '{:14}'.format('{0[0]}|{1[0]}->{1[1]} '.format(trans, trans[1][0]).replace(" ", ""))
            print(s)
        else:
            s = '{:14}'.format('{}${}: '.format(self.title, self.value).replace(" ", ""))
            file.write(s)
            s = ""
            for trans in self.transitions.items():
                s += '{:14}'.format('{0[0]}|{1[0]}->{1[1]} '.format(trans, trans[1][0]).replace(" ", ""))
            file.write(s + "\n")

    def __str__(self):
        return self.title

import functools
from LNFA import NDFA


class RPNI:

    # sample is a map from words (strings) to their values
    def __init__(self, alphabet, lattice, sample):
        self.alphabet = alphabet
        self.lattice = lattice
        self.sample = sample

    def run_algorithm(self):
        comp_words = lambda x1, x2: -1 if len(x1) < len(x2) or (len(x1) == len(x2) and x1 < x2) else 1

        prefs = self.find_prefs()
        prefs.sort(key=functools.cmp_to_key(comp_words))
        # print(prefs)
        states = prefs[:]
        automaton: NDFA = self.create_initial_tree(prefs)
        # automaton.print_automaton()
        # print("----------------------------------------")
        for q2 in prefs:
            prior_prefs = [p for p in states if comp_words(p, q2) < 0]
            prior_prefs.sort(key=functools.cmp_to_key(comp_words))
            for q1 in prior_prefs:
                merged_automaton = automaton.merge_states(q1, q2)
                if self.consistent_with_sample(merged_automaton):
                    automaton = merged_automaton
                    states.remove(q2)
                    print("merged {} with {}".format(q1, q2))
                    # automaton.print_automaton()
                    # print("----------------------------------------")
                    break
        return automaton

    def find_prefs(self):
        find_word_prefixes = lambda w: [w[:i] for i in range(len(w) + 1)]
        prefs = []
        for word in self.sample.keys():
            cur_prefs = find_word_prefixes(word)
            for pref in cur_prefs:
                if pref not in prefs:
                    prefs.append(pref)
        return prefs

    def create_initial_tree(self, prefs):
        q_0 = lambda q: self.lattice.get_max() if q == "" else self.lattice.get_min()
        tree = NDFA(self.alphabet, self.lattice, q_0)
        for pref in prefs:
            value = -1
            if pref in self.sample:
                value = self.sample[pref]
            tree.add_state(pref, value)
            for sigma in self.alphabet:
                if pref + sigma in prefs:
                    next_state = pref + sigma
                    trans_value = max([self.sample[p] for p in self.sample.keys() if p.startswith(pref + sigma)])
                    tree.add_transition(pref, sigma, next_state, trans_value)
        return tree

    def consistent_with_sample(self, automaton: NDFA):
        for w in self.sample.keys():
            expected_value = self.sample[w]
            observed_value = automaton.run_word(w)
            if expected_value != observed_value:
                # print("On {}: expected:{} got:{}".format(w, expected_value, observed_value))
                return False
        return True

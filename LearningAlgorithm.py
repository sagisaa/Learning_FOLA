import FOLStarObservationTable
import LStarObservationTable
from LDFA import LDFA


class LearningAlgorithm:

    FOLSTAR_TABLE = 1
    LSTAR_TABLE = 2

    successes = 0
    nums_of_states = []
    changes = []
    cur_success = False

    def __init__(self, lattice, oracle, alphabet, original=None, table=1):
        self.lattice = lattice
        self.oracle = oracle
        self.alphabet = alphabet

        if table == LearningAlgorithm.LSTAR_TABLE:
            self.table = LStarObservationTable.LStarObservationTable(lattice, alphabet, oracle)
        else:
            self.table = FOLStarObservationTable.FOLStarObservationTable(lattice, alphabet, oracle)

        self.original = original
        self.MAX_ITERATIONS = 15
        self.EQs = 0
        LearningAlgorithm.nums_of_states = []
        LearningAlgorithm.changes = []
        LearningAlgorithm.cur_success = False

    def run_algorithm(self, file=None):
        ok = False
        automaton = None

        LearningAlgorithm.nums_of_states = []
        LearningAlgorithm.changes = []
        LearningAlgorithm.cur_success = False

        for i in range(self.MAX_ITERATIONS):
            if ok:
                break
            self.table.close()
            automaton = self.table.create_automaton()

            # self.table.print_table(file)
            LearningAlgorithm.nums_of_states += [len(automaton.states)]
            # automaton.print_automaton(file)
            counter_example = self.recommend_counter(automaton)
            self.EQs += 1

            if counter_example is None:  # the conjecture is correct!
                ok = True
                LearningAlgorithm.successes += 1
                LearningAlgorithm.cur_success = True
            else:
                # self.debug_print("Counter Example: " + counter_example, file)
                self.table.add_counter_example(counter_example)
        return automaton  # self.table.create_automaton()

    def table_size(self):
        return len(self.table.T)

    def compare_automata(self, prev: LDFA, cur: LDFA):
        if prev is None:
            return "Na"
        if len(prev.states) < len(cur.states):
            return "NS"  # New state
        elif list(prev.states.keys())[:] != list(cur.states.keys())[:]:
            return "RC"  # Representative changed
        elif any([prev.states[state].transitions[sigma][0][1] != cur.states[state].transitions[sigma][0][1]
                  for state in prev.states.keys() for sigma in self.alphabet]):
            return "EC"  # Equivalence Change
        else:
            return "TVC"  # Transition Value Changed

    def debug_print(self, s, file):
        if file is None:
            print(s)
        else:
            file.write(s + "\n")

    # return a counterexample if there is one, else return None
    def recommend_counter(self, automaton):
        if self.original is not None:
            return LDFA.equivalent(self.original, automaton)
        else:
            return LDFA.equivalent_by_words(self.alphabet, self.oracle.vq, automaton)

import LDFA
import LearningAlgorithm
import Oracle
import random
import Lattice
import time


def run_test_from_file(file_name, lattice, alphabet, table=1):
    expected_automaton = LDFA.LDFA.create_by_input(alphabet, lattice, file_name)
    vq = lambda word: expected_automaton.run_word(word)

    expected_automaton.print_automaton()

    equiv = lambda automata: True
    oracle = Oracle.Oracle(vq, equiv)

    learning = LearningAlgorithm.LearningAlgorithm(lattice, oracle, alphabet, expected_automaton, table=table)
    automaton = learning.run_algorithm()
    automaton.print_automaton()

    LDFA.LDFA.equivalent_by_words(alphabet, vq, automaton)


def run_test_from_lambda(fun, lattice, alphabet):
    vq = fun
    equiv = lambda automata: True
    oracle = Oracle.Oracle(vq, equiv)

    learning = LearningAlgorithm.LearningAlgorithm(lattice, oracle, alphabet)
    automaton = learning.run_algorithm()
    automaton.print_automaton()

    LDFA.LDFA.equivalent_by_words(alphabet, vq, automaton)


def generate_random_LDFA(alphabet, lattice, number_of_states=10, state_values=True):

    # number_of_states = random.randrange(10, 11)

    states = [str(i) for i in range(number_of_states)]
    q_0 = lambda q: lattice.get_max() if q == '0' else lattice.get_min()
    f_values = {s: random.choice(lattice.lattice_set) for s in states} if state_values \
        else {s: lattice.get_max() for s in states}
    f = lambda q: f_values[q]

    automaton = LDFA.LDFA(alphabet, lattice, q_0, f)

    for state in states:
        automaton.add_state(state, f(state))

    for state in states:
        for sigma in alphabet:
            dest = random.choice(states)
            trans_value = random.choice(lattice.lattice_set)
            automaton.add_transition(state, sigma, dest, trans_value)

    return automaton


def im_feeling_lucky(lattice, alphabet, count=1, save_to_file=True, state_values=True):
    max_EQ = (0, 0)
    for i in range(count):

        output_file = open("results/output{}.txt".format(i), "w+") if save_to_file else None  # None

        automaton = generate_random_LDFA(alphabet, lattice, 10, state_values=state_values)

        if output_file is None:
            print("Automaton Selected:")
        else:
            output_file.write("Automaton Selected:\n")
        automaton.print_automaton(output_file)  # or None

        vq = lambda word: automaton.run_word(word)
        equiv = lambda automata: True
        oracle = Oracle.Oracle(vq, equiv)

        learning = LearningAlgorithm.LearningAlgorithm(lattice, oracle, alphabet, original=automaton, table=1)

        result = learning.run_algorithm(output_file)

        # print(LDFA.LDFA.equivalent(automaton, result))

        print("[Test {:>5}]  States Original: {:>2} States Result: {:>2}, States Progress: {:>14} - {:>14} Success = {}"
              .format(i, automaton.num_of_states(), result.num_of_states(), str(learning.nums_of_states), str(learning.changes),
                      learning.cur_success))
        if len(learning.nums_of_states) > max_EQ[0]:
            max_EQ = len(learning.nums_of_states), i

        output_file.close()
    print("Score:{}/{}".format(LearningAlgorithm.LearningAlgorithm.successes, count))
    print("Maximum EQ: {}, In test number {}".format(max_EQ[0], max_EQ[1]))

def lstar_vs_min(lattice, alphabet, count=1, save_to_file=True):

    EQ_min = 0
    MQ_min = 0

    EQ_lstar = 0
    MQ_lstar = 0

    for i in range(count):

        output_file_lstar = open("results/output{}_lstar.txt".format(i), "w+") if save_to_file else None  # None
        output_file_min = open("results/output{}_min.txt".format(i), "w+") if save_to_file else None  # None

        states_num = int(i/55+5)#random.randint(5, 40)
        automaton = generate_random_LDFA(alphabet, lattice, states_num)

        output_file_lstar.write("Automaton Selected:\n")
        output_file_min.write("Automaton Selected:\n")

        automaton.print_automaton(output_file_lstar)  # or None
        automaton.print_automaton(output_file_min)  # or None

        vq = lambda word: automaton.run_word(word)
        equiv = lambda automata: True
        oracle = Oracle.Oracle(vq, equiv)

        learning_lstar = LearningAlgorithm.LearningAlgorithm(lattice, oracle, alphabet,
                                                             table=LearningAlgorithm.LearningAlgorithm.LSTAR_TABLE, original=automaton)
        result_lstar = learning_lstar.run_algorithm(output_file_lstar)

        learning_min = LearningAlgorithm.LearningAlgorithm(lattice, oracle, alphabet,
                                                           table=LearningAlgorithm.LearningAlgorithm.FOLSTAR_TABLE, original=automaton)
        result_min = learning_min.run_algorithm(output_file_min)

        # print(LDFA.LDFA.equivalent(result_lstar, automaton))
        # s = automaton.simplify().trim()
        # print(LDFA.LDFA.equivalent(automaton, s))
        # print(LDFA.LDFA.equivalent(automaton, result_lstar))
        # print(LDFA.LDFA.equivalent(automaton, result_min))
        # print("[Episode {:>5}] States: ({:>2}, {:>2}), EQ: ({:>4}, {:>4}), MQ: ({:>6}, {:>6}), Results = ({}, {})"
        #       .format(i,
        #               result_lstar.num_of_states(), result_min.num_of_states(),
        #               str(len(learning_lstar.nums_of_states)), str(len(learning_min.nums_of_states)),
        #               str(learning_lstar.table_size()), str(learning_min.table_size()),
        #               learning_min.cur_success, learning_lstar.cur_success))
        print("{}({}).StatesMin,StatesLstar,MQMin,MQLstar,EQMin,EQLstar:{},{},{},{},{},{}".format(
            i,
            states_num,
            result_min.num_of_states(),
            result_lstar.num_of_states(),
            str(learning_min.table_size()),
            str(learning_lstar.table_size()),
            str(len(learning_min.nums_of_states)),
            str(len(learning_lstar.nums_of_states)),
        ))

        EQ_min += len(learning_min.nums_of_states)
        MQ_min += learning_min.table_size()

        EQ_lstar += len(learning_lstar.nums_of_states)
        MQ_lstar += learning_lstar.table_size()

        output_file_lstar.close()
        output_file_min.close()
    print("Score:{}/{}".format(LearningAlgorithm.LearningAlgorithm.successes, count*2))
    print("Total EQ: Lstar: {}, Min: {}".format(EQ_lstar, EQ_min))
    print("Total MQ: Lstar: {}, Min: {}".format(MQ_lstar, MQ_min))

def generate_and_save(count):
    alphabet = ['a', 'b']
    res = {}  # i: {"k": 7, "n": 8} (n is the number of states of the minimal!)
    random.seed(0)
    c = 10001
    for i in range(10001, 10001 + count):
        if i % 100 == 0:
            time.sleep(2)
        #     with open('Generated/tmp_summary.txt', 'w') as res_file:
        #         res_file.write(str(res))

        k = random.randint(50, 100)
        n = random.randint(10, 70)
        lattice = Lattice.Lattice.numbers_lattice(list(range(k)))
        automaton = generate_random_LDFA(alphabet, lattice, n)

        with open(f"Generated/a{c}.txt", 'w+') as outp:
            automaton.print_automaton(outp)

        vq = lambda word: automaton.run_word(word)
        equiv = lambda automata: True
        oracle = Oracle.Oracle(vq, equiv)

        learning_min = LearningAlgorithm.LearningAlgorithm(lattice, oracle, alphabet,
                                                           table=LearningAlgorithm.LearningAlgorithm.FOLSTAR_TABLE,
                                                           original=automaton)
        result_min = learning_min.run_algorithm()

        if len(set(list(learning_min.table.T.values()))) >= 23:

            learning_lstar = LearningAlgorithm.LearningAlgorithm(lattice, oracle, alphabet,
                                                                 table=LearningAlgorithm.LearningAlgorithm.LSTAR_TABLE,
                                                                 original=automaton)
            result_lstar = learning_lstar.run_algorithm()

            res[c] = {"k": k, "n": len(result_min.states), "n_lstar": len(result_lstar.states),
                      "MQ_min": learning_min.table_size(), "MQ_lstar": learning_lstar.table_size(),
                      "EQ_min": learning_min.EQs, "EQ_lstar": learning_lstar.EQs, "real_k": len(set(list(learning_min.table.T.values())))}

            print(f'{c}: {res[c]},')

            c += 1
        else:
            print("#")

    with open('Generated/summary_extra.txt', 'w') as res_file:
        res_file.write(str(res))
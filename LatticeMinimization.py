from typing import Dict, List, Set
from Lattice import *
from LDFA import LDFA
from pythomata import SimpleDFA
import random

# Here we assume that the lattice is a full ordered lattice where A=[0,1,...,m]


def minimize_LDFA(ldfa, alphabet, lattice):
    m_is = {}
    mis_to_ldfa = {}
    ldfa_to_mis = {}
    minimized_mis = {}
    for l in lattice.lattice_set:
        m_i = construct_m_i(ldfa, alphabet, lattice, l)
        m_is[l] = m_i
        minimized_mis[l] = m_i.minimize()
        mis_to_ldfa[l], ldfa_to_mis[l] = relate_mi_with_ldfa(l, m_i, minimized_mis[l], ldfa)

    minimize_transition_values(ldfa, m_is)

    # print(m_is)
    print(mis_to_ldfa)
    print(ldfa_to_mis)

    H = []
    for H_i in mis_to_ldfa:
        to_add = mis_to_ldfa[H_i].values()
        to_add = [set(list(s)) for s in to_add]
        H.append(to_add)
    # print("H", H)
    P_star = find_minimal_partition(set(ldfa.states.keys()), H)
    # print(P_star)


    return P_star


def construct_m_i(m, alphabet, lattice, l):
    reachable = reachable_using_l(m, l)
    states = []
    for s in reachable:
        s_reachable = reachable_using_l(m, l, state_from=s)
        states_with_l = list(filter(lambda state: m.states[state].value, s_reachable))
        if len(states_with_l) > 0:
            states.append(s)

    accepting_states = [s for s in states if lattice.order(l, m.states[s].value)]
    initial_state = [s for s in states if m.q_0(s) != lattice.get_min()][0]

    # transition is of the form state.transitions = {sigma: (value, next_state)...} We check that the value is
    # greater than l.
    transitions = {state: {sigma: m.states[state].transitions[sigma][0][1] for sigma in alphabet
                           if lattice.order(l, m.states[state].transitions[sigma][0][0])}
                   for state in states}

    m_i = SimpleDFA(set(states), set(alphabet), initial_state, set(accepting_states), transitions)

    return m_i


def relate_mi_with_ldfa(l, m_i: SimpleDFA, minimized_mi: SimpleDFA, ldfa):
    mi_to_ldfa = {}
    ldfa_to_mi = {}

    to_reach = find_words_for_states(ldfa, alphabet)
    to_reach = {s: to_reach[s] for s in m_i.states}

    for s in to_reach:
        mi_state = run_word_for_state(minimized_mi, to_reach[s])
        mi_to_ldfa[mi_state] = [s] if mi_state not in mi_to_ldfa else mi_to_ldfa[mi_state] + [s]
        ldfa_to_mi[s] = mi_state

    print(l, mi_to_ldfa)

    return mi_to_ldfa, ldfa_to_mi


def reachable_using_l(ldfa, l, state_from=None):
    if state_from is None:
        state_from = ldfa.initial_state()
    q = [state_from]
    reachable_states = [state_from]
    while len(q) > 0:
        cur = q.pop(0)
        nexts = ldfa.states[cur].transitions
        for sigma in alphabet:
            value, next_state = nexts[sigma][0]  # trans_tuple[2]
            if ldfa.lattice.order(l, value) and next_state not in reachable_states:
                reachable_states.append(next_state)
                q.append(next_state)
    return reachable_states


def minimize_transition_values(ldfa, mis: Dict[int, SimpleDFA]):
    # we want to find the minimal possible value for every transition in ldfa
    # we do so by finding the maximal mi in which the transition is found, and that i is its value.
    for state in ldfa.states:
        for sigma in ldfa.alphabet:
            ldfa.set_transition_value(state, sigma, ldfa.lattice.get_min())
            for l in mis:
                if state in mis[l].states and sigma in mis[l].transition_function[state]:
                    ldfa.set_transition_value(state, sigma, l)
    # ldfa.print_automaton()


def run_word_for_state(m: SimpleDFA, word):
    cur = m.initial_state
    for sigma in word:
        nexts = m.get_transitions_from(cur)
        trans_tuple = next(filter(lambda trans: sigma in trans, nexts), None)
        cur = trans_tuple[2]
    return cur


def find_words_for_states(m: LDFA, alphabet):
    q = []
    q.append(m.initial_state())
    words_for_states = {m.initial_state(): ""}
    while len(q) > 0:
        cur = q.pop(0)
        nexts = m.states[cur].transitions
        for sigma in alphabet:
            next_state = nexts[sigma][0][1]  # trans_tuple[2]
            if next_state not in words_for_states:
                words_for_states[next_state] = words_for_states[cur] + sigma
                q.append(next_state)
    return words_for_states


def find_minimal_partition(Q: Set, H: List[List[Set]]):
    """
    Find the minimal partition that is consistent with the received transitions.

    :param Q: the set of elements (states).
    :param H: a list of all partitions to be consistent with.
            each partition contains sets of elements from Q
    :return: A minimal partition that is consistent with all partitions in H,
            containing all elements in Q.
    """
    P = [Q]
    for h in H:
        new_P = []
        for T in P:
            parts_to_add = []
            for S in h:
                U = T.intersection(S)
                if len(U) > 0:
                    parts_to_add.append(U)
            if len(parts_to_add) == 0:
                new_P.append(T)
            else:
                elements_left = set([q for q in T if not any([q in u for u in parts_to_add])])
                parts_to_add[0] = parts_to_add[0].union(elements_left)
            new_P.extend(parts_to_add)
        P = new_P
    return P


def find_minimal_partition_with_bonus(Q: Set, H: List[List[Set]], bonus_H: List[Set]):
    """
    Find the minimal partition that is consistent with the received transitions.

    :param Q: the set of elements (states).
    :param H: a list of all partitions to be consistent with.
            each partition contains sets of elements from Q
    :return: A minimal partition that is consistent with all partitions in H,
            containing all elements in Q.
    """
    # Every part in each partition will also contain a set of "possible elements" beside it.
    # These are elements that could have been in that part.
    P = [(set(), Q)]
    for h in H + [bonus_H]:
        new_P = []
        for possible, T in P:
            parts_to_add = []
            for S in h:
                U = T.intersection(S)
                if len(U) > 0:
                    parts_to_add.append(U)
            if len(parts_to_add) == 0:
                new_P.append((possible, T))
            else:
                elements_left = set([q for q in T if not any([q in u for u in parts_to_add])])
                for i in range(len(parts_to_add)):
                    parts_to_add[i] = (possible.union(elements_left), parts_to_add[i])
            new_P.extend(parts_to_add)
        # print(P)
        P = new_P

    cur_P = [p[1] for p in P]
    missing = set()

    for q in Q:
        part_q = list(filter(lambda p: q in p, cur_P))
        if not part_q:
            missing.add(q)
            continue

    prev_missing = missing.copy()
    for q in prev_missing:
        for i, (possible, p) in enumerate(P):
            if q in possible and agree(p.union({q}), bonus_H):
                P[i] = possible.difference({q}), p.union({q})
                missing.remove(q)
                break

    added = Q.difference(missing)

    for i, (possible, p) in enumerate(P):
        P[i] = possible.difference(added), p

    for i, (possible, p) in enumerate(P):
        if possible != set() and possible.issubset(missing):
            P.append((set(), possible))
            for ps in possible:
                added.add(ps)
                missing.remove(ps)

    P = [p[1] for p in P]
    return P

def agree(S, H):
    for s1 in S:
        for s2 in S:
            if s1 != s2:
                part_s1 = list(filter(lambda p: s1 in p, H))
                part_s2 = list(filter(lambda p: s2 in p, H))
                if part_s1 != [] and part_s2 != [] and part_s1 != part_s2:
                    return False
    return True


def test1():
    Q = set(list(range(10)))
    H = [[{0, 1, 2}, {3, 5, 6}, {4, 7, 8, 9}],
         [{0, 2, 3}, {1, 5}, {4, 6, 8, 9}],
         [{3}, {5}, {4, 6}]]
    P = find_minimal_partition(Q, H)
    print(P)


def test2():
    Q = {'', 'aa', 'a', 'bb', 'bba', 'ba', 'b', 'bbb', 'ab'}
    H = [[{'', 'aa', 'a', 'bb', 'bba', 'ba', 'b', 'bbb', 'ab'}],
         [{'', 'bba'}, {'a', 'bb', 'ba', 'bbb', 'ab'}, {'b'}],
         [{''}, {'b'}, {'bb'}], [{''}, {'a'}, {'b'}, {'bb'}]]
    P = find_minimal_partition(Q, H)
    print(P)

def test3():
    Q = {'', 'aa', 'a', 'bb', 'bba', 'ba', 'b', 'bbb', 'ab'}
    H = [[{'', 'aa', 'a', 'bb', 'bba', 'ba', 'b', 'bbb', 'ab'}],
         [{'', 'bba'}, {'a', 'bb', 'ba', 'bbb', 'ab'}, {'b'}],
         [{''}, {'b'}, {'bb'}]]
    P = find_minimal_partition(Q, H)
    print(P)

def test1_bonus():
    Q = set(list(range(10)))
    H = [[{0, 1, 2}, {3, 5, 6}, {4, 7, 8, 9}],
         [{0, 2, 3}, {1, 5}, {4, 6, 8, 9}],
         [{3}, {5}, {4, 6}]]
    P = find_minimal_partition_with_bonus(Q, H, [])
    print(P)

def test2_bonus():
    Q = set(list(range(1, 10)))
    H = [[{1, 2}, {3, 4, 5}],
         [{1, 2, 4}, {5}]]
    H_bonus = [{1}, {2, 6}, {3, 4, 5}]
    P = find_minimal_partition_with_bonus(Q, H, H_bonus)
    print(P)


def generate_random_LDFA(alphabet, lattice, number_of_states=10, state_values=True):

    # number_of_states = random.randrange(10, 11)

    states = [str(i) for i in range(number_of_states)]
    q_0 = lambda q: lattice.get_max() if q == '0' else lattice.get_min()
    f_values = {s: random.choice(lattice.lattice_set) for s in states} if state_values \
        else {s: lattice.get_max() for s in states}
    f = lambda q: f_values[q]

    automaton = LDFA(alphabet, lattice, q_0, f)

    for state in states:
        automaton.add_state(state, f(state))

    for state in states:
        for sigma in alphabet:
            dest = random.choice(states)
            trans_value = random.choice(lattice.lattice_set)
            automaton.add_transition(state, sigma, dest, trans_value)

    return automaton


# test2_bonus()

# test3()
# lattice = Lattice.numbers_lattice([0, 1, 2])
# alphabet = ['a', 'b']
# # # random.seed(16)
# a = generate_random_LDFA(alphabet, lattice)
# # a = LDFA.create_by_input(alphabet, lattice, "Examples/automaton13.txt")
# a.print_automaton()
# a_minimized = minimize_LDFA(a, alphabet, lattice)

import sympy
import numpy as np
from numpy.linalg import inv
import random

import Lattice
from Oracle import Oracle
from pandas import *


def word_matrix(M, w, d):
    """
    :param M, w, d: a multiplicity automaton M of dimension d
    and a word w
    :return: the matrix corresponding to w
    """
    m = np.identity(d)
    for l in w:
        m = np.matmul(m, M[l])
    return m


def evaluate_word(M, w, d):
    """
    :param M a multiplicity automaton M
    :param w a word
    :param d dimension of the matrix
    :return: the value corresponding to valuation of w
    assuming a single initial state
    """
    print("Evaluating", M, w, d)
    v = word_matrix(M, w, d)[0]
    final_v = v * M["final"]
    return np.sum(final_v)


def independent_rows(mat):
    """
    :param mat:
    :return: the reduced_matrix, the numbers of independent rows in that matrix
    """
    reduced_matrix, independents = sympy.Matrix(mat).T.rref()
    return reduced_matrix, independents


def get_S_star(HM):
    _, independents_rows = independent_rows(HM["matrix"])
    return [s for i, s in enumerate(HM["S"]) if i in independents_rows]


def independent_col_indexes(mat):
    _, independents_cols = independent_rows(mat.transpose())
    return independents_cols


def filter_matrix(mat):
    reduced_matrix, independents_rows = independent_rows(mat)
    reduced_matrix, independents_cols = independent_rows(mat.transpose())
    row_idx = np.array(independents_rows)
    col_idx = np.array(independents_cols)
    filtered_m = mat[row_idx[:, None], col_idx]
    return filtered_m


# def evaluate_HM(oracle, HM):
#     HM["matrix"] = list(map(lambda s:
#                             list(map(lambda e: oracle.vq(s + e), HM["cols"])), HM["rows"]))


def closing_row(alphabet, HM):
    reduced_matrix, independents_rows = independent_rows(HM["matrix"])
    for row in independents_rows:
        row_title = HM["S"][row]
        for sigma in alphabet:
            if row_title + sigma not in HM["S"]:
                return row_title + sigma
    return ""


def add_row_to_HM(oracle, row, HM):
    new_row = [[oracle.vq(row + e) for e in HM["E"]]]
    HM["matrix"] = np.append(HM["matrix"], new_row, axis=0)
    HM["S"].append(row)


def add_col_to_HM(oracle, col, HM):
    new_col = [[oracle.vq(s + col)] for s in HM["S"]]
    HM["matrix"] = np.hstack((HM["matrix"], new_col))
    HM["E"].append(col)


def close_HM(oracle, alphabet, HM):
    row_to_add = closing_row(alphabet, HM)
    while row_to_add != "":
        add_row_to_HM(oracle, row_to_add, HM)
        row_to_add = closing_row(alphabet, HM)


def word_generator(letters, word_len=6):
    return ''.join(random.choice(letters) for _ in range(word_len))


def counter_example(alphabet, oracle, mu):
    N = 200
    for i in range(N):
        word = word_generator(alphabet, random.randint(0, 8))
        v1 = oracle.vq(word)
        v2 = evaluate_word(mu, word, len(mu["a"]))
        if abs(v1 - v2) > 0.1:
            return word
    return None


def learn_weighted(alphabet, oracle):
    HM = {"S": [""], "E": [""], "matrix": np.array([[oracle.vq("")]])}
    mu = {sigma: np.empty((0, 1), int) for sigma in alphabet}
    add_col_to_HM(oracle, "a", HM)
    add_col_to_HM(oracle, "b", HM)
    while True:
        print(mu)
        print(HM["S"])
        print(HM["E"])
        print("HM\n", DataFrame(HM["matrix"]))
        for sigma in alphabet:
            print(f'mu_{sigma}\n', DataFrame(mu[sigma]))
        close_HM(oracle, alphabet, HM)
        T = filter_matrix(HM["matrix"])
        mu["final"] = T[:, 0]  # the output vector
        mu["init"] = np.array([1] + [0] * (len(mu["final"]) - 1))  # the initial vector (assumed to be [1 0 0 ... 0]

        s_star = get_S_star(HM)
        col_indexes = independent_col_indexes(HM["matrix"])
        for sigma in alphabet:
            mu[sigma] = np.empty((0, len(col_indexes)), int)
            for s in s_star:
                s_sigma_idx = [HM["S"].index(s + sigma)]
                s_sigma_row = HM["matrix"][s_sigma_idx][0]  # get the row of s from the matrix
                s_sigma_row_filtered = s_sigma_row[None, col_indexes]
                # check this
                m_i = np.matmul(s_sigma_row_filtered, inv(T))
                mu[sigma] = np.append(mu[sigma], m_i, axis=0)
            # mu[sigma] = np.matmul(mu[sigma], inv(T))

        counter = counter_example(alphabet, oracle, mu)
        if counter:
            add_col_to_HM(oracle, counter, HM)
        else:
            break

    return mu


# my_language = lambda x: 1 if x == "" else x.count('b') if x.startswith("b") else x.count('a') + 2 * x.count('b')
# my_language = lambda x: len(x) + 1
# n = 3
# my_language = lambda x: 1 if len(x) >= n and x[len(x) - n] == "a" else -1 if x == "" else len(x) if len(x) < n else 1
#
# learn_weighted(["a", "b"], Oracle(my_language,
#                                   lambda a: True))

from Tests.Run_Test import generate_random_LDFA
import Oracle
import LDFA

lattice = Lattice.Lattice.numbers_lattice(list(range(10)))
alphabet = ['a', 'b']
expected_automaton = LDFA.LDFA.create_by_input(alphabet, lattice, "Examples/full_ordered1.txt")
vq = lambda word: expected_automaton.run_word(word)

expected_automaton.print_automaton()

def equiv(automata):
    print("EQ")
    return True

oracle = Oracle.Oracle(vq, equiv)

# m = generate_random_LDFA(['a', 'b'], lattice, number_of_states=10, state_values=True)
# oracle = Oracle.Oracle(lambda w: m.run_word(w), "")

learn_weighted(['a', 'b'], oracle)


#
# m = np.array([[1, 0, 3], [2, 0, 4], [4, 0, 2]])
# print(m)
# reduced_matrix, independents_rows = independent_rows(m)
# print(reduced_matrix)
# print(independents_rows)
#
# reduced_matrix, independents_cols = independent_rows(m.transpose())
# print(reduced_matrix)
# print(independents_cols)
#
# row_idx = np.array(independents_rows)
# col_idx = np.array(independents_cols)
# filtered_m = m[row_idx[:, None], col_idx]
# print(filtered_m)

#
# tc = 0
#
#
# def test(M, w, d, val):
#     global tc
#     tc = tc + 1
#     if val == evaluate_word(M, w, d):
#         print("Test", tc, "passed")
#     else:
#         print("Test", tc, "failed")
#
#
# M = {'a': np.array([[1, 1],
#                     [0, 1]]),
#      'b': np.array([[1, 0],
#                     [0, 1]]),
#      'gamma': [0, 1]}
#
# test(M, "aaabaa", 2, 5)
# test(M, "aaabaab", 2, 5)
# test(M, "aaabaabbbba", 2, 6)
#
# HM = {'cols': ['e', 'a', 'b', 'ba'],
#       'rows': ['e', 'a', 'b', 'aa', 'ab', 'ba', 'bb', 'aaa', 'aab'],
#       'matrix':
#           np.array([[0, 1, 1, 3],
#                     [1, 2, 3, 4],
#                     [1, 1, 2, 2],
#                     [2, 3, 4, 5],
#                     [3, 4, 5, 6],
#                     [1, 1, 2, 2],
#                     [2, 2, 3, 3],
#                     [3, 4, 5, 6],
#                     [4, 5, 6, 7]])}
#
# T_rows = ['e', 'a', 'b', 'aa']
# T = np.array([[0, 1, 1, 3],
#               [1, 2, 3, 4],
#               [1, 1, 2, 2],
#               [2, 3, 4, 5]])
#
# Mea_rows = ['a', 'aa', 'ba', 'aaa']
# Mea = np.array([[1, 2, 3, 4],
#                 [2, 3, 4, 5],
#                 [1, 1, 2, 2],
#                 [3, 4, 5, 6]])
#
# Meb_rows = ['b', 'ab', 'bb', 'aab']
# Meb = np.array([[1, 1, 2, 2],
#                 [3, 4, 5, 6],
#                 [2, 2, 3, 3],
#                 [4, 5, 6, 7]])
#
# invT = inv(T)
# mu_a = np.matmul(Mea, invT)
# mu_b = np.matmul(Meb, invT)
#
# M4st = {'a': mu_a,
#         'b': mu_b,
#         'gamma': [0, 1, 1, 2]}
#
# test(M4st, "bbb", 4, 3)
# test(M4st, "bbbaaaaaa", 4, 3)
# test(M4st, "bbbaaaaaab", 4, 4)
# test(M4st, "aaa", 4, 3)
# test(M4st, "aaab", 4, 5)
# test(M4st, "aaabbbbbba", 4, 16)
#
# print("mu_a is", mu_a)
# print("mu_b is", mu_b)
#

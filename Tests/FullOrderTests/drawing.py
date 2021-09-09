import Lattice
from Tests.Run_Test import generate_random_LDFA
import LDFA
from graphviz import Digraph

N=5
k=20


def plot_automaton1(m):
    edges = {}
    states = set()
    for state in m.states.values():
        states.add(state.title)
        for sigma in state.transitions:
            edge = (state.title, state.transitions[sigma][0][1])
            transition = sigma + "|" + str(state.transitions[sigma][0][0])
            if edge in edges:
                edges[edge] += ", " + transition
            else:
                edges[edge] = transition
    print(edges)

    G = Digraph('G')
    G.attr('graph', pad='1', ranksep='1', nodesep='1')
    G.attr('node', shape='note')

    for state in states:
        G.node(state, state)

    for edge in edges.keys():
        src, dst = edge
        trans = edges[edge]

        G.edge(src, dst, trans)

    G.view()
    G.render('g', format='png')

lattice_set = list(range(k))
alphabet = ['a', 'b']

lattice = Lattice.Lattice.numbers_lattice(lattice_set)

m = LDFA.LDFA.create_by_input(alphabet, lattice, "Examples/temp_test.txt")

# m = generate_random_LDFA(alphabet, lattice, N)

plot_automaton1(m)

import ast
import csv

import matplotlib.pyplot as plt
import numpy as np


def get_data():
    with open("results/summary_complete.txt", 'r') as outp:
        summary = outp.readline()
        data = ast.literal_eval(summary)

        checks = ['n', 'n_lstar', 'MQ_lstar', 'EQ_lstar', 'MQ_FOL', 'EQ_FOL', 'real_k']
        mapping = {}
        for i in data:
            # if i > 870:
            #     break
            cur = data[i]
            n = cur['n']
            k = cur['real_k']  # round(cur['real_k'] / 3) * 3
            # if cur["MQ_lstar"] > 100000:
            #     continue

            if (n, k) not in mapping:
                mapping[(n, k)] = {}

            for check in checks:
                if check not in mapping[(n, k)]:
                    mapping[(n, k)][check] = []
                mapping[(n, k)][check] += [cur[check]]

        return mapping

def graph_value(to_check):
    mapping = get_data()

    ns, ks = zip(*list(mapping.keys()))
    vals = [sum(d[to_check])/len(d[to_check]) for d in mapping.values()]

    z = vals
    x = ns
    y = ks

    # Creating figure
    fig = plt.figure(figsize=(10, 7))
    ax = plt.axes(projection="3d")

    # Creating plot
    ax.scatter3D(x, y, z, color="green")
    plt.title("simple 3D scatter plot")

    plt.xlabel("Number of states")
    plt.ylabel("Lattice Size")

    # show plot
    plt.show()

def compare_values(to_check1, to_check2, title):
    mapping = get_data()

    ns, ks = zip(*list(mapping.keys()))
    vals1 = [sum(d[to_check1])/len(d[to_check1]) for d in mapping.values()]
    vals2 = [sum(d[to_check2])/len(d[to_check2]) for d in mapping.values()]

    z1 = vals1
    z2 = vals2
    x = ns
    y = ks

    # Creating figure
    fig = plt.figure(figsize=(10, 7))
    ax = plt.axes(projection="3d")

    # Creating plot
    p1 = ax.scatter3D(x, y, z1, color="green")
    p2 = ax.scatter3D(x, y, z2, color="blue", alpha=0.25)
    plt.title(to_check1 + " vs " + to_check2)

    # Creating plot
    # p1 = plt.scatter(x, y1, color="green")
    # p2 = plt.scatter(x, y2, color="blue")

    plt.legend((p1, p2),
               (to_check1, to_check2),
               scatterpoints=1,
               loc='upper left',
               ncol=3,
               fontsize=8)


    plt.xlabel("Number of states")
    plt.ylabel("Lattice Size")

    # show plot
    plt.show()

def compare_values_2d(to_check1, to_check2, title, n_or_k=False):
    mapping = get_data()

    ns, ks = zip(*list(mapping.keys()))
    vals1 = [sum(d[to_check1])/len(d[to_check1]) for d in mapping.values()]
    vals2 = [sum(d[to_check2])/len(d[to_check2]) for d in mapping.values()]

    x = ks if n_or_k else ns
    y1 = vals1
    y2 = vals2

    # Creating plot
    p1 = plt.scatter(x, y1, color="magenta", alpha=0.75)
    p2 = plt.scatter(x, y2, color="blue", alpha=0.2)
    plt.title(to_check1 + " vs " + to_check2)

    plt.legend((p1, p2),
               (to_check1, to_check2),
               scatterpoints=1,
               loc='upper left',
               ncol=3,
               fontsize=8)

    if n_or_k:
        plt.xlabel("Lattice Size")
    else:
        plt.xlabel("Number of states")
    plt.ylabel(title)

    # show plot
    plt.show()


def direct_compare(to_check1, to_check2, title, n_or_k=False):
    mapping = get_data()

    tuples = []
    for (n, k) in mapping.keys():
        cur = mapping[(n, k)]
        if n_or_k:
            n, k = k, n
        tuples += zip(cur[to_check1], cur[to_check2], [n] * len(cur[to_check1]))

    tuples = sorted(tuples, key=lambda t: t[0])
    tuples = list(filter(lambda t: t[0]< 20000, tuples))
    print(tuples)
    t1, t2, ns = zip(*(tuples))
    t1 = [round(t, 4) for t in t1]

    fig, ax = plt.subplots()

    p1 = ax.scatter(t1, t2, zorder=1)

    plt.title(to_check1 + " vs " + to_check2)

    ax.set_xlabel(to_check1)
    ax.set_ylabel(to_check2)
    plt.grid(True)

    # show plot
    plt.show()


def compare_values_2d_avg(checks, title, checks_titles, n_or_k='n'):
    colors = ['magenta', 'blue', 'green', 'red']
    mapping = get_data()

    vals = {}
    for (n, k) in mapping.keys():
        cur = mapping[(n, k)]
        avg_lstar = sum(cur['n_lstar'])/len(cur['n_lstar'])
        ex_val = {'n': n, 'k': k, 'n*k': round(n * k / 40) * 40, 'n_lstar': round(avg_lstar / 30) * 30}
        n = ex_val[n_or_k]
        # if n_or_k:
        #     n, k = k, n
        if n not in vals:
            vals[n] = []
        chs = [cur[to_check] for to_check in checks]
        vals[n] += zip(*chs)

    count = []
    max_count = 0
    stds = {}
    for n in vals:
        count += [n] * len(vals[n])
        max_count = max(max_count, len(vals[n]))

        vs = [[v[i] for v in vals[n]] for i in range(len(checks))]
        avgs = [sum(v)/len(v) for v in vs]  # [np.median(v) for v in vs]


        vals[n] = avgs

    x, ys = zip(*(vals.items()))
    ys = zip(*ys)

    fig, ax = plt.subplots()

    ax2 = ax.twinx()
    ax2.set_ylabel("Count")

    ax2.hist(count, bins=len(x), color="grey", histtype='bar', ec='black', alpha=0.25, zorder=0)

    ps = []
    for i, y in enumerate(ys):
        p = ax.scatter(x, y, facecolors='none', edgecolors=colors[i], zorder=1)
        ps.append(p)

    plt.title(title)

    ax2.set_ylim((0, max_count + 10))

    plt.legend(ps,
               checks_titles,
               scatterpoints=1,
               loc='upper left',
               ncol=3,
               fontsize=8)

    x_axis = {'k': "Lattice Size", 'n': "Number of states", 'n*k': "Lattice Size * Number of states", 'n_lstar': "Number of States in Pumped Automaton"}
    ax.set_xlabel(x_axis[n_or_k])

    ax.set_ylabel(title)
    plt.grid(True)

    n_or_k = n_or_k.replace('*', '')
    title = title.replace(' ', '_')
    title = title.replace('*', '_')
    plt.savefig(f'results/real_k_{title}_{n_or_k}.png')

def data_to_table():
    data = get_data()
    keys = ['k', 'n', 'n_lstar', 'MQ_FOL', 'MQ_lstar', 'EQ_FOL', 'EQ_lstar', 'real_k']

    a = [[data[c][key] for key in keys] for c in data]

    with open("Tests/FullOrderTests/results/all_data.csv", "w+") as my_csv:
        csvWriter = csv.writer(my_csv)
        csvWriter.writerow(keys)
        csvWriter.writerows(a)

def graph_all():
    compare_values_2d_avg(["n", "n_lstar"], "Number of States", ["FOL*", "L*"], 'k')
    compare_values_2d_avg(["MQ_FOL", "MQ_lstar"], "Number of VQs", ["FOL*", "L*"], 'k')
    compare_values_2d_avg(["EQ_FOL", "EQ_lstar"], "Number of EQs", ["FOL*", "L*"], 'k')
    compare_values_2d_avg(["n", "n_lstar"], "Number of States", ["FOL*", "L*"], 'n')
    compare_values_2d_avg(["MQ_FOL", "MQ_lstar"], "Number of VQs", ["FOL*", "L*"], 'n')
    compare_values_2d_avg(["EQ_FOL", "EQ_lstar"], "Number of EQs", ["FOL*", "L*"], 'n')
    compare_values_2d_avg(["MQ_FOL", "MQ_lstar"], "Number of VQs", ["FOL*", "L*"], 'n*k')
    compare_values_2d_avg(["EQ_FOL", "EQ_lstar"], "Number of EQs", ["FOL*", "L*"], 'n*k')
    compare_values_2d_avg(["n", "n_lstar"], "Number of States", ["FOL*", "L*"], 'n*k')

print(get_data())
graph_all()

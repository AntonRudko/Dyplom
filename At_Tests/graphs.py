import time
import random
import tracemalloc
import matplotlib.pyplot as plt

from Algoritms.class_dfa_nfa import NFA
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset

def gen_nfa(n, alphabet, p):
    states = {f"q{i}" for i in range(n)}
    start = "q0"
    acc = {s for s in states if random.random() < 0.3} or {"q0"}
    tr = {}
    for s in states:
        for a in alphabet:
            t = {q for q in states if random.random() < p}
            if t:
                tr[(s, a)] = t
    return NFA(states, alphabet, tr, start, acc)

def height_nfa(n):
    states = {f"q{i}" for i in range(n)}
    start = "q0"
    acc = {f"q{n-1}"}
    tr = {}
    alphabet = {"0", "1"}
    for i in range(n-1):
        tr[(f"q{i}", "0")] = {f"q{i+1}"}
    for i in range(n):
        tr[(f"q{i}", "1")] = {f"q0"}
    return NFA(states, alphabet, tr, start, acc)

def avg_time(alg, nfa, r):
    t = 0
    for _ in range(r):
        s = time.perf_counter()
        alg(nfa)
        t += time.perf_counter() - s
    return t / r

def graph_time_vs_states():
    alphabet = {"0","1","2"}
    sizes = [50,100,200,400,600]
    res_sc, res_brz, res_transset = [],[],[]
    for n in sizes:
        nfas = [gen_nfa(n, alphabet, 0.1) for _ in range(5)]
        res_sc.append(sum(avg_time(determinize_nfa, x, 20) for x in nfas)/5)
        res_brz.append(sum(avg_time(determinize_brz, x, 20) for x in nfas)/5)
        res_transset.append(sum(avg_time(determinize_transset, x, 20) for x in nfas)/5)

    plt.figure(figsize=(9,5))
    plt.plot(sizes,res_sc,"ro-",label="Subset")
    plt.plot(sizes,res_brz,"ms-",label="Brzozowski")
    plt.plot(sizes,res_transset,"b^-",label="transset")
    plt.xlabel("NFA states")
    plt.ylabel("Time (s)")
    plt.title("Time vs Number of NFA states")
    plt.grid(True,linestyle="--",alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig("Graphs/time_vs_states.png")
    plt.show()

def graph_dfa_size_vs_nfa_size():
    alphabet = {"0", "1", "2"}
    sizes = [20, 40, 60, 80, 100, 150, 200, 300,400,500,600]
    automata_per_size = 6

    sc_sizes = []
    brz_sizes = []
    transset_sizes = []

    for n in sizes:
        nfas = [gen_nfa(n, alphabet, 0.1) for _ in range(automata_per_size)]

        sc_sizes.append(sum(len(determinize_nfa(nfa).states) for nfa in nfas) / automata_per_size)
        brz_sizes.append(sum(len(determinize_brz(nfa).states) for nfa in nfas) / automata_per_size)
        transset_sizes.append(sum(len(determinize_transset(nfa).states) for nfa in nfas) / automata_per_size)

    plt.figure(figsize=(10,6))

    plt.plot(sizes, sc_sizes, "ro-", label="Subset")
    plt.plot(sizes, brz_sizes, "ms-", label="Brzozowski")
    plt.plot(sizes, transset_sizes, "b^-", label="transset")

    plt.xlabel("NFA size")
    plt.ylabel("DFA size")
    plt.title("DFA size vs NFA size for different determinization algorithms")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()

    plt.savefig("Graphs/dfa_size_all_methods.png")
    plt.show()

def measure_memory(func, nfa):
    tracemalloc.start()
    func(nfa)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024

def graph_ram_usage():
    alphabet = {"0", "1", "2"}
    sizes = [50, 100, 200, 300, 400,450,550,600,650]
    res_sc, res_brz, res_transset = [], [], []

    for n in sizes:
        nfas = [gen_nfa(n, alphabet, 0.1) for _ in range(5)]
        m_sc = sum(measure_memory(determinize_nfa, x) for x in nfas) / 5
        m_brz = sum(measure_memory(determinize_brz, x) for x in nfas) / 5
        m_transset = sum(measure_memory(determinize_transset, x) for x in nfas) / 5
        res_sc.append(m_sc)
        res_brz.append(m_brz)
        res_transset.append(m_transset)

    plt.figure(figsize=(10, 6))
    plt.plot(sizes, res_sc, "ro-", label="Subset")
    plt.plot(sizes, res_brz, "ms-", label="Brzozowski")
    plt.plot(sizes, res_transset, "b^-", label="transset")
    plt.xlabel("NFA size")
    plt.ylabel("Peak RAM (KB)")
    plt.title("RAM usage during determinization")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig("Graphs/ram_usage.png")
    plt.show()

if __name__ == "__main__":
    graph_ram_usage()
    graph_time_vs_states()
    graph_dfa_size_vs_nfa_size()

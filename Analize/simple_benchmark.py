import time
import random

from Algoritms.class_dfa_nfa import NFA

from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset

def generate_random_nfa(num_states, alphabet, edge_prob=0.15, accept_prob=0.3):
    states = {f"q{i}" for i in range(num_states)}
    start_state = "q0"
    accept_states = {s for s in states if random.random() < accept_prob}
    if not accept_states:
        accept_states = {"q0"}
    transitions = {}
    for s in states:
        for a in alphabet:
            targets = set()
            for t in states:
                if random.random() < edge_prob:
                    targets.add(t)
            if targets:
                transitions[(s, a)] = targets
    return NFA(states, alphabet, transitions, start_state, accept_states)

def benchmark_random_determinization():
    alphabet = {"0", "1", "2","4"}
    sizes = [50, 100, 200, 400, 500]
    automata_per_size = 10

    def avg_time(alg, nfas, repeats):
        total = 0.0
        for nfa in nfas:
            for _ in range(repeats):
                start = time.perf_counter()
                alg(nfa)
                total += time.perf_counter() - start
        return total / (len(nfas) * repeats)

    for n in sizes:
        nfas = [generate_random_nfa(n, alphabet) for _ in range(automata_per_size)]
        repeats = 100 if n <= 100 else 30

        t_subset = avg_time(determinize_nfa, nfas, repeats)
        t_brz = avg_time(determinize_brz, nfas, repeats)
        t_transset = avg_time(determinize_transset, nfas, repeats)

        print(f"States: {n}")
        print(f"  determinize_sub_set avg: {t_subset:.6f} s")
        print(f"  determinize_brz avg: {t_brz:.6f} s")
        print(f"  determinize_transset avg: {t_transset:.6f} s")
        print()
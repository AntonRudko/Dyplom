import time
import random

from Algoritms.class_dfa_nfa import NFA

from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms.qsc import determinize_qsc

def generate_random_nfa(num_states, alphabet, edge_prob=0.15, accept_prob=0.3):
    states = {f"q{i}" for i in range(num_states)}
    state_list = [f"q{i}" for i in range(num_states)]
    alpha_list = sorted(alphabet)
    start_state = "q0"

    accept_states = {s for s in states if random.random() < accept_prob}
    if not accept_states:
        accept_states = {random.choice(state_list[1:])} if num_states > 1 else {"q0"}

    transitions = {}

    # Spine: ланцюг q0→q1→...→q(n-1) для гарантії зв'язності
    for i in range(num_states - 1):
        a = random.choice(alpha_list)
        key = (state_list[i], a)
        transitions.setdefault(key, set()).add(state_list[i + 1])

    # Гарантія недетермінізму: додаємо мінімум одну розгалужену пару на стан
    for i in range(num_states):
        a = random.choice(alpha_list)
        t1 = random.choice(state_list)
        t2 = random.choice(state_list)
        while t2 == t1 and num_states > 1:
            t2 = random.choice(state_list)
        key = (state_list[i], a)
        transitions.setdefault(key, set()).update({t1, t2})

    # Випадкові ребра (як раніше)
    for s in states:
        for a in alphabet:
            targets = set()
            for t in states:
                if random.random() < edge_prob:
                    targets.add(t)
            if targets:
                transitions.setdefault((s, a), set()).update(targets)

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
        t_qsc = avg_time(determinize_qsc, nfas, repeats)

        print(f"States: {n}")
        print(f"  determinize_sub_set avg: {t_subset:.6f} s")
        print(f"  determinize_brz avg: {t_brz:.6f} s")
        print(f"  determinize_transset avg: {t_transset:.6f} s")
        print(f"  determinize_qsc avg: {t_qsc:.6f} s")
        print()
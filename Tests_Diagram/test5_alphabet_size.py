"""
Тест 5: Вплив розміру алфавіту на продуктивність.

Фіксований розмір НКА (80 станів), змінюється кількість символів алфавіту.
Розмір алфавіту впливає на кількість переходів та вартість кожного кроку BFS.

Очікувані результати:
- Час усіх алгоритмів зростає лінійно з |Σ| (множник на BFS-крок)
- Brzozowski зростає найшвидше (|Σ| × 4 проходи)
- Розмір DFA зростає зі збільшенням алфавіту
  (більше символів → більше досяжних підмножин)
"""

import random
import matplotlib.pyplot as plt

from Tests_Diagram.nfa_generators import gen_variable_alphabet, measure
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms.qsc import determinize_qsc

ALGORITHMS = [
    ("Subset",     determinize_nfa,  "ro-"),
    ("Brzozowski", determinize_brz,  "ms-"),
    ("Transset",   determinize_transset, "b^-"),
    ("QSC",        determinize_qsc, "gD-"),
]

NUM_STATES = 15
ALPHABET_SIZES = [2, 3, 4, 6, 8]
EDGE_PROB = 0.04
SAMPLES = 2
REPEATS = 3



def run():
    random.seed(53)
    results = {name: {"time": [], "mem": [], "dfa_size": [], "ops": []}
               for name, _, _ in ALGORITHMS}

    for alpha_sz in ALPHABET_SIZES:
        print(f"|Σ|={alpha_sz}, states={NUM_STATES}, edge_prob={EDGE_PROB}")
        nfas = [gen_variable_alphabet(NUM_STATES, alpha_sz, EDGE_PROB)
                for _ in range(SAMPLES)]

        for name, alg, _ in ALGORITHMS:
            times, mems, sizes, all_ops = [], [], [], []
            for nfa in nfas:
                t, m, s, ops = measure(alg, nfa, REPEATS)
                times.append(t)
                mems.append(m)
                sizes.append(s)
                all_ops.append(ops)

            avg_t = sum(times) / len(times)
            avg_m = sum(mems) / len(mems)
            avg_s = sum(sizes) / len(sizes)
            avg_ops = sum(all_ops) / len(all_ops)

            results[name]["time"].append(avg_t)
            results[name]["mem"].append(avg_m)
            results[name]["dfa_size"].append(avg_s)
            results[name]["ops"].append(avg_ops)

            print(f"  {name:12s}: time={avg_t:.4f}s  mem={avg_m:.1f}KB  DFA≈{avg_s:.0f}  ops≈{avg_ops:.0f}")

    # --- Графіки ---
    fig, axes = plt.subplots(2, 2, figsize=(18, 10))

    ax = axes[0, 0]
    for name, _, style in ALGORITHMS:
        ax.plot(ALPHABET_SIZES, results[name]["time"], style, label=name, markersize=6)
    ax.set_xlabel("Alphabet size |Σ|")
    ax.set_ylabel("Time (s)")
    ax.set_title(f"Test 5: Alphabet Size Impact — Time (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    ax = axes[0, 1]
    for name, _, style in ALGORITHMS:
        ax.plot(ALPHABET_SIZES, results[name]["mem"], style, label=name, markersize=6)
    ax.set_xlabel("Alphabet size |Σ|")
    ax.set_ylabel("Peak RAM (KB)")
    ax.set_title(f"Test 5: Alphabet Size Impact — Memory (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    ax = axes[1, 0]
    for name, _, style in ALGORITHMS:
        ax.plot(ALPHABET_SIZES, results[name]["dfa_size"], style, label=name, markersize=6)
    ax.set_xlabel("Alphabet size |Σ|")
    ax.set_ylabel("DFA states")
    ax.set_title(f"Test 5: Alphabet Size Impact — DFA Size (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    ax = axes[1, 1]
    for name, _, style in ALGORITHMS:
        ax.plot(ALPHABET_SIZES, results[name]["ops"], style, label=name, markersize=6)
    ax.set_xlabel("Alphabet size |Σ|")
    ax.set_ylabel("Operations")
    ax.set_title(f"Test 5: Alphabet Size Impact — Operations (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    plt.tight_layout()
    plt.savefig("Tests_Diagram/test5_alphabet_size.png", dpi=150)
    plt.close()
    print("\nSaved: Tests_Diagram/test5_alphabet_size.png")


if __name__ == "__main__":
    run()
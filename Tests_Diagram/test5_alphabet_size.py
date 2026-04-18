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
from Tests_Diagram.cache import load_cache, save_cache, BASE_SOURCES
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset

ALGORITHMS = [
    ("Subset",     determinize_nfa,  "ro-"),
    ("Brzozowski", determinize_brz,  "ms-"),
    ("Transset",   determinize_transset, "b^-"),
]

NUM_STATES = 15
ALPHABET_SIZES = [2, 3, 4, 6, 8]
EDGE_PROB = 0.04
SAMPLES = 2
REPEATS = 3

_PARAMS = {
    "NUM_STATES": NUM_STATES,
    "ALPHABET_SIZES": ALPHABET_SIZES,
    "EDGE_PROB": EDGE_PROB,
    "SAMPLES": SAMPLES,
    "REPEATS": REPEATS,
    "SEED": 53,
}


def _compute():
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

    return results


def _plot(results):
    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(ALPHABET_SIZES, results[name]["time"], style, label=name, markersize=6)
    ax.set_xlabel("Alphabet size |Σ|")
    ax.set_ylabel("Time (s)")
    ax.set_title(f"Test 5: Alphabet Size Impact — Time (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test5_alphabet_size_time.png", dpi=150)
    plt.close()
    print("\nSaved: Tests_Diagram/test5_alphabet_size_time.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(ALPHABET_SIZES, results[name]["mem"], style, label=name, markersize=6)
    ax.set_xlabel("Alphabet size |Σ|")
    ax.set_ylabel("Peak RAM (KB)")
    ax.set_title(f"Test 5: Alphabet Size Impact — Memory (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test5_alphabet_size_memory.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test5_alphabet_size_memory.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(ALPHABET_SIZES, results[name]["dfa_size"], style, label=name, markersize=6)
    ax.set_xlabel("Alphabet size |Σ|")
    ax.set_ylabel("DFA states")
    ax.set_title(f"Test 5: Alphabet Size Impact — DFA Size (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test5_alphabet_size_dfa_size.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test5_alphabet_size_dfa_size.png")


def run():
    results = load_cache("test5", _PARAMS, BASE_SOURCES)
    if results is None:
        results = _compute()
        save_cache("test5", _PARAMS, BASE_SOURCES, results)
    _plot(results)


if __name__ == "__main__":
    run()

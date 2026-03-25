"""
Тест 1: Експоненційний вибух (worst-case).

НКА сімейства "n-й символ з кінця": n+1 стан → 2^n станів ДКА.
Демонструє як час та пам'ять зростають експоненційно.

Очікувані результати:
- Subset, Transset: експоненційне зростання часу та пам'яті
- Brzozowski: ще повільніший (подвійна детермінізація + реверс)
- Всі алгоритми дають 2^n станів (неможливо зменшити)
"""

import matplotlib.pyplot as plt

from Tests_Diagram.nfa_generators import gen_nth_from_last, measure
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms.lazy_subset import determinize_lazy

ALGORITHMS = [
    ("Subset",     determinize_nfa,  "ro-"),
    ("Brzozowski", determinize_brz,  "ms-"),
    ("Transset",   determinize_transset, "b^-"),
    ("Lazy",       determinize_lazy, "cv-"),
]

SIZES = [4, 5, 6, 7, 8, 9, 10]
REPEATS = 5



def run():
    results = {name: {"time": [], "mem": [], "dfa_size": [], "ops": []} for name, _, _ in ALGORITHMS}

    for n in SIZES:
        nfa = gen_nth_from_last(n)
        print(f"n={n}, NFA states={len(nfa.states)}, expected DFA=2^{n}={2**n}")

        for name, alg, _ in ALGORITHMS:
            t, m, s, ops = measure(alg, nfa, REPEATS)
            results[name]["time"].append(t)
            results[name]["mem"].append(m)
            results[name]["dfa_size"].append(s)
            results[name]["ops"].append(ops)
            print(f"  {name:12s}: time={t:.4f}s  mem={m:.1f}KB  DFA states={s}  ops={ops}")

    # --- Графіки ---
    fig, axes = plt.subplots(2, 2, figsize=(18, 10))

    ax = axes[0, 0]
    for name, _, style in ALGORITHMS:
        ax.plot(SIZES, results[name]["time"], style, label=name, markersize=6)
    ax.set_xlabel("NFA parameter n (states = n+1)")
    ax.set_ylabel("Time (s)")
    ax.set_title("Test 1: Exponential Blowup — Time")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    # --- Графік 2: Пам'ять ---
    ax = axes[0, 1]
    for name, _, style in ALGORITHMS:
        ax.plot(SIZES, results[name]["mem"], style, label=name, markersize=6)
    ax.set_xlabel("NFA parameter n (states = n+1)")
    ax.set_ylabel("Peak RAM (KB)")
    ax.set_title("Test 1: Exponential Blowup — Memory")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    # --- Графік 3: Розмір DFA ---
    ax = axes[1, 0]
    for name, _, style in ALGORITHMS:
        ax.plot(SIZES, results[name]["dfa_size"], style, label=name, markersize=6)
    ax.plot(SIZES, [2**n for n in SIZES], "k--", label="2^n (theoretical)", alpha=0.5)
    ax.set_xlabel("NFA parameter n (states = n+1)")
    ax.set_ylabel("DFA states")
    ax.set_title("Test 1: Exponential Blowup — DFA Size")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    # --- Графік 4: Операції ---
    ax = axes[1, 1]
    for name, _, style in ALGORITHMS:
        ax.plot(SIZES, results[name]["ops"], style, label=name, markersize=6)
    ax.set_xlabel("NFA parameter n (states = n+1)")
    ax.set_ylabel("Operations")
    ax.set_title("Test 1: Exponential Blowup — Operations")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    plt.tight_layout()
    plt.savefig("Tests_Diagram/test1_exponential_blowup.png", dpi=150)
    plt.close()
    print("\nSaved: Tests_Diagram/test1_exponential_blowup.png")


if __name__ == "__main__":
    run()

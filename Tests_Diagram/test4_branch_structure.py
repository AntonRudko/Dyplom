"""
Тест 4: Структурований НКА з паралельними гілками.

НКА з k паралельними гілками довжини n, що зливаються в один стан.
Стартовий стан недетерміновано обирає гілку.
Subset Construction створює декартовий добуток гілок.

Очікувані результати:
- Subset: DFA = O(n^k) станів (декартовий добуток позицій у гілках)
- Brzozowski: менший DFA (мінімізація знаходить еквівалентні стани)
- Transset: зливає стани з однаковою transition set (гілки симетричні)
- Різниця у DFA size між алгоритмами найбільш помітна тут
"""

import matplotlib.pyplot as plt

from Tests_Diagram.nfa_generators import gen_multi_branch, measure
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

K = 3  # кількість гілок
BRANCH_LENGTHS = [2, 3, 4, 5, 6, 7]
REPEATS = 5



def run():
    results = {name: {"time": [], "mem": [], "dfa_size": [], "ops": []}
               for name, _, _ in ALGORITHMS}
    nfa_sizes = []

    for n in BRANCH_LENGTHS:
        nfa = gen_multi_branch(n, K)
        nfa_size = len(nfa.states)
        nfa_sizes.append(nfa_size)
        print(f"branches={K}, length={n}, NFA states={nfa_size}")

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
        ax.plot(BRANCH_LENGTHS, results[name]["time"], style, label=name, markersize=6)
    ax.set_xlabel(f"Branch length (k={K} branches)")
    ax.set_ylabel("Time (s)")
    ax.set_title(f"Test 4: Multi-Branch NFA (k={K}) — Time")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    ax = axes[0, 1]
    for name, _, style in ALGORITHMS:
        ax.plot(BRANCH_LENGTHS, results[name]["mem"], style, label=name, markersize=6)
    ax.set_xlabel(f"Branch length (k={K} branches)")
    ax.set_ylabel("Peak RAM (KB)")
    ax.set_title(f"Test 4: Multi-Branch NFA (k={K}) — Memory")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    ax = axes[1, 0]
    for name, _, style in ALGORITHMS:
        ax.plot(BRANCH_LENGTHS, results[name]["dfa_size"], style, label=name, markersize=6)
    ax.plot(BRANCH_LENGTHS, nfa_sizes, "k--", label="NFA size", alpha=0.5)
    ax.set_xlabel(f"Branch length (k={K} branches)")
    ax.set_ylabel("DFA states")
    ax.set_title(f"Test 4: Multi-Branch NFA (k={K}) — DFA Size")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    ax = axes[1, 1]
    for name, _, style in ALGORITHMS:
        ax.plot(BRANCH_LENGTHS, results[name]["ops"], style, label=name, markersize=6)
    ax.set_xlabel(f"Branch length (k={K} branches)")
    ax.set_ylabel("Operations")
    ax.set_title(f"Test 4: Multi-Branch NFA (k={K}) — Operations")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    plt.tight_layout()
    plt.savefig("Tests_Diagram/test4_branch_structure.png", dpi=150)
    plt.close()
    print("\nSaved: Tests_Diagram/test4_branch_structure.png")


if __name__ == "__main__":
    run()

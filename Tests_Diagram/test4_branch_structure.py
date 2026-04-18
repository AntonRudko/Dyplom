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
from Tests_Diagram.cache import load_cache, save_cache, BASE_SOURCES
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset

ALGORITHMS = [
    ("Subset",     determinize_nfa,  "ro-"),
    ("Brzozowski", determinize_brz,  "ms-"),
    ("Transset",   determinize_transset, "b^-"),
]

K = 3  # кількість гілок
BRANCH_LENGTHS = [2, 3, 4, 5, 6, 7]
REPEATS = 5

_PARAMS = {"K": K, "BRANCH_LENGTHS": BRANCH_LENGTHS, "REPEATS": REPEATS}


def _compute():
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

    results["_nfa_sizes"] = nfa_sizes
    return results


def _plot(results):
    nfa_sizes = results.get("_nfa_sizes", BRANCH_LENGTHS)

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(BRANCH_LENGTHS, results[name]["time"], style, label=name, markersize=6)
    ax.set_xlabel(f"Довжина гілки (k={K} гілок)")
    ax.set_ylabel("Час (с)")
    ax.set_title(f"Тест 4: Багатогілковий НСА (k={K}) — Час")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test4_branch_structure_time.png", dpi=150)
    plt.close()
    print("\nSaved: Tests_Diagram/test4_branch_structure_time.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(BRANCH_LENGTHS, results[name]["mem"], style, label=name, markersize=6)
    ax.set_xlabel(f"Довжина гілки (k={K} гілок)")
    ax.set_ylabel("Пікова RAM (КБ)")
    ax.set_title(f"Тест 4: Багатогілковий НСА (k={K}) — Пам'ять")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test4_branch_structure_memory.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test4_branch_structure_memory.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(BRANCH_LENGTHS, results[name]["dfa_size"], style, label=name, markersize=6)
    ax.plot(BRANCH_LENGTHS, nfa_sizes, "k--", label="Розмір НСА", alpha=0.5)
    ax.set_xlabel(f"Довжина гілки (k={K} гілок)")
    ax.set_ylabel("Станів ДСА")
    ax.set_title(f"Тест 4: Багатогілковий НСА (k={K}) — Розмір ДСА")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test4_branch_structure_dfa_size.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test4_branch_structure_dfa_size.png")


def run():
    results = load_cache("test4", _PARAMS, BASE_SOURCES)
    if results is None:
        results = _compute()
        save_cache("test4", _PARAMS, BASE_SOURCES, results)
    _plot(results)


if __name__ == "__main__":
    run()

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
from Tests_Diagram.cache import load_cache, save_cache, BASE_SOURCES
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset

ALGORITHMS = [
    ("Subset",     determinize_nfa,  "ro-"),
    ("Brzozowski", determinize_brz,  "ms-"),
    ("Transset",   determinize_transset, "b^-"),
]

SIZES = [4, 5, 6, 7, 8, 9, 10]
REPEATS = 5

_PARAMS = {"SIZES": SIZES, "REPEATS": REPEATS}


def _compute():
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

    return results


def _plot(results):
    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(SIZES, results[name]["time"], style, label=name, markersize=6)
    ax.set_xlabel("Параметр n НСА (станів = n+1)")
    ax.set_ylabel("Час (с)")
    ax.set_title("Тест 1: Експоненційний вибух — Час")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test1_exponential_blowup_time.png", dpi=150)
    plt.close()
    print("\nSaved: Tests_Diagram/test1_exponential_blowup_time.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(SIZES, results[name]["mem"], style, label=name, markersize=6)
    ax.set_xlabel("Параметр n НСА (станів = n+1)")
    ax.set_ylabel("Пікова RAM (КБ)")
    ax.set_title("Тест 1: Експоненційний вибух — Пам'ять")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test1_exponential_blowup_memory.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test1_exponential_blowup_memory.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(SIZES, results[name]["dfa_size"], style, label=name, markersize=6)
    ax.plot(SIZES, [2**n for n in SIZES], "k--", label="2^n (теоретична межа)", alpha=0.5)
    ax.set_xlabel("Параметр n НСА (станів = n+1)")
    ax.set_ylabel("Станів ДСА")
    ax.set_title("Тест 1: Експоненційний вибух — Розмір ДСА")
    ax.set_yscale("log")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test1_exponential_blowup_dfa_size.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test1_exponential_blowup_dfa_size.png")


def run():
    results = load_cache("test1", _PARAMS, BASE_SOURCES)
    if results is None:
        results = _compute()
        save_cache("test1", _PARAMS, BASE_SOURCES, results)
    _plot(results)


if __name__ == "__main__":
    run()

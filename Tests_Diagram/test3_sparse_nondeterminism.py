"""
Тест 3: Переважно детерміновані НКА (sparse nondeterminism).

НКА з мінімальним недетермінізмом (5% переходів недетерміновані).
Зростає розмір автомата.

Очікувані результати:
- Subset Construction перебудовує весь автомат з нуля
- Brzozowski найповільніший (подвійна детермінізація зайва
  для майже-детермінованих автоматів)
- DFA розміри близькі до NFA (мало нового недетермінізму)
"""

import random
import matplotlib.pyplot as plt

from Tests_Diagram.nfa_generators import gen_sparse_nfa, measure
from Tests_Diagram.cache import load_cache, save_cache, BASE_SOURCES
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset

ALGORITHMS = [
    ("Subset",     determinize_nfa,  "ro-"),
    ("Brzozowski", determinize_brz,  "ms-"),
    ("Transset",   determinize_transset, "b^-"),
]

ALPHABET = {"0", "1", "2"}
SIZES = [5, 8, 11, 14, 17, 20]
NONDET_FRACTION = 0.05
SAMPLES = 3
REPEATS = 5

_PARAMS = {
    "ALPHABET": sorted(ALPHABET),
    "SIZES": SIZES,
    "NONDET_FRACTION": NONDET_FRACTION,
    "SAMPLES": SAMPLES,
    "REPEATS": REPEATS,
    "SEED": 53,
}


def _compute():
    random.seed(53)
    results = {name: {"time": [], "mem": [], "dfa_size": [], "ops": []}
               for name, _, _ in ALGORITHMS}

    for n in SIZES:
        print(f"NFA states={n}, nondet={NONDET_FRACTION*100:.0f}%")
        nfas = [gen_sparse_nfa(n, ALPHABET, NONDET_FRACTION) for _ in range(SAMPLES)]

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

            print(f"  {name:12s}: time={avg_t:.5f}s  mem={avg_m:.1f}KB  DFA≈{avg_s:.0f}  ops≈{avg_ops:.0f}")

    return results


def _plot(results):
    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(SIZES, results[name]["time"], style, label=name, markersize=6)
    ax.set_xlabel("Станів НСА")
    ax.set_ylabel("Час (с)")
    ax.set_yscale("log")
    ax.set_title(f"Тест 3: Розріджений недетермінізм ({NONDET_FRACTION*100:.0f}%) — Час")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test3_sparse_nondeterminism_time.png", dpi=150)
    plt.close()
    print("\nSaved: Tests_Diagram/test3_sparse_nondeterminism_time.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(SIZES, results[name]["mem"], style, label=name, markersize=6)
    ax.set_xlabel("Станів НСА")
    ax.set_ylabel("Пікова RAM (КБ)")
    ax.set_yscale("log")
    ax.set_title(f"Тест 3: Розріджений недетермінізм ({NONDET_FRACTION*100:.0f}%) — Пам'ять")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test3_sparse_nondeterminism_memory.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test3_sparse_nondeterminism_memory.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(SIZES, results[name]["dfa_size"], style, label=name, markersize=6)
    ax.plot(SIZES, SIZES, "k--", label="Розмір НСА (орієнтир)", alpha=0.5)
    ax.set_xlabel("Станів НСА")
    ax.set_ylabel("Станів ДСА")
    ax.set_title(f"Тест 3: Розріджений недетермінізм ({NONDET_FRACTION*100:.0f}%) — Розмір ДСА")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test3_sparse_nondeterminism_dfa_size.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test3_sparse_nondeterminism_dfa_size.png")


def run():
    results = load_cache("test3", _PARAMS, BASE_SOURCES)
    if results is None:
        results = _compute()
        save_cache("test3", _PARAMS, BASE_SOURCES, results)
    _plot(results)


if __name__ == "__main__":
    run()

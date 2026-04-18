"""
Тест 2: Вплив щільності переходів на продуктивність.

Фіксований розмір НКА (100 станів), змінюється щільність ребер.
Демонструє як алгоритми реагують на різний рівень недетермінізму.

Очікувані результати:
- Висока щільність (0.3-0.5): Brzozowski може бути ефективнішим
  (дає мінімальний DFA, менше станів для обробки)
- Transset: менше станів ніж Subset при будь-якій щільності
"""

import random
import matplotlib.pyplot as plt

from Tests_Diagram.nfa_generators import gen_dense_random, measure
from Tests_Diagram.cache import load_cache, save_cache, BASE_SOURCES
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset

ALGORITHMS = [
    ("Subset",     determinize_nfa,  "ro-"),
    ("Brzozowski", determinize_brz,  "ms-"),
    ("Transset",   determinize_transset, "b^-"),
]

NUM_STATES = 30
ALPHABET = {"0", "1", "2"}
DENSITIES = [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.15]
SAMPLES = 3
REPEATS = 5

_PARAMS = {
    "NUM_STATES": NUM_STATES,
    "ALPHABET": sorted(ALPHABET),
    "DENSITIES": DENSITIES,
    "SAMPLES": SAMPLES,
    "REPEATS": REPEATS,
    "SEED": 53,
}


def _compute():
    random.seed(53)
    results = {name: {"time": [], "mem": [], "dfa_size": [], "ops": []}
               for name, _, _ in ALGORITHMS}

    for density in DENSITIES:
        print(f"density={density:.2f}")
        nfas = [gen_dense_random(NUM_STATES, ALPHABET, density) for _ in range(SAMPLES)]

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
        ax.plot(DENSITIES, results[name]["time"], style, label=name, markersize=6)
    ax.set_xlabel("Ймовірність ребра (щільність)")
    ax.set_ylabel("Час (с)")
    ax.set_yscale("log")
    ax.set_title(f"Тест 2: Вплив щільності — Час (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test2_density_impact_time.png", dpi=150)
    plt.close()
    print("\nSaved: Tests_Diagram/test2_density_impact_time.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(DENSITIES, results[name]["mem"], style, label=name, markersize=6)
    ax.set_xlabel("Ймовірність ребра (щільність)")
    ax.set_ylabel("Пікова RAM (КБ)")
    ax.set_yscale("log")
    ax.set_title(f"Тест 2: Вплив щільності — Пам'ять (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test2_density_impact_memory.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test2_density_impact_memory.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(DENSITIES, results[name]["dfa_size"], style, label=name, markersize=6)
    ax.set_xlabel("Ймовірність ребра (щільність)")
    ax.set_ylabel("Станів ДСА")
    ax.set_title(f"Тест 2: Вплив щільності — Розмір ДСА (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test2_density_impact_dfa_size.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test2_density_impact_dfa_size.png")


def run():
    results = load_cache("test2", _PARAMS, BASE_SOURCES)
    if results is None:
        results = _compute()
        save_cache("test2", _PARAMS, BASE_SOURCES, results)
    _plot(results)


if __name__ == "__main__":
    run()

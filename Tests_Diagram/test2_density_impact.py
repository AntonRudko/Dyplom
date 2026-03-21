"""
Тест 2: Вплив щільності переходів на продуктивність.

Фіксований розмір НКА (100 станів), змінюється щільність ребер.
Демонструє як алгоритми реагують на різний рівень недетермінізму.

Очікувані результати:
- Висока щільність (0.3-0.5): Brzozowski може бути ефективнішим
  (дає мінімальний DFA, менше станів для обробки)
- Transset: менше станів ніж Subset при будь-якій щільності
"""

import time
import tracemalloc
import matplotlib.pyplot as plt

from Tests_Diagram.nfa_generators import gen_dense_random
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

NUM_STATES = 30
ALPHABET = {"0", "1", "2"}
DENSITIES = [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.15]
SAMPLES = 3
REPEATS = 5


def measure(alg, nfa, repeats):
    total = 0.0
    for _ in range(repeats):
        start = time.perf_counter()
        alg(nfa)
        total += time.perf_counter() - start
    avg_t = total / repeats

    tracemalloc.start()
    dfa, ops = alg(nfa)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return avg_t, peak / 1024, len(dfa.states), ops


def run():
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

    # --- Графіки ---
    fig, axes = plt.subplots(2, 2, figsize=(18, 10))

    ax = axes[0, 0]
    for name, _, style in ALGORITHMS:
        ax.plot(DENSITIES, results[name]["time"], style, label=name, markersize=6)
    ax.set_xlabel("Edge probability (density)")
    ax.set_ylabel("Time (s)")
    ax.set_yscale("log")
    ax.set_title(f"Test 2: Density Impact — Time (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    ax = axes[0, 1]
    for name, _, style in ALGORITHMS:
        ax.plot(DENSITIES, results[name]["mem"], style, label=name, markersize=6)
    ax.set_xlabel("Edge probability (density)")
    ax.set_ylabel("Peak RAM (KB)")
    ax.set_yscale("log")
    ax.set_title(f"Test 2: Density Impact — Memory (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    ax = axes[1, 0]
    for name, _, style in ALGORITHMS:
        ax.plot(DENSITIES, results[name]["dfa_size"], style, label=name, markersize=6)
    ax.set_xlabel("Edge probability (density)")
    ax.set_ylabel("DFA states")
    ax.set_title(f"Test 2: Density Impact — DFA Size (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    ax = axes[1, 1]
    for name, _, style in ALGORITHMS:
        ax.plot(DENSITIES, results[name]["ops"], style, label=name, markersize=6)
    ax.set_xlabel("Edge probability (density)")
    ax.set_ylabel("Operations")
    ax.set_title(f"Test 2: Density Impact — Operations (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()

    plt.tight_layout()
    plt.savefig("Table/Tests_Diagram/test2_density_impact.png", dpi=150)
    plt.close()
    print("\nSaved: Table/Tests_Diagram/test2_density_impact.png")


if __name__ == "__main__":
    run()

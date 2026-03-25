"""
Тест 6: Overhead epsilon-переходів.

Порівнює алгоритми БЕЗ epsilon та З epsilon на одних і тих самих НКА.
Фіксований розмір (60 станів), змінюється кількість ε-переходів.

Очікувані результати:
- При 0 epsilon-переходів: epsilon-варіанти мають мінімальний overhead
- Зі збільшенням ε: час зростає через обчислення ε-closure
- Brzozowski + ε найбільш чутливий (ε-closure на першій детермінізації)
- Розмір DFA може зменшитися (ε-переходи зливають стани)
"""

import matplotlib.pyplot as plt

from Tests_Diagram.nfa_generators import gen_epsilon_chain, measure
from Algoritms_with_epsilon.sub_set_epsilon import determinize_nfa_epsilon
from Algoritms_with_epsilon.brzozowski_epsilon import determinize_brz_epsilon
from Algoritms_with_epsilon.transset_epsilon import determinize_transset_epsilon
from Algoritms_with_epsilon.lazy_subset_epsilon import determinize_lazy_epsilon

ALGORITHMS = [
    ("Subset+ε",     determinize_nfa_epsilon,      "ro-"),
    ("Brzozowski+ε", determinize_brz_epsilon,      "ms-"),
    ("Transset+ε",   determinize_transset_epsilon,  "b^-"),
    ("Lazy+ε",       determinize_lazy_epsilon,      "cv-"),
]

NUM_STATES = 15
EPSILON_COUNTS = [0, 2, 5, 8, 12, 18]
SAMPLES = 2
REPEATS = 3



def run():
    results = {name: {"time": [], "mem": [], "dfa_size": [], "ops": []}
               for name, _, _ in ALGORITHMS}

    for num_eps in EPSILON_COUNTS:
        print(f"states={NUM_STATES}, ε-transitions={num_eps}")
        nfas = [gen_epsilon_chain(NUM_STATES, num_eps) for _ in range(SAMPLES)]

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

            print(f"  {name:14s}: time={avg_t:.4f}s  mem={avg_m:.1f}KB  DFA≈{avg_s:.0f}  ops≈{avg_ops:.0f}")

    # --- Графіки (bar chart для кращої читабельності дискретних значень ε) ---
    fig, axes = plt.subplots(2, 2, figsize=(18, 10))
    x_pos = range(len(EPSILON_COUNTS))
    x_labels = [str(e) for e in EPSILON_COUNTS]
    n_algs = len(ALGORITHMS)
    bar_width = 0.8 / n_algs
    colors = ["#e74c3c", "#9b59b6", "#3498db", "#1abc9c"]

    ax = axes[0, 0]
    for idx, (name, _, _) in enumerate(ALGORITHMS):
        offset = (idx - n_algs / 2 + 0.5) * bar_width
        ax.bar([p + offset for p in x_pos], results[name]["time"], bar_width,
               label=name, color=colors[idx], alpha=0.85)
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Number of ε-transitions")
    ax.set_ylabel("Time (s)")
    ax.set_title(f"Test 6: Epsilon Overhead — Time (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4, axis="y")
    ax.legend()

    ax = axes[0, 1]
    for idx, (name, _, _) in enumerate(ALGORITHMS):
        offset = (idx - n_algs / 2 + 0.5) * bar_width
        ax.bar([p + offset for p in x_pos], results[name]["mem"], bar_width,
               label=name, color=colors[idx], alpha=0.85)
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Number of ε-transitions")
    ax.set_ylabel("Peak RAM (KB)")
    ax.set_title(f"Test 6: Epsilon Overhead — Memory (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4, axis="y")
    ax.legend()

    ax = axes[1, 0]
    for idx, (name, _, _) in enumerate(ALGORITHMS):
        offset = (idx - n_algs / 2 + 0.5) * bar_width
        ax.bar([p + offset for p in x_pos], results[name]["dfa_size"], bar_width,
               label=name, color=colors[idx], alpha=0.85)
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Number of ε-transitions")
    ax.set_ylabel("DFA states")
    ax.set_title(f"Test 6: Epsilon Overhead — DFA Size (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4, axis="y")
    ax.legend()

    ax = axes[1, 1]
    for idx, (name, _, _) in enumerate(ALGORITHMS):
        offset = (idx - n_algs / 2 + 0.5) * bar_width
        ax.bar([p + offset for p in x_pos], results[name]["ops"], bar_width,
               label=name, color=colors[idx], alpha=0.85)
    ax.set_xticks(list(x_pos))
    ax.set_xticklabels(x_labels)
    ax.set_xlabel("Number of ε-transitions")
    ax.set_ylabel("Operations")
    ax.set_title(f"Test 6: Epsilon Overhead — Operations (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4, axis="y")
    ax.legend()

    plt.tight_layout()
    plt.savefig("Tests_Diagram/test6_epsilon_overhead.png", dpi=150)
    plt.close()
    print("\nSaved: Tests_Diagram/test6_epsilon_overhead.png")


if __name__ == "__main__":
    run()
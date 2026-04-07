"""
Хітмап алгоритмічного порівняння алгоритмів детермінізації.

Три типи порівняння:
  1. Worst-case NFAs (nth-from-last): DFA = 2^n станів для всіх алгоритмів,
     мінімізація не допомагає → видно справжній overhead Brzozowski (2 проходи).
  2. Розмір вихідного DFA: показує, чому Brzozowski "швидший" на random NFAs
     (він будує менший мінімальний DFA).
  3. Час / розмір DFA: нормалізований на кількість станів вихідного DFA →
     чисте алгоритмічне порівняння без впливу мінімізації.

Запуск:
    python -m Tests_Diagram.heatmap_algorithmic
"""

import os
import random
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LogNorm

from Tests_Diagram.nfa_generators import gen_nth_from_last, gen_dense_random
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms.qsc import determinize_qsc

# ── Конфігурація ────────────────────────────────────────────────────────────

ALGORITHMS = [
    ("Subset",     determinize_nfa),
    ("Brzozowski", determinize_brz),
    ("Transset",   determinize_transset),
    ("QSC",        determinize_qsc),
]
ALG_NAMES = [name for name, _ in ALGORITHMS]

# Параметри worst-case (nth-from-last): NFA має n+1 станів, DFA = 2^n
WORSTCASE_N = [4, 5, 6, 7, 8, 9, 10]
WORSTCASE_REPEATS = 30

# Параметри random NFAs (для heatmap 2 і 3)
DENSITIES = [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15, 0.20]
NFA_SIZE = 30       # невеликий розмір, бо DFA може бути великим при low density
SAMPLES = 8
REPEATS = 10

OUTPUT_DIR = "Hitmaps"
ALPHABET = {"0", "1"}


# ── Вимірювання ─────────────────────────────────────────────────────────────

def measure(func, nfa, repeats):
    """Повертає (середній_час, розмір_DFA)."""
    total = 0.0
    dfa_size = 0
    for _ in range(repeats):
        t0 = time.perf_counter()
        dfa, _ = func(nfa)
        total += time.perf_counter() - t0
        dfa_size = len(dfa.states)
    return total / repeats, dfa_size


# ── Heatmap 1: Worst-case (nth-from-last) ───────────────────────────────────

def collect_worstcase():
    """
    Час кожного алгоритму на nth-from-last NFA.
    DFA = 2^n для ВСІХ алгоритмів — мінімізація не дає переваги.
    """
    n_algs = len(ALGORITHMS)
    n_cols = len(WORSTCASE_N)
    times = np.zeros((n_algs, n_cols))

    for j, n in enumerate(WORSTCASE_N):
        nfa = gen_nth_from_last(n)
        print(f"  nth-from-last n={n} (NFA={n+1} states, DFA=2^{n}={2**n})", end="")
        for i, (name, func) in enumerate(ALGORITHMS):
            t, _ = measure(func, nfa, WORSTCASE_REPEATS)
            times[i, j] = t
            print(f"  {name}={t*1000:.2f}ms", end="")
        print()

    return times


def plot_worstcase(times):
    col_labels = [f"n={n}\n(DFA=2^{n})" for n in WORSTCASE_N]

    # Нормалізований
    col_min = times.min(axis=0, keepdims=True)
    col_min[col_min == 0] = 1e-12
    normalized = times / col_min

    fig, axes = plt.subplots(1, 2, figsize=(18, 5))

    # Ліворуч: абсолютний час
    ax = axes[0]
    data_pos = np.where(times > 0, times * 1000, 1e-9)  # у мс
    norm_log = LogNorm(vmin=data_pos.min(), vmax=data_pos.max())
    im = ax.imshow(times * 1000, cmap="RdYlGn_r", aspect="auto", norm=norm_log)
    fig.colorbar(im, ax=ax, label="Час (мс)")
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=9)
    ax.set_yticks(range(len(ALG_NAMES)))
    ax.set_yticklabels(ALG_NAMES)
    ax.set_title("Worst-case NFA: абсолютний час (мс)\n(nth-from-last, DFA = 2ⁿ станів)")
    ax.set_xlabel("Параметр n")
    for i in range(times.shape[0]):
        for j in range(times.shape[1]):
            val = times[i, j] * 1000
            text = f"{val:.1f}" if val < 100 else f"{val:.0f}"
            ax.text(j, i, text, ha="center", va="center", fontsize=9)

    # Праворуч: нормалізований (1.0 = найшвидший у колонці)
    ax = axes[1]
    im2 = ax.imshow(normalized, cmap="RdYlGn_r", aspect="auto",
                    vmin=1.0, vmax=max(normalized.max(), 1.01))
    fig.colorbar(im2, ax=ax, label="Відносний час (1.0 = найшвидший)")
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=9)
    ax.set_yticks(range(len(ALG_NAMES)))
    ax.set_yticklabels(ALG_NAMES)
    ax.set_title("Worst-case NFA: відносний час\n(мінімізація не допомагає — чисте алгоритмічне порівняння)")
    ax.set_xlabel("Параметр n")
    for i in range(normalized.shape[0]):
        for j in range(normalized.shape[1]):
            val = normalized[i, j]
            ax.text(j, i, f"{val:.2f}x", ha="center", va="center", fontsize=9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "algo_heatmap1_worstcase.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


# ── Heatmap 2: Розмір DFA по щільності ─────────────────────────────────────

def collect_dfa_sizes():
    """
    Середній розмір вихідного DFA кожного алгоритму для кожної щільності.
    Показує, чому Brzozowski "швидший" на random NFAs: він будує менший DFA.
    """
    n_algs = len(ALGORITHMS)
    n_cols = len(DENSITIES)
    sizes = np.zeros((n_algs, n_cols))

    for j, density in enumerate(DENSITIES):
        nfas = [gen_dense_random(NFA_SIZE, ALPHABET, density) for _ in range(SAMPLES)]
        print(f"  density={density:.2f}", end="")
        for i, (name, func) in enumerate(ALGORITHMS):
            sz_list = []
            for nfa in nfas:
                dfa, _ = func(nfa)
                sz_list.append(len(dfa.states))
            avg_sz = sum(sz_list) / len(sz_list)
            sizes[i, j] = avg_sz
            print(f"  {name}={avg_sz:.1f}st", end="")
        print()

    return sizes


def plot_dfa_sizes(sizes):
    col_labels = [f"{d:.2f}" for d in DENSITIES]

    # Нормалізуємо: кожен стовпець / мінімальний (Brzozowski зазвичай мінімальний)
    col_min = sizes.min(axis=0, keepdims=True)
    col_min[col_min == 0] = 1e-9
    normalized = sizes / col_min

    fig, axes = plt.subplots(1, 2, figsize=(18, 5))

    # Ліворуч: абсолютний розмір DFA
    ax = axes[0]
    vmax = sizes.max()
    im = ax.imshow(sizes, cmap="RdYlGn_r", aspect="auto", vmin=sizes.min(), vmax=vmax)
    fig.colorbar(im, ax=ax, label="Кількість станів DFA")
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticks(range(len(ALG_NAMES)))
    ax.set_yticklabels(ALG_NAMES)
    ax.set_title(f"Розмір вихідного DFA (n={NFA_SIZE} станів NFA)\nЧому Brzozowski виглядає швидшим: він будує менший DFA")
    ax.set_xlabel("Щільність переходів")
    for i in range(sizes.shape[0]):
        for j in range(sizes.shape[1]):
            val = sizes[i, j]
            ax.text(j, i, f"{val:.0f}", ha="center", va="center", fontsize=9)

    # Праворуч: відносний розмір (1.0 = найменший DFA у стовпці)
    ax = axes[1]
    im2 = ax.imshow(normalized, cmap="RdYlGn_r", aspect="auto", vmin=1.0)
    fig.colorbar(im2, ax=ax, label="Відносний розмір DFA (1.0 = найменший)")
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticks(range(len(ALG_NAMES)))
    ax.set_yticklabels(ALG_NAMES)
    ax.set_title("Відносний розмір DFA (1.0 = мінімальний)\nBrzozowski ≈ 1.0x — завжди мінімальний")
    ax.set_xlabel("Щільність переходів")
    for i in range(normalized.shape[0]):
        for j in range(normalized.shape[1]):
            val = normalized[i, j]
            ax.text(j, i, f"{val:.2f}x", ha="center", va="center", fontsize=9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "algo_heatmap2_dfa_size.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


# ── Heatmap 3: Час / розмір DFA ─────────────────────────────────────────────

def collect_time_per_state():
    """
    Час / кількість станів вихідного DFA.
    Нейтралізує перевагу Brzozowski від мінімізації:
    якщо алгоритм будує менший DFA, він ділиться на менше.
    Результат: "вартість побудови одного стану DFA".
    """
    n_algs = len(ALGORITHMS)
    n_cols = len(DENSITIES)
    cost_per_state = np.zeros((n_algs, n_cols))

    for j, density in enumerate(DENSITIES):
        nfas = [gen_dense_random(NFA_SIZE, ALPHABET, density) for _ in range(SAMPLES)]
        print(f"  density={density:.2f}", end="")
        for i, (name, func) in enumerate(ALGORITHMS):
            costs = []
            for nfa in nfas:
                t, sz = measure(func, nfa, REPEATS)
                if sz > 0:
                    costs.append(t / sz)
            avg_cost = sum(costs) / len(costs) if costs else 0.0
            cost_per_state[i, j] = avg_cost
            print(f"  {name}={avg_cost*1e6:.2f}µs/st", end="")
        print()

    return cost_per_state


def plot_time_per_state(cost_per_state):
    col_labels = [f"{d:.2f}" for d in DENSITIES]

    # Нормалізуємо по стовпцю
    col_min = cost_per_state.min(axis=0, keepdims=True)
    col_min[col_min == 0] = 1e-20
    normalized = cost_per_state / col_min

    fig, axes = plt.subplots(1, 2, figsize=(18, 5))

    # Ліворуч: абсолютна вартість у µs/стан
    ax = axes[0]
    data_us = cost_per_state * 1e6
    data_pos = np.where(data_us > 0, data_us, 1e-12)
    norm_log = LogNorm(vmin=data_pos.min(), vmax=data_pos.max())
    im = ax.imshow(data_us, cmap="RdYlGn_r", aspect="auto", norm=norm_log)
    fig.colorbar(im, ax=ax, label="Час / стан DFA (µs)")
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticks(range(len(ALG_NAMES)))
    ax.set_yticklabels(ALG_NAMES)
    ax.set_title(f"Час на один стан вихідного DFA (µs/стан, n={NFA_SIZE})\nНейтралізує перевагу мінімізації")
    ax.set_xlabel("Щільність переходів")
    for i in range(data_us.shape[0]):
        for j in range(data_us.shape[1]):
            val = data_us[i, j]
            text = f"{val:.2f}" if val < 100 else f"{val:.0f}"
            ax.text(j, i, text, ha="center", va="center", fontsize=9)

    # Праворуч: нормалізований (1.0 = найефективніший)
    ax = axes[1]
    im2 = ax.imshow(normalized, cmap="RdYlGn_r", aspect="auto", vmin=1.0)
    fig.colorbar(im2, ax=ax, label="Відносна вартість/стан (1.0 = найефективніший)")
    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticks(range(len(ALG_NAMES)))
    ax.set_yticklabels(ALG_NAMES)
    ax.set_title("Відносна вартість побудови одного стану DFA\n(чисте алгоритмічне порівняння без впливу мінімізації)")
    ax.set_xlabel("Щільність переходів")
    for i in range(normalized.shape[0]):
        for j in range(normalized.shape[1]):
            val = normalized[i, j]
            ax.text(j, i, f"{val:.2f}x", ha="center", va="center", fontsize=9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "algo_heatmap3_time_per_state.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"Saved: {path}")


# ── Головна функція ──────────────────────────────────────────────────────────

def run():
    random.seed(53)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 65)
    print("АЛГОРИТМІЧНЕ ПОРІВНЯННЯ АЛГОРИТМІВ ДЕТЕРМІНІЗАЦІЇ")
    print("=" * 65)

    print("\n[1/3] Worst-case NFAs (nth-from-last): мінімізація не допомагає")
    worstcase_times = collect_worstcase()
    plot_worstcase(worstcase_times)

    print(f"\n[2/3] Розмір вихідного DFA по щільності (n={NFA_SIZE})")
    dfa_sizes = collect_dfa_sizes()
    plot_dfa_sizes(dfa_sizes)

    print(f"\n[3/3] Час / розмір DFA — чисте алгоритмічне порівняння (n={NFA_SIZE})")
    cost_per_state = collect_time_per_state()
    plot_time_per_state(cost_per_state)

    print("\n" + "=" * 65)
    print(f"ГОТОВО! Файли збережені у {OUTPUT_DIR}/")
    print("  algo_heatmap1_worstcase.png   — worst-case, чисте порівняння")
    print("  algo_heatmap2_dfa_size.png    — розмір DFA (причина 'переваги' Brzozowski)")
    print("  algo_heatmap3_time_per_state.png — час/стан (без впливу мінімізації)")
    print("=" * 65)


if __name__ == "__main__":
    run()

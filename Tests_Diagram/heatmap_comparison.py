"""
Heatmap порівняння алгоритмів детермінізації.

Генерує теплові карти, де:
- Рядки — алгоритми (Subset, Brzozowski, Transset, Lazy)
- Стовпці — рівні щільності NFA або розміри NFA
- Колір — відносна швидкість (час виконання)

Додатково: матриця попарного порівняння «алгоритм A швидший за B на X%».

Запуск:
    python -m Tests_Diagram.heatmap_comparison
"""

import random
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import TwoSlopeNorm, LogNorm

from Tests_Diagram.nfa_generators import gen_dense_random, gen_sparse_nfa
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms.qsc import determinize_qsc

# ── Конфігурація ──────────────────────────────────────────────

ALGORITHMS = [
    ("Subset",     determinize_nfa),
    ("Brzozowski", determinize_brz),
    ("Transset",   determinize_transset),
    ("QSC",        determinize_qsc),
]

ALG_NAMES = [name for name, _ in ALGORITHMS]

# Параметри бенчмарку
DENSITIES = [0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15, 0.20]
NFA_SIZES = [20, 40, 60, 80, 100]
ALPHABET = {"0", "1", "2"}
SAMPLES = 5
REPEATS = 5

OUTPUT_DIR = "Hitmaps"


# ── Вимірювання ───────────────────────────────────────────────

def measure_time(alg_func, nfa, repeats=REPEATS):
    """Середній час виконання алгоритму на одному NFA."""
    total = 0.0
    for _ in range(repeats):
        start = time.perf_counter()
        alg_func(nfa)
        total += time.perf_counter() - start
    return total / repeats


def collect_density_data(num_states=100):
    """
    Збирає дані: час кожного алгоритму для кожного рівня щільності.
    Повертає numpy-масив shape (len(ALGORITHMS), len(DENSITIES)).
    """
    data = np.zeros((len(ALGORITHMS), len(DENSITIES)))

    for j, density in enumerate(DENSITIES):
        nfas = [gen_dense_random(num_states, ALPHABET, density) for _ in range(SAMPLES)]
        print(f"  density={density:.2f}", end="")

        for i, (name, func) in enumerate(ALGORITHMS):
            times = [measure_time(func, nfa) for nfa in nfas]
            avg = sum(times) / len(times)
            data[i, j] = avg
            print(f"  {name}={avg:.4f}s", end="")
        print()

    return data


def collect_size_data(density=0.08):
    """
    Збирає дані: час кожного алгоритму для кожного розміру NFA.
    Повертає numpy-масив shape (len(ALGORITHMS), len(NFA_SIZES)).
    """
    data = np.zeros((len(ALGORITHMS), len(NFA_SIZES)))

    for j, size in enumerate(NFA_SIZES):
        nfas = [gen_dense_random(size, ALPHABET, density) for _ in range(SAMPLES)]
        print(f"  size={size}", end="")

        for i, (name, func) in enumerate(ALGORITHMS):
            times = [measure_time(func, nfa) for nfa in nfas]
            avg = sum(times) / len(times)
            data[i, j] = avg
            print(f"  {name}={avg:.4f}s", end="")
        print()

    return data


def collect_density_size_grid():
    """
    Повна сітка: для кожної пари (розмір, щільність) збирає час кожного алгоритму.
    Повертає dict: alg_name -> numpy array shape (len(NFA_SIZES), len(DENSITIES)).
    """
    grids = {name: np.zeros((len(NFA_SIZES), len(DENSITIES))) for name in ALG_NAMES}

    for si, size in enumerate(NFA_SIZES):
        for dj, density in enumerate(DENSITIES):
            nfas = [gen_dense_random(size, ALPHABET, density) for _ in range(SAMPLES)]
            print(f"  size={size} density={density:.2f}", end="")

            for name, func in ALGORITHMS:
                times = [measure_time(func, nfa) for nfa in nfas]
                avg = sum(times) / len(times)
                grids[name][si, dj] = avg
                print(f"  {name}={avg:.4f}s", end="")
            print()

    return grids


# ── Побудова Heatmap ──────────────────────────────────────────

def plot_time_heatmap(data, row_labels, col_labels, title, xlabel, filename):
    """
    Heatmap абсолютного часу: рядки=алгоритми, стовпці=параметр.
    Кольори: зелений=швидко, червоний=повільно.
    """
    fig, ax = plt.subplots(figsize=(max(10, len(col_labels) * 1.4), 5))

    # Логарифмічна шкала кольору для кращого розрізнення малих значень
    data_positive = np.where(data > 0, data, 1e-9)
    norm = LogNorm(vmin=data_positive.min(), vmax=data_positive.max())
    im = ax.imshow(data, cmap="RdYlGn_r", aspect="auto", norm=norm)
    cbar = fig.colorbar(im, ax=ax, label="Час (с)")

    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels)
    ax.set_xlabel(xlabel)
    ax.set_title(title)

    # Анотації: час у кожній клітинці
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            text = f"{val:.4f}" if val < 1 else f"{val:.2f}"
            color = "white" if val > (data.max() + data.min()) / 2 else "black"
            ax.text(j, i, text, ha="center", va="center", fontsize=9, color=color)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Saved: {filename}")


def plot_normalized_heatmap(data, row_labels, col_labels, title, xlabel, filename):
    """
    Нормалізована heatmap: кожен стовпець нормалізується відносно найшвидшого.
    Значення = відносний час (1.0 = найшвидший, >1 = повільніший).
    """
    col_min = data.min(axis=0, keepdims=True)
    col_min[col_min == 0] = 1e-9
    normalized = data / col_min

    fig, ax = plt.subplots(figsize=(max(10, len(col_labels) * 1.4), 5))

    im = ax.imshow(normalized, cmap="RdYlGn_r", aspect="auto", vmin=1.0)
    cbar = fig.colorbar(im, ax=ax, label="Відносний час (1.0 = найшвидший)")

    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels)
    ax.set_xlabel(xlabel)
    ax.set_title(title)

    for i in range(normalized.shape[0]):
        for j in range(normalized.shape[1]):
            val = normalized[i, j]
            text = f"{val:.2f}x"
            color = "white" if val > (normalized.max() + 1) / 2 else "black"
            ax.text(j, i, text, ha="center", va="center", fontsize=9, color=color)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Saved: {filename}")


def plot_pairwise_speedup(data, alg_names, col_labels, xlabel, filename):
    """
    Матриця попарного порівняння: коефіцієнт Nx (у скільки разів рядок швидший за стовпець).

    >1x = рядок швидший, <1x = рядок повільніший.
    Зелений = швидший, Червоний = повільніший.
    """
    n = len(alg_names)
    # Матриця коефіцієнтів: time_col / time_row (>1 = row faster)
    ratio_matrix = np.ones((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                ratio_matrix[i, j] = 1.0
            else:
                ratios = []
                for c in range(data.shape[1]):
                    if data[i, c] > 0:
                        ratios.append(data[j, c] / data[i, c])
                ratio_matrix[i, j] = sum(ratios) / len(ratios) if ratios else 1.0

    fig, ax = plt.subplots(figsize=(8, 6))

    # Симетрична шкала навколо 1.0
    max_ratio = max(ratio_matrix.max(), 1.0 / ratio_matrix[ratio_matrix > 0].min())
    max_ratio = min(max_ratio, 20.0)  # обмежуємо щоб не спотворювати шкалу
    norm = TwoSlopeNorm(vmin=1.0 / max_ratio, vcenter=1.0, vmax=max_ratio)

    im = ax.imshow(ratio_matrix, cmap="RdYlGn", norm=norm, aspect="auto")
    cbar = fig.colorbar(im, ax=ax, label="Коефіцієнт швидкості (>1 = рядок швидший)")

    ax.set_xticks(range(n))
    ax.set_xticklabels(alg_names)
    ax.set_yticks(range(n))
    ax.set_yticklabels(alg_names)
    ax.set_xlabel("Стовпець (базовий алгоритм)")
    ax.set_ylabel("Рядок (порівнюваний алгоритм)")
    ax.set_title(f"Попарне порівняння: у скільки разів рядок швидший за стовпець\n({xlabel})")

    for i in range(n):
        for j in range(n):
            val = ratio_matrix[i, j]
            if i == j:
                text = "—"
            else:
                text = f"{val:.1f}x"
            color = "white" if val > max_ratio * 0.6 or val < 1.0 / (max_ratio * 0.6) else "black"
            ax.text(j, i, text, ha="center", va="center", fontsize=11,
                    fontweight="bold", color=color)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Saved: {filename}")


def plot_speedup_vs_subset_by_density(data, col_labels, filename):
    """
    Heatmap: прискорення кожного алгоритму відносно Subset для кожної щільності.
    Зелений = швидший за Subset, Червоний = повільніший.
    """
    subset_idx = 0  # Subset is first
    subset_times = data[subset_idx, :]
    other_algs = ALG_NAMES[1:]

    n_algs = len(other_algs)
    n_cols = len(col_labels)
    speedup = np.zeros((n_algs, n_cols))

    for i, name in enumerate(other_algs):
        alg_idx = ALG_NAMES.index(name)
        for j in range(n_cols):
            if subset_times[j] > 0:
                speedup[i, j] = (subset_times[j] - data[alg_idx, j]) / subset_times[j] * 100

    fig, ax = plt.subplots(figsize=(max(10, n_cols * 1.4), 4.5))

    max_abs = max(abs(speedup.min()), abs(speedup.max()), 1)
    norm = TwoSlopeNorm(vmin=-max_abs, vcenter=0, vmax=max_abs)

    im = ax.imshow(speedup, cmap="RdYlGn", norm=norm, aspect="auto")
    cbar = fig.colorbar(im, ax=ax, label="Прискорення відносно Subset (%)")

    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(col_labels)
    ax.set_yticks(range(n_algs))
    ax.set_yticklabels(other_algs)
    ax.set_xlabel("Щільність переходів")
    ax.set_title("Прискорення відносно Subset Construction (%)\nЗелений = швидший, Червоний = повільніший")

    for i in range(n_algs):
        for j in range(n_cols):
            val = speedup[i, j]
            sign = "+" if val > 0 else ""
            text = f"{sign}{val:.1f}%"
            color = "white" if abs(val) > max_abs * 0.6 else "black"
            ax.text(j, i, text, ha="center", va="center", fontsize=9,
                    fontweight="bold", color=color)

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"Saved: {filename}")


def plot_full_grid_heatmap(grids, filename_prefix):
    """
    Для кожного алгоритму: heatmap розмір(Y) x щільність(X) = час.
    Збільшений розмір, єдина кольорова шкала для всіх підграфіків.
    """
    density_labels = [f"{d:.2f}" for d in DENSITIES]
    size_labels = [str(s) for s in NFA_SIZES]

    # Єдиний діапазон кольорів для всіх алгоритмів
    all_vals = np.concatenate([grids[name].ravel() for name in ALG_NAMES])
    all_positive = all_vals[all_vals > 0]
    global_vmin = all_positive.min() if len(all_positive) > 0 else 1e-9
    global_vmax = all_vals.max()
    global_norm = LogNorm(vmin=global_vmin, vmax=global_vmax)

    n_algs = len(ALG_NAMES)
    fig, axes = plt.subplots(2, 2, figsize=(22, 16))
    axes_flat = axes.flatten()

    for idx, name in enumerate(ALG_NAMES):
        ax = axes_flat[idx]
        data = grids[name]

        im = ax.imshow(data, cmap="RdYlGn_r", aspect="auto", norm=global_norm)
        fig.colorbar(im, ax=ax, label="Час (с)")

        ax.set_xticks(range(len(density_labels)))
        ax.set_xticklabels(density_labels, fontsize=10)
        ax.set_yticks(range(len(size_labels)))
        ax.set_yticklabels(size_labels, fontsize=10)
        ax.set_xlabel("Щільність", fontsize=11)
        ax.set_ylabel("Кількість станів NFA", fontsize=11)
        ax.set_title(f"{name}: час детермінізації", fontsize=13)

        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                val = data[i, j]
                text = f"{val:.4f}" if val < 0.01 else (f"{val:.3f}" if val < 1 else f"{val:.1f}")
                color = "white" if val > (global_vmax + global_vmin) / 2 else "black"
                ax.text(j, i, text, ha="center", va="center", fontsize=10, color=color)

    for idx in range(n_algs, len(axes_flat)):
        axes_flat[idx].set_visible(False)

    plt.suptitle("Час детермінізації: розмір NFA × щільність переходів", fontsize=16)
    plt.tight_layout()
    plt.savefig(f"{filename_prefix}_per_algorithm.png", dpi=150)
    plt.close()
    print(f"Saved: {filename_prefix}_per_algorithm.png")


# ── Головна функція ──────────────────────────────────────────

def run():
    """Запуск повного набору heatmap-порівнянь."""
    random.seed(53)
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("HEATMAP ПОРІВНЯННЯ АЛГОРИТМІВ ДЕТЕРМІНІЗАЦІЇ")
    print("=" * 60)

    # 1. Heatmap: алгоритми × щільність (фіксований розмір 100)
    print("\n[1/4] Збір даних: алгоритми × щільність (n=100)")
    density_data = collect_density_data(num_states=100)
    density_labels = [f"{d:.2f}" for d in DENSITIES]

    plot_time_heatmap(
        density_data, ALG_NAMES, density_labels,
        title="Час детермінізації: алгоритми × щільність (n=100)",
        xlabel="Щільність переходів",
        filename=f"{OUTPUT_DIR}/heatmap_time_by_density.png",
    )
    plot_normalized_heatmap(
        density_data, ALG_NAMES, density_labels,
        title="Відносний час: алгоритми × щільність (n=100, 1.0=найшвидший)",
        xlabel="Щільність переходів",
        filename=f"{OUTPUT_DIR}/heatmap_normalized_by_density.png",
    )
    plot_speedup_vs_subset_by_density(
        density_data, density_labels,
        filename=f"{OUTPUT_DIR}/heatmap_speedup_vs_subset.png",
    )

    # 2. Heatmap: алгоритми × розмір NFA (фіксована щільність 0.08)
    print("\n[2/4] Збір даних: алгоритми × розмір NFA (density=0.08)")
    size_data = collect_size_data(density=0.08)
    size_labels = [str(s) for s in NFA_SIZES]

    plot_time_heatmap(
        size_data, ALG_NAMES, size_labels,
        title="Час детермінізації: алгоритми × розмір NFA (density=0.08)",
        xlabel="Кількість станів NFA",
        filename=f"{OUTPUT_DIR}/heatmap_time_by_size.png",
    )
    plot_normalized_heatmap(
        size_data, ALG_NAMES, size_labels,
        title="Відносний час: алгоритми × розмір NFA (density=0.08, 1.0=найшвидший)",
        xlabel="Кількість станів NFA",
        filename=f"{OUTPUT_DIR}/heatmap_normalized_by_size.png",
    )

    # 3. Попарне порівняння (середнє по всіх щільностях)
    print("\n[3/4] Попарне порівняння алгоритмів")
    plot_pairwise_speedup(
        density_data, ALG_NAMES, density_labels,
        xlabel=f"середнє по щільностях {DENSITIES[0]:.2f}–{DENSITIES[-1]:.2f}",
        filename=f"{OUTPUT_DIR}/heatmap_pairwise_comparison.png",
    )

    # 4. Повна сітка: розмір × щільність для кожного алгоритму
    print("\n[4/4] Збір даних: повна сітка розмір × щільність")
    grids = collect_density_size_grid()
    plot_full_grid_heatmap(grids, f"{OUTPUT_DIR}/heatmap_grid")

    print("\n" + "=" * 60)
    print("ГОТОВО! Всі heatmap збережені у", OUTPUT_DIR)
    print("=" * 60)


if __name__ == "__main__":
    run()

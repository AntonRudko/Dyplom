"""
Запуск усіх тестів детермінізації для алгоритмів з ε-замиканнями.

Використання:
    python -m Tests_Diagram.run_all_epsilon          # всі тести
    python -m Tests_Diagram.run_all_epsilon 1 3      # тільки тести 1 і 3
    python -m Tests_Diagram.run_all_epsilon --no-cache
"""

import sys
import os
import random
import matplotlib.pyplot as plt

from Tests_Diagram.nfa_generators import gen_epsilon_chain, measure
from Tests_Diagram.cache import load_cache, save_cache, EPS_SOURCES, ALL_SOURCES
from Algoritms_with_epsilon.sub_set_epsilon import determinize_nfa_epsilon
from Algoritms_with_epsilon.brzozowski_epsilon import determinize_brz_epsilon
from Algoritms_with_epsilon.transset_epsilon import determinize_transset_epsilon

ALGORITHMS = [
    ("Subset+ε",     determinize_nfa_epsilon,      "ro-"),
    ("Brzozowski+ε", determinize_brz_epsilon,      "ms-"),
    ("Transset+ε",   determinize_transset_epsilon,  "b^-"),
]

OUTPUT_DIR = "Tests_Diagram_Epsilon"


# ============================================================
#  Тест 1: Масштабування ε-ланцюга (зростання кількості станів)
# ============================================================

def run_test1():
    SIZES = [8, 10, 12, 15, 18, 20, 25]
    EPS_RATIO = 0.3
    SAMPLES = 3
    REPEATS = 3

    params = {"SIZES": SIZES, "EPS_RATIO": EPS_RATIO, "SAMPLES": SAMPLES, "REPEATS": REPEATS, "SEED": 53}

    results = load_cache("eps_test1", params, EPS_SOURCES)
    if results is None:
        results = {name: {"time": [], "mem": [], "dfa_size": [], "ops": []}
                   for name, _, _ in ALGORITHMS}

        for n in SIZES:
            num_eps = max(1, int(n * EPS_RATIO))
            print(f"  states={n}, ε-transitions={num_eps}")
            nfas = [gen_epsilon_chain(n, num_eps) for _ in range(SAMPLES)]

            for name, alg, _ in ALGORITHMS:
                times, mems, sizes, all_ops = [], [], [], []
                for nfa in nfas:
                    t, m, s, ops = measure(alg, nfa, REPEATS)
                    times.append(t); mems.append(m); sizes.append(s); all_ops.append(ops)

                avg_t = sum(times) / len(times)
                avg_m = sum(mems) / len(mems)
                avg_s = sum(sizes) / len(sizes)
                avg_ops = sum(all_ops) / len(all_ops)

                results[name]["time"].append(avg_t)
                results[name]["mem"].append(avg_m)
                results[name]["dfa_size"].append(avg_s)
                results[name]["ops"].append(avg_ops)

                print(f"    {name:14s}: time={avg_t:.4f}s  mem={avg_m:.1f}KB  "
                      f"DFA≈{avg_s:.0f}  ops≈{avg_ops:.0f}")

        save_cache("eps_test1", params, EPS_SOURCES, results)

    # --- Графіки ---
    metrics = [
        ("time", "Час (с)", "Час", "time", True),
        ("mem", "Пікова RAM (КБ)", "Пам'ять", "memory", True),
        ("dfa_size", "Станів ДСА", "Розмір ДСА", "dfa_size", True),
    ]

    for key, ylabel, title_ua, suffix, use_log in metrics:
        fig, ax = plt.subplots(figsize=(9, 6))
        for name, _, style in ALGORITHMS:
            ax.plot(SIZES, results[name][key], style, label=name, markersize=6)
        ax.set_xlabel("Кількість станів НСА")
        ax.set_ylabel(ylabel)
        ax.set_title(f"Тест ε-1: Масштабування ε-ланцюга — {title_ua} (ε≈30%)")
        if use_log:
            ax.set_yscale("log")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend()
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/eps_test1_chain_scaling_{suffix}.png"
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"  Saved: {path}")


# ============================================================
#  Тест 2: Вплив кількості ε-переходів (overhead)
# ============================================================

def run_test2():
    NUM_STATES = 15
    EPSILON_COUNTS = [0, 1, 2, 3, 5, 8, 12, 18]
    SAMPLES = 3
    REPEATS = 3

    params = {"NUM_STATES": NUM_STATES, "EPSILON_COUNTS": EPSILON_COUNTS,
              "SAMPLES": SAMPLES, "REPEATS": REPEATS, "SEED": 53}

    results = load_cache("eps_test2", params, EPS_SOURCES)
    if results is None:
        results = {name: {"time": [], "mem": [], "dfa_size": [], "ops": []}
                   for name, _, _ in ALGORITHMS}

        for num_eps in EPSILON_COUNTS:
            print(f"  states={NUM_STATES}, ε-transitions={num_eps}")
            nfas = [gen_epsilon_chain(NUM_STATES, num_eps) for _ in range(SAMPLES)]

            for name, alg, _ in ALGORITHMS:
                times, mems, sizes, all_ops = [], [], [], []
                for nfa in nfas:
                    t, m, s, ops = measure(alg, nfa, REPEATS)
                    times.append(t); mems.append(m); sizes.append(s); all_ops.append(ops)

                avg_t = sum(times) / len(times)
                avg_m = sum(mems) / len(mems)
                avg_s = sum(sizes) / len(sizes)
                avg_ops = sum(all_ops) / len(all_ops)

                results[name]["time"].append(avg_t)
                results[name]["mem"].append(avg_m)
                results[name]["dfa_size"].append(avg_s)
                results[name]["ops"].append(avg_ops)

                print(f"    {name:14s}: time={avg_t:.4f}s  mem={avg_m:.1f}KB  "
                      f"DFA≈{avg_s:.0f}  ops≈{avg_ops:.0f}")

        save_cache("eps_test2", params, EPS_SOURCES, results)

    # --- Графіки ---
    metrics = [
        ("time", "Час (с)", "Час", "time", True),
        ("mem", "Пікова RAM (КБ)", "Пам'ять", "memory", True),
        ("dfa_size", "Станів ДСА", "Розмір ДСА", "dfa_size", False),
    ]

    for key, ylabel, title_ua, suffix, use_log in metrics:
        fig, ax = plt.subplots(figsize=(9, 6))
        for name, _, style in ALGORITHMS:
            ax.plot(EPSILON_COUNTS, results[name][key], style, label=name, markersize=6)
        ax.set_xlabel("Кількість ε-переходів")
        ax.set_ylabel(ylabel)
        ax.set_title(f"Тест ε-2: Вплив кількості ε-переходів — {title_ua} (n={NUM_STATES})")
        if use_log:
            ax.set_yscale("log")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend()
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/eps_test2_epsilon_count_{suffix}.png"
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"  Saved: {path}")


# ============================================================
#  Тест 3: Вплив глибини ε-замикання
# ============================================================

def run_test3():
    from Algoritms.class_dfa_nfa import NFA

    NUM_STATES = 20
    CHAIN_DEPTHS = [0, 2, 4, 6, 8, 10, 14]
    SAMPLES = 3
    REPEATS = 3

    params = {"NUM_STATES": NUM_STATES, "CHAIN_DEPTHS": CHAIN_DEPTHS,
              "SAMPLES": SAMPLES, "REPEATS": REPEATS, "SEED": 53}

    def gen_deep_epsilon_chain(num_states, eps_depth):
        state_list = [f"q{i}" for i in range(num_states)]
        states = set(state_list)
        tr = {}
        for i in range(num_states - 1):
            sym = str(i % 2)
            tr[(state_list[i], sym)] = {state_list[i + 1]}
        for i in range(num_states):
            for sym in ("0", "1"):
                if (state_list[i], sym) not in tr:
                    tr[(state_list[i], sym)] = {random.choice(state_list)}
        for i in range(min(eps_depth, num_states - 1)):
            tr.setdefault((state_list[i], ""), set()).add(state_list[i + 1])
        acc = {state_list[-1]}
        if num_states > 3:
            acc.add(state_list[num_states // 2])
        return NFA(states, {"0", "1", ""}, tr, "q0", acc)

    results = load_cache("eps_test3", params, EPS_SOURCES)
    if results is None:
        results = {name: {"time": [], "mem": [], "dfa_size": [], "ops": []}
                   for name, _, _ in ALGORITHMS}

        for depth in CHAIN_DEPTHS:
            print(f"  states={NUM_STATES}, ε-chain depth={depth}")
            nfas = [gen_deep_epsilon_chain(NUM_STATES, depth) for _ in range(SAMPLES)]

            for name, alg, _ in ALGORITHMS:
                times, mems, sizes, all_ops = [], [], [], []
                for nfa in nfas:
                    t, m, s, ops = measure(alg, nfa, REPEATS)
                    times.append(t); mems.append(m); sizes.append(s); all_ops.append(ops)

                avg_t = sum(times) / len(times)
                avg_m = sum(mems) / len(mems)
                avg_s = sum(sizes) / len(sizes)
                avg_ops = sum(all_ops) / len(all_ops)

                results[name]["time"].append(avg_t)
                results[name]["mem"].append(avg_m)
                results[name]["dfa_size"].append(avg_s)
                results[name]["ops"].append(avg_ops)

                print(f"    {name:14s}: time={avg_t:.4f}s  mem={avg_m:.1f}KB  "
                      f"DFA≈{avg_s:.0f}  ops≈{avg_ops:.0f}")

        save_cache("eps_test3", params, EPS_SOURCES, results)

    # --- Графіки ---
    metrics = [
        ("time", "Time (s)", "Час виконання", "time"),
        ("mem", "Peak RAM (KB)", "Пам'ять", "memory"),
        ("dfa_size", "DFA states", "Розмір DFA", "dfa_size"),
    ]

    for key, ylabel, title_ua, suffix in metrics:
        fig, ax = plt.subplots(figsize=(9, 6))
        for name, _, style in ALGORITHMS:
            ax.plot(CHAIN_DEPTHS, results[name][key], style, label=name, markersize=6)
        ax.set_xlabel("Глибина ε-ланцюга")
        ax.set_ylabel(ylabel)
        ax.set_title(f"Тест ε-3: Глибина ε-замикання — {title_ua} (n={NUM_STATES})")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend()
        plt.tight_layout()
        path = f"{OUTPUT_DIR}/eps_test3_closure_depth_{suffix}.png"
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"  Saved: {path}")


# ============================================================
#  Тест 4: Порівняння з базовими алгоритмами (overhead ε-closure)
# ============================================================

def run_test4():
    from Algoritms.sub_set import determinize_nfa
    from Algoritms.brzozowski import determinize_brz
    from Algoritms.transset import determinize_transset

    BASE_ALGORITHMS = [
        ("Subset",     determinize_nfa),
        ("Brzozowski", determinize_brz),
        ("Transset",   determinize_transset),
    ]

    SIZES = [8, 10, 12, 15, 18, 20, 25]
    SAMPLES = 3
    REPEATS = 3

    params = {"SIZES": SIZES, "SAMPLES": SAMPLES, "REPEATS": REPEATS, "SEED": 53}

    cached = load_cache("eps_test4", params, ALL_SOURCES)
    if cached is not None:
        results_base = cached["base"]
        results_eps = cached["eps"]
    else:
        results_base = {name: [] for name, _ in BASE_ALGORITHMS}
        results_eps = {name: [] for name, _, _ in ALGORITHMS}

        for n in SIZES:
            print(f"  states={n}, ε-transitions=0")
            nfas = [gen_epsilon_chain(n, 0) for _ in range(SAMPLES)]

            for name, alg in BASE_ALGORITHMS:
                times = []
                for nfa in nfas:
                    t, _, _, _ = measure(alg, nfa, REPEATS)
                    times.append(t)
                avg_t = sum(times) / len(times)
                results_base[name].append(avg_t)
                print(f"    {name:14s}: time={avg_t:.6f}s")

            for name, alg, _ in ALGORITHMS:
                times = []
                for nfa in nfas:
                    t, _, _, _ = measure(alg, nfa, REPEATS)
                    times.append(t)
                avg_t = sum(times) / len(times)
                results_eps[name].append(avg_t)
                print(f"    {name:14s}: time={avg_t:.6f}s")

        save_cache("eps_test4", params, ALL_SOURCES, {"base": results_base, "eps": results_eps})

    # --- Графіки ---
    SIZES = [8, 10, 12, 15, 18, 20, 25]

    colors_base = ["#e74c3c", "#9b59b6", "#3498db"]
    colors_eps = ["#c0392b", "#8e44ad", "#2980b9"]

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_title("Тест ε-4: Абсолютний час (базові vs ε-варіанти, ε=0)")
    for idx, (name, _) in enumerate([("Subset", None), ("Brzozowski", None),
                                      ("Transset", None)]):
        ax.plot(SIZES, results_base[name], "o-", label=name,
                color=colors_base[idx], markersize=6)
    for idx, (name, _, _) in enumerate(ALGORITHMS):
        ax.plot(SIZES, results_eps[name], "s--", label=name,
                color=colors_eps[idx], markersize=6)
    ax.set_xlabel("Кількість станів НКА")
    ax.set_ylabel("Time (s)")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(fontsize=8)
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/eps_test4_time_absolute.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\n  Saved: {path}")

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_title("Тест ε-4: Overhead ε-closure (ratio ε-час / базовий час)")
    alg_pairs = [
        ("Subset", "Subset+ε"),
        ("Brzozowski", "Brzozowski+ε"),
        ("Transset", "Transset+ε"),
    ]
    for idx, (base_name, eps_name) in enumerate(alg_pairs):
        ratios = []
        for i in range(len(SIZES)):
            base_t = results_base[base_name][i]
            eps_t = results_eps[eps_name][i]
            ratio = eps_t / base_t if base_t > 0 else 1.0
            ratios.append(ratio)
        ax.plot(SIZES, ratios, "o-", label=f"{eps_name} / {base_name}",
                color=colors_base[idx], markersize=6)
    ax.axhline(y=1.0, color="k", linestyle="--", alpha=0.3, label="ratio = 1.0")
    ax.set_xlabel("Кількість станів НКА")
    ax.set_ylabel("Ratio (ε-час / базовий час)")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(fontsize=8)
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/eps_test4_time_ratio.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# ============================================================
#  Тест 5: Коректність ε-алгоритмів (не кешується)
# ============================================================

def run_test5():
    NUM_WORDS = 200

    def _eps_closure(states, transitions):
        closure = set(states)
        stack = list(states)
        while stack:
            s = stack.pop()
            for t in transitions.get((s, ""), set()):
                if t not in closure:
                    closure.add(t)
                    stack.append(t)
        return closure

    def run_nfa(nfa, word):
        current = _eps_closure({nfa.start_state}, nfa.transitions)
        for ch in word:
            nxt = set()
            for s in current:
                nxt |= nfa.transitions.get((s, ch), set())
            current = _eps_closure(nxt, nfa.transitions)
            if not current:
                return False
        return bool(current & nfa.accept_states)

    def run_dfa(dfa, word):
        state = dfa.start_state
        for ch in word:
            key = (state, ch)
            if key not in dfa.transitions:
                return False
            state = dfa.transitions[key]
        return state in dfa.accept_states

    test_cases = [
        ("ε-chain(8, ε=2)",    gen_epsilon_chain(8, 2)),
        ("ε-chain(10, ε=3)",   gen_epsilon_chain(10, 3)),
        ("ε-chain(10, ε=6)",   gen_epsilon_chain(10, 6)),
        ("ε-chain(12, ε=4)",   gen_epsilon_chain(12, 4)),
        ("ε-chain(15, ε=5)",   gen_epsilon_chain(15, 5)),
        ("ε-chain(15, ε=10)",  gen_epsilon_chain(15, 10)),
        ("ε-chain(20, ε=3)",   gen_epsilon_chain(20, 3)),
        ("ε-chain(20, ε=8)",   gen_epsilon_chain(20, 8)),
        ("ε-chain(20, ε=15)",  gen_epsilon_chain(20, 15)),
        ("ε-chain(25, ε=10)",  gen_epsilon_chain(25, 10)),
    ]

    total_errors = 0
    all_sizes = []
    all_nfa_sizes = []
    test_labels = []

    for label, nfa in test_cases:
        alpha_list = sorted(a for a in nfa.alphabet if a != "")
        words = []
        for _ in range(NUM_WORDS):
            length = random.randint(0, 15)
            word = "".join(random.choice(alpha_list) for _ in range(length))
            words.append(word)

        dfas = {}
        sizes = {}
        for name, alg, _ in ALGORITHMS:
            dfa, _ = alg(nfa)
            dfas[name] = dfa
            sizes[name] = len(dfa.states)

        errors = 0
        for word in words:
            nfa_result = run_nfa(nfa, word)
            for name, dfa in dfas.items():
                dfa_result = run_dfa(dfa, word)
                if dfa_result != nfa_result:
                    print(f"    MISMATCH: {label} / {name} / word='{word}': "
                          f"NFA={nfa_result}, DFA={dfa_result}")
                    errors += 1

            results_set = {name: run_dfa(dfas[name], word) for name in dfas}
            if len(set(results_set.values())) > 1:
                print(f"    DISAGREEMENT: {label} / word='{word}': {results_set}")
                errors += 1

        total_errors += errors
        nfa_size = len(nfa.states)
        all_sizes.append(sizes)
        all_nfa_sizes.append(nfa_size)
        test_labels.append(label)

        status = "OK" if errors == 0 else f"FAIL ({errors} errors)"
        size_str = "  ".join(f"{n}={s:4d}" for n, s in sizes.items())
        print(f"  {label:25s}: NFA={nfa_size:3d}  {size_str}  [{status}]")

    print(f"\n  {'='*50}")
    if total_errors == 0:
        print("  ALL ε-TESTS PASSED: всі ε-алгоритми дають еквівалентні ДКА")
    else:
        print(f"  FAILED: {total_errors} помилок знайдено!")
    print(f"  {'='*50}")

    # --- Графіки ---
    if not test_labels:
        return

    x = range(len(test_labels))

    fig, ax = plt.subplots(figsize=(10, 7))
    blowups = [
        all_sizes[i].get("Subset+ε", all_nfa_sizes[i]) / all_nfa_sizes[i]
        if all_nfa_sizes[i] > 0 else 1
        for i in range(len(test_labels))
    ]
    ax.bar(x, blowups, color="steelblue", alpha=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(test_labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Blowup ratio (DFA / NFA states)")
    ax.set_title("Тест ε-5: State Blowup Ratio (ε-алгоритми)")
    ax.axhline(y=1, color="k", linestyle="--", alpha=0.3)
    ax.grid(True, linestyle="--", alpha=0.3, axis="y")
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/eps_test5_blowup.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\n  Saved: {path}")

    fig, ax = plt.subplots(figsize=(10, 7))
    other_algs = [n for n, _, _ in ALGORITHMS if n != "Subset+ε"]
    n_algs = len(other_algs)
    width = 0.8 / n_algs
    colors = ["coral", "mediumseagreen", "mediumpurple"]

    for idx, name in enumerate(other_algs):
        compressions = []
        for i in range(len(test_labels)):
            subset_s = all_sizes[i].get("Subset+ε", 1)
            alg_s = all_sizes[i].get(name, subset_s)
            compressions.append(alg_s / subset_s if subset_s > 0 else 1)
        offset = (idx - n_algs / 2 + 0.5) * width
        ax.bar([j + offset for j in x], compressions, width,
               label=f"{name} / Subset+ε", color=colors[idx % len(colors)], alpha=0.8)

    ax.set_xticks(list(x))
    ax.set_xticklabels(test_labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Compression ratio (D_alg / D_subset)")
    ax.set_title("Тест ε-5: Compression Ratios vs Subset+ε")
    ax.axhline(y=1, color="k", linestyle="--", alpha=0.3)
    ax.grid(True, linestyle="--", alpha=0.3, axis="y")
    ax.legend(fontsize=8)
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/eps_test5_compression.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


# ============================================================
#  Головний запуск
# ============================================================

TESTS = {
    "1": ("Масштабування ε-ланцюга (розмір НКА)",     run_test1),
    "2": ("Вплив кількості ε-переходів",               run_test2),
    "3": ("Глибина ε-замикання",                        run_test3),
    "4": ("Overhead ε-closure vs базові алгоритми",     run_test4),
    "5": ("Коректність ε-алгоритмів",                   run_test5),
}


def main():
    random.seed(53)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    selected = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not selected:
        selected = list(TESTS.keys())

    print("=" * 60)
    print("  Тести детермінізації: алгоритми з ε-замиканнями")
    print("=" * 60)

    for key in selected:
        if key not in TESTS:
            print(f"  Невідомий тест: {key}. Доступні: {', '.join(TESTS.keys())}")
            continue

        title, func = TESTS[key]
        print(f"\n{'='*60}")
        print(f"  Тест ε-{key}: {title}")
        print(f"{'='*60}\n")
        func()

    print(f"\n{'='*60}")
    print(f"  Усі графіки збережено в: {OUTPUT_DIR}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

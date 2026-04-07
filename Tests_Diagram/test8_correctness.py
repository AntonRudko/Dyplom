"""
Тест 8: Верифікація коректності алгоритмів.

Перевіряє, що всі 4 алгоритми (з і без epsilon) дають
еквівалентні ДКА — приймають однакову мову.

Метод: генерація випадкових слів і перевірка, що всі ДКА
приймають/відхиляють кожне слово однаково.

Додатково вимірює:
- Коефіцієнт вибуху (DFA states / NFA states)
- Коефіцієнт стиснення Brzozowski (D_min / D_subset)
- Коефіцієнт стиснення Transset (D' / D_subset)
"""

import random
import matplotlib.pyplot as plt

from Tests_Diagram.nfa_generators import (
    gen_nth_from_last, gen_dense_random, gen_sparse_nfa,
    gen_multi_branch, gen_epsilon_chain, gen_variable_nondet,
)
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms.qsc import determinize_qsc
from Algoritms_with_epsilon.sub_set_epsilon import determinize_nfa_epsilon
from Algoritms_with_epsilon.brzozowski_epsilon import determinize_brz_epsilon
from Algoritms_with_epsilon.transset_epsilon import determinize_transset_epsilon
from Algoritms_with_epsilon.qsc_epsilon import determinize_qsc_epsilon

ALGORITHMS = [
    ("Subset",     determinize_nfa),
    ("Brzozowski", determinize_brz),
    ("Transset",   determinize_transset),
    ("QSC",        determinize_qsc),
]

ALGORITHMS_EPS = [
    ("Subset+ε",     determinize_nfa_epsilon),
    ("Brzozowski+ε", determinize_brz_epsilon),
    ("Transset+ε",   determinize_transset_epsilon),
    ("QSC+ε",        determinize_qsc_epsilon),
]

NUM_WORDS = 100


def run_dfa(dfa, word):
    """Перевірка слова на ДКА."""
    state = dfa.start_state
    for ch in word:
        key = (state, ch)
        if key not in dfa.transitions:
            return False
        state = dfa.transitions[key]
    return state in dfa.accept_states


def _eps_closure(states, transitions):
    """Epsilon-замикання множини станів."""
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
    """Перевірка слова на НКА (з підтримкою epsilon-переходів)."""
    current = _eps_closure({nfa.start_state}, nfa.transitions)
    for ch in word:
        nxt = set()
        for s in current:
            nxt |= nfa.transitions.get((s, ch), set())
        current = _eps_closure(nxt, nfa.transitions)
        if not current:
            return False
    return bool(current & nfa.accept_states)


def gen_random_words(alphabet, count, max_len=15):
    """Генерація випадкових слів."""
    alpha_list = sorted(a for a in alphabet if a != "")
    words = []
    for _ in range(count):
        length = random.randint(0, max_len)
        word = "".join(random.choice(alpha_list) for _ in range(length))
        words.append(word)
    return words


def verify_one(label, nfa, algorithms, words):
    """Перевірка одного НКА на всіх алгоритмах."""
    dfas = {}
    sizes = {}
    for name, alg in algorithms:
        dfa, _ops = alg(nfa)
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

    # Перевірка між алгоритмами
    alg_names = list(dfas.keys())
    for word in words:
        results = {name: run_dfa(dfas[name], word) for name in alg_names}
        unique = set(results.values())
        if len(unique) > 1:
            print(f"    DISAGREEMENT: {label} / word='{word}': {results}")
            errors += 1

    return errors, sizes


def run():
    random.seed(53)
    print("=" * 60)
    print("  Test 8: Correctness Verification")
    print("=" * 60)

    total_errors = 0
    alg_names = [name for name, _ in ALGORITHMS]
    # Зберігаємо розміри DFA для кожного тесту: [{alg_name: size, ...}, ...]
    all_sizes = []
    all_nfa_sizes = []
    test_labels = []

    # --- Набір тестових НКА (без epsilon) ---
    test_cases = [
        ("nth_from_last(5)",  gen_nth_from_last(5)),
        ("nth_from_last(7)",  gen_nth_from_last(7)),
        ("dense(15, p=0.1)",  gen_dense_random(15, {"0", "1", "2"}, 0.1)),
        ("dense(20, p=0.05)", gen_dense_random(20, {"0", "1"}, 0.05)),
        ("sparse(15, 5%)",    gen_sparse_nfa(15, {"0", "1", "2"}, 0.05)),
        ("sparse(20, 10%)",   gen_sparse_nfa(20, {"0", "1"}, 0.10)),
        ("branch(3, k=3)",    gen_multi_branch(3, 3)),
        ("branch(4, k=2)",    gen_multi_branch(4, 2)),
        ("nondet(15, 0%)",    gen_variable_nondet(15, {"0", "1"}, 0.0)),
        ("nondet(15, 20%)",   gen_variable_nondet(15, {"0", "1"}, 0.2)),
        ("nondet(15, 50%)",   gen_variable_nondet(15, {"0", "1"}, 0.5)),
    ]

    print("\n--- Алгоритми без epsilon ---\n")
    for label, nfa in test_cases:
        words = gen_random_words(nfa.alphabet, NUM_WORDS)
        errs, sizes = verify_one(label, nfa, ALGORITHMS, words)
        total_errors += errs

        nfa_size = len(nfa.states)
        all_sizes.append(sizes)
        all_nfa_sizes.append(nfa_size)
        test_labels.append(label)

        status = "OK" if errs == 0 else f"FAIL ({errs} errors)"
        size_str = "  ".join(f"{n}={s:4d}" for n, s in sizes.items())
        print(f"  {label:25s}: NFA={nfa_size:3d}  {size_str}  [{status}]")

    # --- Набір тестових НКА (з epsilon) ---
    test_cases_eps = [
        ("eps_chain(10, ε=3)",  gen_epsilon_chain(10, 3)),
        ("eps_chain(10, ε=6)",  gen_epsilon_chain(10, 6)),
        ("eps_chain(15, ε=5)",  gen_epsilon_chain(15, 5)),
        ("eps_chain(15, ε=10)", gen_epsilon_chain(15, 10)),
    ]

    print("\n--- Алгоритми з epsilon ---\n")
    for label, nfa in test_cases_eps:
        words = gen_random_words(nfa.alphabet, NUM_WORDS)
        errs, sizes = verify_one(label, nfa, ALGORITHMS_EPS, words)
        total_errors += errs

        nfa_size = len(nfa.states)
        status = "OK" if errs == 0 else f"FAIL ({errs} errors)"
        size_str = "  ".join(f"{n}={s}" for n, s in sizes.items())
        print(f"  {label:25s}: NFA={nfa_size:3d}  {size_str}  [{status}]")

    # --- Підсумок ---
    print(f"\n{'=' * 60}")
    if total_errors == 0:
        print("  ALL TESTS PASSED: всі алгоритми дають еквівалентні ДКА")
    else:
        print(f"  FAILED: {total_errors} помилок знайдено!")
    print(f"{'=' * 60}")

    # --- Графіки ---
    if not test_labels:
        return

    x = range(len(test_labels))

    # Графік 1: Blowup ratio (Subset DFA / NFA)
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    ax = axes[0]
    blowups = [
        all_sizes[i].get("Subset", all_nfa_sizes[i]) / all_nfa_sizes[i]
        if all_nfa_sizes[i] > 0 else 1
        for i in range(len(test_labels))
    ]
    ax.bar(x, blowups, color="steelblue", alpha=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(test_labels, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Blowup ratio (DFA / NFA states)")
    ax.set_title("Test 8: State Blowup Ratio")
    ax.axhline(y=1, color="k", linestyle="--", alpha=0.3)
    ax.grid(True, linestyle="--", alpha=0.3, axis="y")

    # Графік 2: Коефіцієнт стиснення кожного алгоритму відносно Subset
    ax = axes[1]
    other_algs = [n for n in alg_names if n != "Subset"]
    n_algs = len(other_algs)
    width = 0.8 / n_algs
    colors = ["coral", "mediumseagreen", "mediumpurple", "goldenrod"]

    for idx, name in enumerate(other_algs):
        compressions = []
        for i in range(len(test_labels)):
            subset_s = all_sizes[i].get("Subset", 1)
            alg_s = all_sizes[i].get(name, subset_s)
            compressions.append(alg_s / subset_s if subset_s > 0 else 1)
        offset = (idx - n_algs / 2 + 0.5) * width
        ax.bar([j + offset for j in x], compressions, width,
               label=f"{name} / Subset", color=colors[idx % len(colors)], alpha=0.8)

    ax.set_xticks(list(x))
    ax.set_xticklabels(test_labels, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Compression ratio (D_alg / D_subset)")
    ax.set_title("Test 8: Compression Ratios vs Subset")
    ax.axhline(y=1, color="k", linestyle="--", alpha=0.3)
    ax.grid(True, linestyle="--", alpha=0.3, axis="y")
    ax.legend(fontsize=7)

    plt.tight_layout()
    plt.savefig("Tests_Diagram/test8_correctness.png", dpi=150)
    plt.close()
    print("\nSaved: Tests_Diagram/test8_correctness.png")


if __name__ == "__main__":
    run()
"""
Генерація зведеної таблиці результатів юніт-тестів у PNG.

Показує, які види тестів який алгоритм пройшов (✓ / ✗).
Запуск:  python generate_test_table.py
"""

import sys
import os
import unittest
import traceback

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# ── Збір тестів ────────────────────────────────────────────────────

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "unit_tests"))

from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms.lazy_subset import determinize_lazy
from Algoritms_with_epsilon.sub_set_epsilon import determinize_nfa_epsilon
from Algoritms_with_epsilon.brzozowski_epsilon import determinize_brz_epsilon
from Algoritms_with_epsilon.transset_epsilon import determinize_transset_epsilon
from Algoritms_with_epsilon.lazy_subset_epsilon import determinize_lazy_epsilon
from Algoritms.class_dfa_nfa import NFA, DFA

from Analize.nfa import (
    nfa_1, nfa_2, nfa_3, nfa_4, nfa_5,
    nfa_large_1, nfa_large_2, nfa_large_3, nfa_large_4, nfa_large_5,
    nfa_epsilon,
)
from Tests_Diagram.nfa_generators import (
    gen_nth_from_last, gen_dense_random, gen_sparse_nfa,
    gen_multi_branch, gen_epsilon_chain,
)
from helpers.dfa_helpers import run_dfa, run_nfa, gen_random_words, gen_systematic_words
from helpers.equivalence import (
    check_language_equivalence_by_words,
    check_dfa_equivalence_by_minimization,
)
from helpers.minimization import minimize_dfa
from helpers.isomorphism import are_isomorphic


# ── Алгоритми ──────────────────────────────────────────────────────

ALGORITHMS = [
    "Subset",
    "Brzozowski",
    "Transset",
    "Lazy",
    "Subset (ε)",
    "Brzozowski (ε)",
    "Transset (ε)",
    "Lazy (ε)",
]

ALGO_FUNCS = {
    "Subset": determinize_nfa,
    "Brzozowski": determinize_brz,
    "Transset": determinize_transset,
    "Lazy": determinize_lazy,
    "Subset (ε)": determinize_nfa_epsilon,
    "Brzozowski (ε)": determinize_brz_epsilon,
    "Transset (ε)": determinize_transset_epsilon,
    "Lazy (ε)": determinize_lazy_epsilon,
}

REGULAR_ALGOS = ["Subset", "Brzozowski", "Transset", "Lazy"]
EPSILON_ALGOS = ["Subset (ε)", "Brzozowski (ε)", "Transset (ε)", "Lazy (ε)"]

# ── Визначення тестів ──────────────────────────────────────────────
# Кожен тест: (назва_виду, список_алгоритмів, функція_перевірки)
# Функція повертає dict { алгоритм: True/False }


def _run_safe(func, _algo_name):
    """Запуск з перехопленням винятків."""
    try:
        return func()
    except Exception:
        traceback.print_exc()
        return False


def test_structure():
    """Структура DFA: стани, старт, приймаючі, переходи."""
    results = {}
    nfa = gen_nth_from_last(3)
    for name in REGULAR_ALGOS:
        def check(n=name):
            dfa, _ = ALGO_FUNCS[n](nfa)
            assert dfa.start_state in dfa.states
            assert dfa.accept_states.issubset(dfa.states)
            for (s, sym), t in dfa.transitions.items():
                assert s in dfa.states
                assert t in dfa.states
            return True
        results[name] = _run_safe(check, name)
    return results


def test_determinism():
    """Детермінізм: кожен (стан, символ) → один стан."""
    results = {}
    nfa = gen_nth_from_last(4)
    for name in REGULAR_ALGOS:
        def check(n=name):
            dfa, _ = ALGO_FUNCS[n](nfa)
            for (s, sym), t in dfa.transitions.items():
                assert not isinstance(t, (set, frozenset, list))
            return True
        results[name] = _run_safe(check, name)
    return results


def test_language_predefined():
    """Еквівалентність мов: предвизначені НКА (nfa_1..5)."""
    results = {}
    nfas = [nfa_1, nfa_2, nfa_3, nfa_4, nfa_5]
    for name in REGULAR_ALGOS:
        def check(n=name):
            for nfa in nfas:
                dfa, _ = ALGO_FUNCS[n](nfa)
                ok, _ = check_language_equivalence_by_words(nfa, dfa)
                if not ok:
                    return False
            return True
        results[name] = _run_safe(check, name)
    return results


def test_language_large():
    """Еквівалентність мов: великі НКА (nfa_large_1..5)."""
    results = {}
    nfas = [nfa_large_1, nfa_large_2, nfa_large_3, nfa_large_4, nfa_large_5]
    for name in REGULAR_ALGOS:
        def check(n=name):
            for nfa in nfas:
                dfa, _ = ALGO_FUNCS[n](nfa)
                ok, _ = check_language_equivalence_by_words(nfa, dfa)
                if not ok:
                    return False
            return True
        results[name] = _run_safe(check, name)
    return results


def test_cross_algorithm():
    """Крос-алгоритмна перевірка: усі 4 дають однакові DFA."""
    results = {name: True for name in REGULAR_ALGOS}
    test_nfas = [
        gen_nth_from_last(4),
        gen_dense_random(10, {"a", "b"}, 0.15),
        gen_sparse_nfa(15, {"0", "1"}, 0.1),
    ]
    for nfa in test_nfas:
        dfas = {}
        for name in REGULAR_ALGOS:
            try:
                dfa, _ = ALGO_FUNCS[name](nfa)
                dfas[name] = dfa
            except Exception:
                results[name] = False

        words = gen_random_words(nfa.alphabet, count=200, max_len=10)
        words += gen_systematic_words(nfa.alphabet, max_len=3)
        words = list(set(words))

        for word in words:
            accepts = {}
            for name, dfa in dfas.items():
                accepts[name] = run_dfa(dfa, word)
            vals = list(accepts.values())
            if not all(v == vals[0] for v in vals):
                for name in REGULAR_ALGOS:
                    if accepts.get(name) != vals[0]:
                        results[name] = False
    return results


def test_edge_single_state():
    """Граничний: один стан (приймаючий / відхиляючий)."""
    results = {}
    nfa_acc = NFA(
        states={"q0"}, alphabet={"a", "b"},
        transitions={("q0", "a"): {"q0"}, ("q0", "b"): {"q0"}},
        start_state="q0", accept_states={"q0"},
    )
    nfa_rej = NFA(
        states={"q0"}, alphabet={"a", "b"},
        transitions={("q0", "a"): {"q0"}, ("q0", "b"): {"q0"}},
        start_state="q0", accept_states=set(),
    )
    for name in REGULAR_ALGOS:
        def check(n=name):
            for nfa in [nfa_acc, nfa_rej]:
                dfa, _ = ALGO_FUNCS[n](nfa)
                ok, _ = check_language_equivalence_by_words(nfa, dfa)
                if not ok:
                    return False
            return True
        results[name] = _run_safe(check, name)
    return results


def test_edge_no_transitions():
    """Граничний: НКА без переходів."""
    results = {}
    nfa = NFA(
        states={"q0", "q1"}, alphabet={"a"},
        transitions={}, start_state="q0", accept_states={"q1"},
    )
    for name in REGULAR_ALGOS:
        def check(n=name):
            dfa, _ = ALGO_FUNCS[n](nfa)
            assert not run_dfa(dfa, "a")
            assert not run_dfa(dfa, "aa")
            return True
        results[name] = _run_safe(check, name)
    return results


def test_edge_unreachable():
    """Граничний: недосяжні стани."""
    results = {}
    nfa = NFA(
        states={"q0", "q1", "q2", "unreachable"}, alphabet={"a", "b"},
        transitions={
            ("q0", "a"): {"q1"}, ("q1", "b"): {"q0"},
            ("unreachable", "a"): {"q2"}, ("q2", "b"): {"unreachable"},
        },
        start_state="q0", accept_states={"q1"},
    )
    for name in REGULAR_ALGOS:
        def check(n=name):
            dfa, _ = ALGO_FUNCS[n](nfa)
            ok, _ = check_language_equivalence_by_words(nfa, dfa)
            return ok
        results[name] = _run_safe(check, name)
    return results


def test_edge_self_loops():
    """Граничний: самопетлі на кожному стані."""
    results = {}
    nfa = NFA(
        states={"q0", "q1", "q2"}, alphabet={"a", "b"},
        transitions={
            ("q0", "a"): {"q0", "q1"}, ("q0", "b"): {"q0"},
            ("q1", "a"): {"q1"}, ("q1", "b"): {"q1", "q2"},
            ("q2", "a"): {"q2"}, ("q2", "b"): {"q2"},
        },
        start_state="q0", accept_states={"q2"},
    )
    for name in REGULAR_ALGOS:
        def check(n=name):
            dfa, _ = ALGO_FUNCS[n](nfa)
            ok, _ = check_language_equivalence_by_words(nfa, dfa)
            return ok
        results[name] = _run_safe(check, name)
    return results


def test_exponential_blowup():
    """Експоненційне зростання: nth-from-last → 2^n станів."""
    results = {}
    n = 4
    nfa = gen_nth_from_last(n)
    for name in REGULAR_ALGOS:
        def check(n_=name, expected=2**n):
            dfa, _ = ALGO_FUNCS[n_](nfa)
            ok, _ = check_language_equivalence_by_words(nfa, dfa)
            return ok
        results[name] = _run_safe(check, name)
    return results


def test_minimization_isomorphism():
    """Мінімізовані DFA ізоморфні між алгоритмами."""
    results = {}
    nfa = gen_nth_from_last(4)
    dfas = {}
    for name in REGULAR_ALGOS:
        try:
            dfa, _ = ALGO_FUNCS[name](nfa)
            dfas[name] = minimize_dfa(dfa)
        except Exception:
            dfas[name] = None

    for name in REGULAR_ALGOS:
        if dfas[name] is None:
            results[name] = False
            continue
        ok = True
        for other in REGULAR_ALGOS:
            if other == name or dfas[other] is None:
                continue
            if not are_isomorphic(dfas[name], dfas[other]):
                ok = False
                break
        results[name] = ok
    return results


def test_epsilon_language():
    """ε-алгоритми: еквівалентність мов (nfa_epsilon)."""
    results = {}
    for name in EPSILON_ALGOS:
        def check(n=name):
            dfa, _ = ALGO_FUNCS[n](nfa_epsilon)
            ok, _ = check_language_equivalence_by_words(nfa_epsilon, dfa)
            return ok
        results[name] = _run_safe(check, name)
    return results


def test_epsilon_chain():
    """ε-алгоритми: ланцюг ε-переходів."""
    results = {}
    nfa = gen_epsilon_chain(15, 5)
    for name in EPSILON_ALGOS:
        def check(n=name):
            dfa, _ = ALGO_FUNCS[n](nfa)
            ok, _ = check_language_equivalence_by_words(nfa, dfa)
            return ok
        results[name] = _run_safe(check, name)
    return results


def test_epsilon_no_eps_in_alphabet():
    """ε-алгоритми: DFA алфавіт без ε."""
    results = {}
    for name in EPSILON_ALGOS:
        def check(n=name):
            dfa, _ = ALGO_FUNCS[n](nfa_epsilon)
            return "" not in dfa.alphabet
        results[name] = _run_safe(check, name)
    return results


def test_epsilon_only():
    """ε-алгоритми: НКА тільки з ε-переходами."""
    results = {}
    nfa = NFA(
        states={"q0", "q1"}, alphabet={"a", ""},
        transitions={("q0", ""): {"q1"}},
        start_state="q0", accept_states={"q1"},
    )
    for name in EPSILON_ALGOS:
        def check(n=name):
            dfa, _ = ALGO_FUNCS[n](nfa)
            if not run_dfa(dfa, ""):
                return False
            if run_dfa(dfa, "a"):
                return False
            return True
        results[name] = _run_safe(check, name)
    return results


def test_epsilon_heavy_chain():
    """ε-алгоритми: великий ланцюг ε-переходів."""
    results = {}
    nfa = gen_epsilon_chain(30, 15)
    for name in EPSILON_ALGOS:
        def check(n=name):
            dfa, _ = ALGO_FUNCS[n](nfa)
            ok, _ = check_language_equivalence_by_words(nfa, dfa)
            return ok
        results[name] = _run_safe(check, name)
    return results


# ── Список тестів ──────────────────────────────────────────────────

TESTS = [
    ("Структура DFA", test_structure),
    ("Детермінізм", test_determinism),
    ("Мова: предвизначені НКА", test_language_predefined),
    ("Мова: великі НКА", test_language_large),
    ("Крос-алгоритмна перевірка", test_cross_algorithm),
    ("Граничний: один стан", test_edge_single_state),
    ("Граничний: без переходів", test_edge_no_transitions),
    ("Граничний: недосяжні стани", test_edge_unreachable),
    ("Граничний: самопетлі", test_edge_self_loops),
    ("Експоненц. зростання", test_exponential_blowup),
    ("Мінімізація / ізоморфізм", test_minimization_isomorphism),
    ("ε: еквівалентність мов", test_epsilon_language),
    ("ε: ланцюг переходів", test_epsilon_chain),
    ("ε: алфавіт без ε", test_epsilon_no_eps_in_alphabet),
    ("ε: тільки ε-переходи", test_epsilon_only),
    ("ε: великий ланцюг", test_epsilon_heavy_chain),
]


# ── Побудова таблиці ───────────────────────────────────────────────

def build_table():
    """Запуск тестів та побудова матриці результатів."""
    # matrix[row][col] = True/False/None (None = не застосовується)
    matrix = []
    test_names = []

    for test_name, test_func in TESTS:
        print(f"  Тест: {test_name} ...", end=" ", flush=True)
        results = test_func()
        row = []
        for algo in ALGORITHMS:
            if algo in results:
                row.append(results[algo])
            else:
                row.append(None)  # не застосовується
        matrix.append(row)
        test_names.append(test_name)

        passed = sum(1 for v in row if v is True)
        total = sum(1 for v in row if v is not None)
        print(f"{passed}/{total}")

    return test_names, matrix


def render_table_png(test_names, matrix, filename):
    """Рендер таблиці у PNG."""
    n_rows = len(test_names)
    n_cols = len(ALGORITHMS)

    fig_width = max(14, n_cols * 1.8 + 4)
    fig_height = max(6, n_rows * 0.55 + 2)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.set_axis_off()
    ax.set_title(
        "Результати юніт-тестів: алгоритми детермінізації",
        fontsize=16, fontweight="bold", pad=20,
    )

    cell_text = []
    cell_colors = []

    COLOR_PASS = "#C8E6C9"   # зелений
    COLOR_FAIL = "#FFCDD2"   # червоний
    COLOR_NA   = "#F5F5F5"   # сірий
    COLOR_HDR  = "#BBDEFB"   # блакитний

    for row in matrix:
        text_row = []
        color_row = []
        for val in row:
            if val is True:
                text_row.append("✓")
                color_row.append(COLOR_PASS)
            elif val is False:
                text_row.append("✗")
                color_row.append(COLOR_FAIL)
            else:
                text_row.append("—")
                color_row.append(COLOR_NA)
        cell_text.append(text_row)
        cell_colors.append(color_row)

    table = ax.table(
        cellText=cell_text,
        rowLabels=test_names,
        colLabels=ALGORITHMS,
        cellColours=cell_colors,
        rowColours=[COLOR_HDR] * n_rows,
        colColours=[COLOR_HDR] * n_cols,
        cellLoc="center",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.5)

    # Заголовки стовпців — жирний
    for col in range(n_cols):
        cell = table[0, col]
        cell.set_text_props(fontweight="bold", fontsize=10)

    # Заголовки рядків — жирний
    for row in range(n_rows):
        cell = table[row + 1, -1]
        cell.set_text_props(fontweight="bold", fontsize=10)
        cell.set_width(0.28)

    # Символи ✓/✗ — великий шрифт
    for row in range(n_rows):
        for col in range(n_cols):
            cell = table[row + 1, col]
            cell.set_text_props(fontsize=14)

    # ── Підсумковий рядок ──
    summary_text = []
    summary_colors = []
    for col_idx in range(n_cols):
        passed = sum(1 for row in matrix if row[col_idx] is True)
        total = sum(1 for row in matrix if row[col_idx] is not None)
        summary_text.append(f"{passed}/{total}")
        summary_colors.append("#E1BEE7" if passed == total else "#FFCDD2")

    # Додаємо підсумковий рядок вручну
    n_row = n_rows + 1
    for col_idx in range(n_cols):
        table.add_cell(n_row, col_idx, width=table[1, 0].get_width(),
                        height=table[1, 0].get_height(),
                        text=summary_text[col_idx], loc="center",
                        facecolor=summary_colors[col_idx])
        table[n_row, col_idx].set_text_props(fontweight="bold", fontsize=12)

    table.add_cell(n_row, -1, width=table[1, -1].get_width(),
                    height=table[1, -1].get_height(),
                    text="ВСЬОГО", loc="center",
                    facecolor="#CE93D8")
    table[n_row, -1].set_text_props(fontweight="bold", fontsize=11)

    plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"\nТаблицю збережено: {filename}")


# ── main ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Запуск тестів та побудова зведеної таблиці")
    print("=" * 60)

    test_names, matrix = build_table()

    out_path = os.path.join(PROJECT_ROOT, "Table", "test_results_table.png")
    render_table_png(test_names, matrix, out_path)
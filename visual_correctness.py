"""
Візуалізація коректності алгоритмів детермінізації.

Частина 1: Мовна еквівалентність (консольний вивід)
Частина 2: Структурна ізоморфність (графи DFA + таблиця + матриця)

Запуск:
    python visual_correctness.py
"""

import sys
import os
import random
import itertools
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms.lazy_subset import determinize_lazy
from Algoritms_with_epsilon.sub_set_epsilon import determinize_nfa_epsilon
from Algoritms_with_epsilon.brzozowski_epsilon import determinize_brz_epsilon
from Algoritms_with_epsilon.transset_epsilon import determinize_transset_epsilon
from Algoritms_with_epsilon.lazy_subset_epsilon import determinize_lazy_epsilon

from Analize.mocks.nfa import nfa_test1, nfa_epsilon
from Tests_Diagram.nfa_generators import gen_nth_from_last


# ── Допоміжні функції ─────────────────────────────────────────────

def epsilon_closure(states, transitions):
    closure = set(states)
    queue = deque(states)
    while queue:
        s = queue.popleft()
        for target in transitions.get((s, ""), set()):
            if target not in closure:
                closure.add(target)
                queue.append(target)
    return closure


def run_nfa(nfa, word):
    current = epsilon_closure({nfa.start_state}, nfa.transitions)
    for ch in word:
        nxt = set()
        for s in current:
            nxt |= nfa.transitions.get((s, ch), set())
        current = epsilon_closure(nxt, nfa.transitions)
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


def gen_words(alphabet, count=15, max_len=8):
    alpha = sorted(sym for sym in alphabet if sym != "")
    words = [""]
    # Систематичні короткі
    for length in range(1, 4):
        for combo in itertools.product(alpha, repeat=length):
            words.append("".join(combo))
    # Випадкові довші
    for _ in range(count):
        length = random.randint(2, max_len)
        word = "".join(random.choice(alpha) for _ in range(length))
        words.append(word)
    # Без дублікатів, обмежити кількість
    words = list(dict.fromkeys(words))
    return words


# ── Мінімізація DFA (Hopcroft) ────────────────────────────────────

class MinimalDFA:
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states


def minimize_dfa(dfa):
    alphabet = sorted(sym for sym in dfa.alphabet if sym != "")

    # BFS reachable
    reachable = set()
    queue = deque([dfa.start_state])
    reachable.add(dfa.start_state)
    while queue:
        s = queue.popleft()
        for sym in alphabet:
            nxt = dfa.transitions.get((s, sym))
            if nxt is not None and nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)

    states = reachable
    accept = dfa.accept_states & states
    non_accept = states - accept

    DEAD = "__dead__"
    total_tr = {}
    needs_dead = False
    for s in states:
        for sym in alphabet:
            nxt = dfa.transitions.get((s, sym))
            if nxt is not None and nxt in states:
                total_tr[(s, sym)] = nxt
            else:
                total_tr[(s, sym)] = DEAD
                needs_dead = True

    if needs_dead:
        states = states | {DEAD}
        non_accept = non_accept | {DEAD}
        for sym in alphabet:
            total_tr[(DEAD, sym)] = DEAD

    if not accept:
        partition = [states]
    elif not non_accept:
        partition = [accept]
    else:
        partition = [accept, non_accept]

    def get_pid(state, part):
        for i, group in enumerate(part):
            if state in group:
                return i
        return -1

    changed = True
    while changed:
        changed = False
        new_part = []
        for group in partition:
            splits = {}
            for s in group:
                sig = tuple(get_pid(total_tr[(s, sym)], partition) for sym in alphabet)
                splits.setdefault(sig, set()).add(s)
            if len(splits) > 1:
                changed = True
            new_part.extend(splits.values())
        partition = new_part

    state_to_group = {}
    for i, group in enumerate(partition):
        for s in group:
            state_to_group[s] = i

    start_g = state_to_group[dfa.start_state]
    min_states = set()
    min_tr = {}
    min_accept = set()

    for i, group in enumerate(partition):
        rep = next(iter(group))
        min_states.add(i)
        if rep in accept:
            min_accept.add(i)
        for sym in alphabet:
            tg = state_to_group[total_tr[(rep, sym)]]
            min_tr[(i, sym)] = tg

    if needs_dead:
        dead_g = state_to_group[DEAD]
        min_states.discard(dead_g)
        min_accept.discard(dead_g)
        min_tr = {k: v for k, v in min_tr.items() if k[0] != dead_g and v != dead_g}

    return MinimalDFA(min_states, set(alphabet), min_tr, start_g, min_accept)


# ── Ізоморфізм через BFS-бієкцію ─────────────────────────────────

def are_isomorphic(dfa1, dfa2):
    alphabet = sorted(dfa1.alphabet)
    if sorted(dfa2.alphabet) != alphabet:
        return False
    if len(dfa1.states) != len(dfa2.states):
        return False
    if len(dfa1.accept_states) != len(dfa2.accept_states):
        return False

    mapping = {dfa1.start_state: dfa2.start_state}
    reverse = {dfa2.start_state: dfa1.start_state}

    if (dfa1.start_state in dfa1.accept_states) != (dfa2.start_state in dfa2.accept_states):
        return False

    queue = deque([dfa1.start_state])
    while queue:
        s1 = queue.popleft()
        s2 = mapping[s1]
        for sym in alphabet:
            t1 = dfa1.transitions.get((s1, sym))
            t2 = dfa2.transitions.get((s2, sym))
            if (t1 is None) != (t2 is None):
                return False
            if t1 is None:
                continue
            if t1 in mapping:
                if mapping[t1] != t2:
                    return False
            else:
                if t2 in reverse:
                    return False
                if (t1 in dfa1.accept_states) != (t2 in dfa2.accept_states):
                    return False
                mapping[t1] = t2
                reverse[t2] = t1
                queue.append(t1)

    return len(mapping) == len(dfa1.states)


# ── BFS-перейменування станів (0, 1, 2, ...) ─────────────────────

def bfs_rename(dfa):
    alphabet = sorted(dfa.alphabet)
    old_to_new = {}
    counter = 0
    queue = deque([dfa.start_state])
    old_to_new[dfa.start_state] = counter
    counter += 1

    while queue:
        s = queue.popleft()
        for sym in alphabet:
            t = dfa.transitions.get((s, sym))
            if t is not None and t not in old_to_new:
                old_to_new[t] = counter
                counter += 1
                queue.append(t)

    new_states = set(old_to_new.values())
    new_tr = {}
    for (s, sym), t in dfa.transitions.items():
        if s in old_to_new and t in old_to_new:
            new_tr[(old_to_new[s], sym)] = old_to_new[t]
    new_accept = {old_to_new[s] for s in dfa.accept_states if s in old_to_new}
    new_start = old_to_new[dfa.start_state]

    return MinimalDFA(new_states, dfa.alphabet, new_tr, new_start, new_accept)


# ================================================================
#  ЧАСТИНА 1: Мовна еквівалентність (консольний вивід)
# ================================================================

def part1_language_equivalence():
    print("\n" + "=" * 70)
    print("  ЧАСТИНА 1: МОВНА ЕКВІВАЛЕНТНІСТЬ")
    print("=" * 70)

    # --- Базові алгоритми на nfa_1 ---
    algorithms = [
        ("Subset",     determinize_nfa),
        ("Brzozowski", determinize_brz),
        ("Transset",   determinize_transset),
        ("Lazy",       determinize_lazy),
    ]

    words = gen_words(nfa_test1.alphabet, count=20, max_len=14)
    # Обмежуємо до 15 слів для читабельності
    words = words[:15]

    for alg_name, alg_func in algorithms:
        dfa, _ = alg_func(nfa_test1)

        print(f"\n=== Мовна еквівалентність: nfa_1 → {alg_name} ===")
        match_count = 0
        for word in words:
            nfa_res = run_nfa(nfa_test1, word)
            dfa_res = run_dfa(dfa, word)
            match = nfa_res == dfa_res
            if match:
                match_count += 1
            display_word = f'"{word}"' if word else '""'
            print(f'  word: {display_word:12s} -- for NFA: {str(nfa_res):5s}'
                  f'  -- for DFA: {str(dfa_res):5s}'
                  f'  {"✓" if match else "✗ MISMATCH"}')

        equal = match_count == len(words)
        print(f"\n  Automats equal ? {equal}   ({match_count}/{len(words)} words match)")

    # --- Epsilon-алгоритми на nfa_epsilon ---
    eps_algorithms = [
        ("Subset+ε",     determinize_nfa_epsilon),
        ("Brzozowski+ε", determinize_brz_epsilon),
        ("Transset+ε",   determinize_transset_epsilon),
        ("Lazy+ε",       determinize_lazy_epsilon),
    ]

    words_eps = gen_words(nfa_epsilon.alphabet, count=20, max_len=14)
    words_eps = words_eps[:15]

    for alg_name, alg_func in eps_algorithms:
        dfa, _ = alg_func(nfa_epsilon)

        print(f"\n=== Мовна еквівалентність: nfa_epsilon → {alg_name} ===")
        match_count = 0
        for word in words_eps:
            nfa_res = run_nfa(nfa_epsilon, word)
            dfa_res = run_dfa(dfa, word)
            match = nfa_res == dfa_res
            if match:
                match_count += 1
            display_word = f'"{word}"' if word else '""'
            print(f'  word: {display_word:12s} -- for NFA: {str(nfa_res):5s}'
                  f'  -- for DFA: {str(dfa_res):5s}'
                  f'  {"✓" if match else "✗ MISMATCH"}')

        equal = match_count == len(words_eps)
        print(f"\n  Automats equal ? {equal}   ({match_count}/{len(words_eps)} words match)")


# ================================================================
#  ЧАСТИНА 2: Структурна ізоморфність
# ================================================================

def part2_structural_isomorphism():
    print("\n" + "=" * 70)
    print("  ЧАСТИНА 2: СТРУКТУРНА ІЗОМОРФНІСТЬ")
    print("=" * 70)

    OUTPUT_DIR = "Outputs/Visual_Correctness"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    nfa = gen_nth_from_last(3)

    algorithms = [
        ("Subset",     determinize_nfa),
        ("Brzozowski", determinize_brz),
        ("Transset",   determinize_transset),
        ("Lazy",       determinize_lazy),
    ]

    # Детермінізація → мінімізація → BFS-перейменування
    minimized = {}
    raw_dfas = {}
    for name, func in algorithms:
        dfa, _ = func(nfa)
        raw_dfas[name] = dfa
        m = minimize_dfa(dfa)
        minimized[name] = bfs_rename(m)

    alg_names = [name for name, _ in algorithms]

    # ── 2a: Консольний вивід характеристик ────────────────────────
    print(f"\n=== Ізоморфність мінімальних DFA: nth_from_last(3) ===\n")
    print(f"  {'Алгоритм':<14s}  {'Станів':>7s}  {'Переходів':>10s}  "
          f"{'Приймаючих':>11s}  {'Старт':>6s}")
    print(f"  {'-'*14}  {'-'*7}  {'-'*10}  {'-'*11}  {'-'*6}")

    for name in alg_names:
        m = minimized[name]
        n_states = len(m.states)
        n_trans = len(m.transitions)
        n_accept = len(m.accept_states)
        print(f"  {name:<14s}  {n_states:>7d}  {n_trans:>10d}  "
              f"{n_accept:>11d}  {m.start_state:>6}")

    # ── 2b: Попарна ізоморфність (консоль) ────────────────────────
    print()
    iso_matrix = {}
    all_iso = True
    for i in range(len(alg_names)):
        for j in range(i + 1, len(alg_names)):
            n1, n2 = alg_names[i], alg_names[j]
            iso = are_isomorphic(minimized[n1], minimized[n2])
            iso_matrix[(n1, n2)] = iso
            iso_matrix[(n2, n1)] = iso
            if not iso:
                all_iso = False
            print(f"  {n1:<14s} ↔ {n2:<14s} : isomorphic ? {iso}")

    print(f"\n  All minimized DFAs are isomorphic ? {all_iso}")

    # ── 2c: Графи мінімальних DFA (2x2) ──────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle("Мінімізовані DFA: nth_from_last(3)\n"
                 "(всі графи мають бути ідентичні)",
                 fontsize=16, fontweight="bold", y=0.98)

    for idx, name in enumerate(alg_names):
        ax = axes[idx // 2][idx % 2]
        m = minimized[name]
        alphabet = sorted(m.alphabet)

        G = nx.MultiDiGraph()
        for s in m.states:
            G.add_node(s)

        # Групуємо переходи з однаковими src→dst
        edge_labels = {}
        for (s, sym), t in m.transitions.items():
            key = (s, t)
            if key not in edge_labels:
                edge_labels[key] = []
            edge_labels[key].append(sym)

        for (s, t), syms in edge_labels.items():
            G.add_edge(s, t, label=",".join(sorted(syms)))

        # Позиціонування
        pos = nx.spring_layout(G, seed=42, k=2.5)

        # Малювання вузлів
        normal_nodes = [s for s in m.states if s not in m.accept_states]
        accept_nodes = [s for s in m.states if s in m.accept_states]

        nx.draw_networkx_nodes(G, pos, nodelist=normal_nodes, ax=ax,
                               node_color="#AED6F1", node_size=700,
                               edgecolors="black", linewidths=1.5)
        nx.draw_networkx_nodes(G, pos, nodelist=accept_nodes, ax=ax,
                               node_color="#ABEBC6", node_size=700,
                               edgecolors="black", linewidths=3)

        # Стартовий стан — стрілка
        start_pos = pos[m.start_state]
        ax.annotate("", xy=start_pos,
                    xytext=(start_pos[0] - 0.25, start_pos[1] + 0.25),
                    arrowprops=dict(arrowstyle="->", color="red", lw=2.5))

        # Підписи вузлів
        nx.draw_networkx_labels(G, pos, ax=ax,
                                font_size=12, font_weight="bold")

        # Підписи ребер
        edge_label_dict = {}
        for (s, t), syms in edge_labels.items():
            edge_label_dict[(s, t)] = ",".join(sorted(syms))

        nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#555555",
                               arrows=True, arrowstyle="->", arrowsize=20,
                               connectionstyle="arc3,rad=0.15",
                               min_source_margin=15, min_target_margin=15)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_label_dict,
                                     ax=ax, font_size=8, font_color="#333333",
                                     label_pos=0.35)

        n_s = len(m.states)
        n_t = len(m.transitions)
        n_a = len(m.accept_states)
        ax.set_title(f"{name}\nстанів={n_s}, переходів={n_t}, "
                     f"приймаючих={n_a}, старт={m.start_state}",
                     fontsize=12, fontweight="bold")
        ax.axis("off")

    # Легенда
    legend_elements = [
        mpatches.Patch(facecolor="#AED6F1", edgecolor="black", label="Звичайний стан"),
        mpatches.Patch(facecolor="#ABEBC6", edgecolor="black", linewidth=3,
                       label="Приймаючий стан"),
        mpatches.FancyArrowPatch((0, 0), (1, 0), arrowstyle="->", color="red",
                                 label="Стартовий стан"),
    ]
    fig.legend(handles=legend_elements[:2], loc="lower center", ncol=2,
               fontsize=11, frameon=True, fancybox=True)

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    path_graphs = f"{OUTPUT_DIR}/isomorphism_graphs.png"
    plt.savefig(path_graphs, dpi=150, facecolor="white")
    plt.close()
    print(f"\n  Saved: {path_graphs}")

    # ── 2d: Таблиця характеристик (PNG) ──────────────────────────
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_axis_off()
    ax.set_title("Характеристики мінімізованих DFA: nth_from_last(3)",
                 fontsize=14, fontweight="bold", pad=20)

    col_labels = ["Алгоритм", "|Станів|", "|Переходів|", "|Приймаючих|", "Старт"]
    cell_text = []
    for name in alg_names:
        m = minimized[name]
        cell_text.append([
            name,
            str(len(m.states)),
            str(len(m.transitions)),
            str(len(m.accept_states)),
            str(m.start_state),
        ])

    table = ax.table(cellText=cell_text, colLabels=col_labels,
                     cellLoc="center", loc="center",
                     colColours=["#BBDEFB"] * 5)
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.8)

    # Виділити зеленим якщо всі рядки однакові
    for col in range(1, 5):
        values = [cell_text[row][col] for row in range(len(alg_names))]
        all_same = len(set(values)) == 1
        color = "#C8E6C9" if all_same else "#FFCDD2"
        for row in range(len(alg_names)):
            table[row + 1, col].set_facecolor(color)

    plt.tight_layout()
    path_table = f"{OUTPUT_DIR}/isomorphism_table.png"
    plt.savefig(path_table, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Saved: {path_table}")

    # ── 2e: Матриця ізоморфності (PNG) ────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.set_title("Попарна ізоморфність мінімальних DFA\nnth_from_last(3)",
                 fontsize=14, fontweight="bold", pad=15)

    n = len(alg_names)
    cell_text = []
    cell_colors = []

    for i, n1 in enumerate(alg_names):
        row_text = []
        row_colors = []
        for j, n2 in enumerate(alg_names):
            if i == j:
                row_text.append("—")
                row_colors.append("#E3F2FD")
            else:
                iso = iso_matrix.get((n1, n2), False)
                row_text.append("✓" if iso else "✗")
                row_colors.append("#C8E6C9" if iso else "#FFCDD2")
        cell_text.append(row_text)
        cell_colors.append(row_colors)

    table = ax.table(cellText=cell_text,
                     rowLabels=alg_names, colLabels=alg_names,
                     cellColours=cell_colors,
                     cellLoc="center", loc="center",
                     rowColours=["#BBDEFB"] * n,
                     colColours=["#BBDEFB"] * n)
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    table.scale(1, 2)

    for row in range(n):
        table[row + 1, -1].set_text_props(fontweight="bold")
    for col in range(n):
        table[0, col].set_text_props(fontweight="bold")

    ax.axis("off")
    plt.tight_layout()
    path_matrix = f"{OUTPUT_DIR}/isomorphism_matrix.png"
    plt.savefig(path_matrix, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Saved: {path_matrix}")


# ── main ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    random.seed(42)

    part1_language_equivalence()
    part2_structural_isomorphism()

    print("\n" + "=" * 70)
    print("  Готово!")
    print("  Консольний вивід — зробіть скріншот для звіту")
    print("  Графічні файли збережено в Outputs/Visual_Correctness/")
    print("=" * 70)

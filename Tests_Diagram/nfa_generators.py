"""
Генератори спеціальних НКА для бенчмарків детермінізації.

Кожен генератор створює сімейство автоматів з контрольованими
характеристиками, що дозволяє виявити різницю між алгоритмами.
"""

import random
import time
import tracemalloc
from Algoritms.class_dfa_nfa import NFA


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


def gen_nth_from_last(n):
    """
    Класичний worst-case: мова L = (0|1)* 1 (0|1)^{n-1}.

    Приймає рядки над {0,1}, де n-й символ з кінця = '1'.
    НКА: n+1 стан.
    ДКА: рівно 2^n станів (експоненційний вибух).

    Джерело: стандартний приклад з теорії автоматів.
    """
    states = {f"q{i}" for i in range(n + 1)}
    alphabet = {"0", "1"}
    transitions = {}

    # q0 — стартовий стан, зациклений на собі по 0 і 1
    transitions[("q0", "0")] = {"q0"}
    transitions[("q0", "1")] = {"q0", "q1"}  # недетермінований вибір

    # Ланцюг q1 → q2 → ... → qn по обох символах
    for i in range(1, n):
        transitions[(f"q{i}", "0")] = {f"q{i+1}"}
        transitions[(f"q{i}", "1")] = {f"q{i+1}"}

    return NFA(states, alphabet, transitions, "q0", {f"q{n}"})


def gen_dense_random(num_states, alphabet, edge_prob):
    """
    Густий випадковий НКА з гарантією зв'язності та недетермінізму.

    Висока щільність переходів (edge_prob ≥ 0.2) створює багато
    недетермінізму. Brzozowski тут дає мінімальний ДКА,
    Transset може зливати стани з однаковою поведінкою.
    """
    state_list = [f"q{i}" for i in range(num_states)]
    states = set(state_list)
    alpha_list = sorted(alphabet)

    acc = {s for s in states if random.random() < 0.3}
    if not acc:
        acc = {random.choice(state_list[1:])} if num_states > 1 else {"q0"}

    tr = {}

    # Spine для зв'язності
    for i in range(num_states - 1):
        a = random.choice(alpha_list)
        tr.setdefault((state_list[i], a), set()).add(state_list[i + 1])

    # Гарантія недетермінізму
    for i in range(num_states):
        a = random.choice(alpha_list)
        t1, t2 = random.choice(state_list), random.choice(state_list)
        while t2 == t1 and num_states > 1:
            t2 = random.choice(state_list)
        tr.setdefault((state_list[i], a), set()).update({t1, t2})

    # Випадкові ребра з заданою ймовірністю
    for s in states:
        for a in alphabet:
            targets = {q for q in states if random.random() < edge_prob}
            if targets:
                tr.setdefault((s, a), set()).update(targets)

    return NFA(states, alphabet, tr, "q0", acc)


def gen_sparse_nfa(num_states, alphabet, nondet_fraction=0.05):
    """
    Переважно детермінований НКА з мінімальним недетермінізмом.

    Більшість переходів детерміновані (одна ціль).
    Лише nondet_fraction частка переходів має 2+ цілі.

    Quick Subset Construction тут має перевагу — він
    зберігає детерміновану частину без змін.
    """
    state_list = [f"q{i}" for i in range(num_states)]
    states = set(state_list)
    alpha_list = sorted(alphabet)

    acc = {s for s in states if random.random() < 0.25}
    if not acc:
        acc = {random.choice(state_list[1:])} if num_states > 1 else {"q0"}

    tr = {}

    # Spine для зв'язності
    for i in range(num_states - 1):
        a = random.choice(alpha_list)
        tr.setdefault((state_list[i], a), set()).add(state_list[i + 1])

    # Детерміновані переходи для кожного стану/символу
    for s in state_list:
        for a in alpha_list:
            if (s, a) not in tr:
                tr[(s, a)] = {random.choice(state_list)}

    # Додаємо недетермінізм лише до малої частки переходів
    all_keys = list(tr.keys())
    nondet_count = max(1, int(len(all_keys) * nondet_fraction))
    for key in random.sample(all_keys, nondet_count):
        extra = random.choice(state_list)
        tr[key].add(extra)

    return NFA(states, alphabet, tr, "q0", acc)


def gen_variable_alphabet(num_states, alphabet_size, edge_prob=0.08):
    """
    НКА з фіксованим числом станів та змінним розміром алфавіту.

    Більший алфавіт збільшує кількість переходів на стан,
    що впливає на час BFS-кроку кожного алгоритму.
    """
    alphabet = {str(i) for i in range(alphabet_size)}
    state_list = [f"q{i}" for i in range(num_states)]
    states = set(state_list)
    alpha_list = sorted(alphabet)

    acc = {s for s in states if random.random() < 0.25}
    if not acc:
        acc = {random.choice(state_list[1:])} if num_states > 1 else {"q0"}

    tr = {}

    # Spine
    for i in range(num_states - 1):
        a = random.choice(alpha_list)
        tr.setdefault((state_list[i], a), set()).add(state_list[i + 1])

    # Недетермінізм
    for i in range(num_states):
        a = random.choice(alpha_list)
        t1, t2 = random.choice(state_list), random.choice(state_list)
        while t2 == t1 and num_states > 1:
            t2 = random.choice(state_list)
        tr.setdefault((state_list[i], a), set()).update({t1, t2})

    # Випадкові ребра
    for s in states:
        for a in alphabet:
            targets = {q for q in states if random.random() < edge_prob}
            if targets:
                tr.setdefault((s, a), set()).update(targets)

    return NFA(states, alphabet, tr, "q0", acc)


def gen_epsilon_chain(num_states, num_epsilon):
    """
    НКА з epsilon-переходами: ланцюг станів + випадкові ε-зв'язки.

    Базовий ланцюг q0 → q1 → ... → q(n-1) по символах {0, 1}.
    Додатково num_epsilon випадкових ε-переходів, що створюють
    ε-замикання різної глибини.
    """
    state_list = [f"q{i}" for i in range(num_states)]
    states = set(state_list)
    alphabet = {"0", "1", ""}

    tr = {}

    # Детермінований ланцюг
    for i in range(num_states - 1):
        sym = str(i % 2)
        tr[(state_list[i], sym)] = {state_list[i + 1]}

    # Недетермінізм: кожен стан має перехід по обох символах
    for i in range(num_states):
        for sym in ("0", "1"):
            if (state_list[i], sym) not in tr:
                tr[(state_list[i], sym)] = {random.choice(state_list)}

    # Додаємо ε-переходи
    for _ in range(num_epsilon):
        src = random.choice(state_list)
        dst = random.choice(state_list)
        while dst == src and num_states > 1:
            dst = random.choice(state_list)
        tr.setdefault((src, ""), set()).add(dst)

    acc = {state_list[-1]}
    if num_states > 3:
        acc.add(state_list[num_states // 2])

    return NFA(states, alphabet, tr, "q0", acc)


def gen_variable_nondet(num_states, alphabet, nondet_fraction):
    """
    НКА зі змінним ступенем недетермінізму.

    Базовий детермінований автомат, до якого додається
    контрольована частка недетермінованих переходів.
    nondet_fraction: від 0.0 (повністю дет.) до 1.0 (повністю недет.).
    """
    state_list = [f"q{i}" for i in range(num_states)]
    states = set(state_list)
    alpha_list = sorted(alphabet)

    acc = {s for s in states if random.random() < 0.25}
    if not acc:
        acc = {random.choice(state_list[1:])} if num_states > 1 else {"q0"}

    tr = {}

    # Spine
    for i in range(num_states - 1):
        a = random.choice(alpha_list)
        tr.setdefault((state_list[i], a), set()).add(state_list[i + 1])

    # Повністю детерміновані переходи
    for s in state_list:
        for a in alpha_list:
            if (s, a) not in tr:
                tr[(s, a)] = {random.choice(state_list)}

    # Додаємо недетермінізм до вказаної частки
    all_keys = list(tr.keys())
    nondet_count = max(0, int(len(all_keys) * nondet_fraction))
    nondet_count = min(nondet_count, len(all_keys))
    for key in random.sample(all_keys, nondet_count):
        extra = random.choice(state_list)
        tr[key].add(extra)

    return NFA(states, alphabet, tr, "q0", acc)


def gen_multi_branch(n, k=3):
    """
    НКА з k паралельними гілками довжини n.

    Стартовий стан недетерміновано переходить у k гілок.
    Кожна гілка — ланцюг зі своїм алфавітом символів.
    Гілки зливаються у спільний приймальний стан.

    Subset Construction створює O(n^k) станів через декартовий добуток.
    Brzozowski може дати менший DFA завдяки мінімізації.
    Transset зливає гілки з однаковою поведінкою.
    """
    alphabet = {str(i) for i in range(k)}
    states = {"q0", "qf"}
    transitions = {}

    # k гілок з n станів кожна
    for branch in range(k):
        branch_states = [f"b{branch}_q{i}" for i in range(n)]
        states.update(branch_states)

        # q0 → початок кожної гілки по символу branch та "0"
        sym = str(branch)
        transitions.setdefault(("q0", sym), set()).add(branch_states[0])
        # Також додаємо перехід з q0 по "0" для перекриття
        transitions.setdefault(("q0", "0"), set()).add(branch_states[0])

        # Ланцюг всередині гілки
        for i in range(n - 1):
            for s in alphabet:
                transitions[(branch_states[i], s)] = {branch_states[i + 1]}

        # Кінець гілки → qf
        for s in alphabet:
            transitions[(branch_states[-1], s)] = {"qf"}

    # qf — приймальний, з самоциклом
    for s in alphabet:
        transitions[("qf", s)] = {"qf"}

    return NFA(states, alphabet, transitions, "q0", {"qf"})

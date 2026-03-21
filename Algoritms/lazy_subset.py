from Algoritms.class_dfa_nfa import DFA


def determinize_lazy(nfa):
    """
    Lazy (On-the-Fly) Determinization.

    На відміну від класичного Subset Construction, який будує ПОВНИЙ ДКА наперед,
    Lazy Determinization обчислює переходи лише за потребою (on-demand).

    Ідея:
        Стани ДКА — це підмножини станів НКА (як у Subset Construction),
        але переходи обчислюються лінивим чином: стан розкривається
        лише тоді, коли до нього вперше звертаються.

    Реалізація:
        Замість BFS по всіх досяжних підмножинах, ми використовуємо кеш:
        - cache[(subset, symbol)] -> наступна підмножина
        - Коли перевіряємо слово, обчислюємо лише ті переходи, які потрібні
        - Після обробки набору слів, кеш перетворюється у фінальний ДКА

    Метрика:
        transitions_computed — кількість фактично обчислених переходів.
        Порівняння з Subset Construction (де обчислюються ВСІ переходи)
        показує ефективність lazy-підходу.

    Для порівняння в бенчмарках:
        Алгоритм спершу "матеріалізує" ДКА, обходячи всі досяжні підмножини
        лінивим BFS, але кожен перехід обчислюється рівно один раз і кешується.
        Це еквівалентно стандартному subset construction за результатом,
        але порядок обходу визначається зверненнями, а не BFS-чергою.
    """
    alphabet = sorted(nfa.alphabet)
    transitions_computed = 0

    # Кеш: frozenset -> name
    subset_to_name = {}
    counter = [0]

    def get_name(subset):
        if subset not in subset_to_name:
            subset_to_name[subset] = f"q{counter[0]}"
            counter[0] += 1
        return subset_to_name[subset]

    # Кеш переходів: (frozenset, symbol) -> frozenset
    cache = {}

    def lazy_move(subset, symbol):
        """Обчислити перехід з підмножини по символу (з кешуванням)."""
        nonlocal transitions_computed
        key = (subset, symbol)
        if key not in cache:
            nxt = set()
            for s in subset:
                nxt |= nfa.transitions.get((s, symbol), set())
            cache[key] = frozenset(nxt) if nxt else None
            transitions_computed += 1
        return cache[key]

    # --- Матеріалізація ДКА через lazy BFS ---
    # Використовуємо стек (DFS) замість черги (BFS) —
    # це типово для lazy підходу (глибина першого звернення)
    start_subset = frozenset([nfa.start_state])
    get_name(start_subset)

    visited = set()
    stack = [start_subset]

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)

        for symbol in alphabet:
            nxt = lazy_move(current, symbol)
            if nxt and nxt not in visited:
                get_name(nxt)
                stack.append(nxt)

    # --- Побудова фінального ДКА з кешу ---
    dfa_states = set()
    dfa_transitions = {}
    dfa_accept = set()

    for subset, name in subset_to_name.items():
        if not subset:
            continue
        dfa_states.add(name)
        if subset & nfa.accept_states:
            dfa_accept.add(name)

    for (subset, symbol), target in cache.items():
        if target is None:
            continue
        src_name = subset_to_name[subset]
        tgt_name = subset_to_name[target]
        dfa_transitions[(src_name, symbol)] = tgt_name

    start_name = subset_to_name[start_subset]

    return DFA(dfa_states, set(alphabet), dfa_transitions, start_name, dfa_accept), transitions_computed

from Algoritms.class_dfa_nfa import DFA
from Algoritms_with_epsilon.epsilon_closure import epsilon_closure, build_epsilon_table


def determinize_lazy_epsilon(nfa):
    """
    Lazy (On-the-Fly) Determinization з підтримкою epsilon-переходів.

    Аналогічно lazy_subset, але кожна підмножина розширюється
    epsilon-замиканням перед кешуванням.
    """
    alphabet = sorted(sym for sym in nfa.alphabet if sym != "")
    transitions_computed = 0
    eps_table = build_epsilon_table(nfa.states, nfa.transitions)

    subset_to_name = {}
    counter = [0]

    def get_name(subset):
        if subset not in subset_to_name:
            subset_to_name[subset] = f"q{counter[0]}"
            counter[0] += 1
        return subset_to_name[subset]

    cache = {}

    def lazy_move(subset, symbol):
        nonlocal transitions_computed
        key = (subset, symbol)
        if key not in cache:
            nxt = set()
            for s in subset:
                nxt |= nfa.transitions.get((s, symbol), set())
            if nxt:
                nxt = epsilon_closure(nxt, nfa.transitions, eps_table)
                cache[key] = nxt
            else:
                cache[key] = None
            transitions_computed += 1
        return cache[key]

    # --- Матеріалізація через lazy DFS ---
    start_subset = epsilon_closure({nfa.start_state}, nfa.transitions, eps_table)
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

    # --- Побудова фінального ДКА ---
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
    result_alphabet = {sym for sym in nfa.alphabet if sym != ""}

    return DFA(dfa_states, result_alphabet, dfa_transitions, start_name, dfa_accept), transitions_computed

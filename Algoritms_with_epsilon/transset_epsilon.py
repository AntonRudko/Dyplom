from collections import deque
from Algoritms.class_dfa_nfa import DFA
from Algoritms_with_epsilon.epsilon_closure import epsilon_closure, build_epsilon_table


def determinize_transset_epsilon(nfa):
    merges_count = 0
    eps_table = build_epsilon_table(nfa.states, nfa.transitions)
    # Побудова trans_by_state без ε-переходів
    trans_by_state = {s: set() for s in nfa.states}
    for (s, a), targets in nfa.transitions.items():
        if a == "":
            continue
        for t in targets:
            trans_by_state[s].add((a, t))

    def make_tuple_from_states(state_set):
        """Об'єднує характеристики для множини станів (після ε-замикання)."""
        combined_T = set()
        combined_b = False
        for p in state_set:
            combined_T |= trans_by_state.get(p, set())
            if p in nfa.accept_states:
                combined_b = True
        return (frozenset(combined_T), combined_b)

    tuple_to_name = {}
    name_to_tuple = {}
    state_names = set()
    accept_names = set()
    dfa_transitions = {}

    def register_tuple(P):
        nonlocal merges_count
        if P in tuple_to_name:
            return tuple_to_name[P], False
        merges_count += 1
        name = f"q{len(tuple_to_name)}"
        tuple_to_name[P] = name
        name_to_tuple[name] = P
        state_names.add(name)
        T, b = P
        if b:
            accept_names.add(name)
        return name, True

    # Стартовий стан = ε-замикання стартового стану
    start_closure = epsilon_closure({nfa.start_state}, nfa.transitions, eps_table)
    start_tuple = make_tuple_from_states(start_closure)
    start_name, _ = register_tuple(start_tuple)

    alphabet = sorted(sym for sym in nfa.alphabet if sym != "")
    queue = deque([start_name])

    while queue:
        cur_name = queue.popleft()
        T, b = name_to_tuple[cur_name]

        for a in alphabet:
            # Знаходимо цільові стани по символу a
            target_states = set()
            for lab, p in T:
                if lab == a:
                    target_states.add(p)

            if not target_states:
                # Порожній перехід
                next_T = frozenset()
                next_b = False
            else:
                # Застосовуємо ε-замикання до цільових станів
                closed = epsilon_closure(target_states, nfa.transitions, eps_table)
                combined_T = set()
                next_b = False
                for p in closed:
                    combined_T |= trans_by_state.get(p, set())
                    if p in nfa.accept_states:
                        next_b = True
                next_T = frozenset(combined_T)

            P0 = (next_T, next_b)
            name0, is_new = register_tuple(P0)
            dfa_transitions[(cur_name, a)] = name0
            if is_new:
                queue.append(name0)

    result_alphabet = {sym for sym in nfa.alphabet if sym != ""}
    return DFA(state_names, result_alphabet, dfa_transitions, start_name, accept_names), merges_count

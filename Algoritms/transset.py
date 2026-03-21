from collections import deque
from Algoritms.class_dfa_nfa import DFA

def determinize_transset(nfa):
    merges_count = 0
    trans_by_state = {s: set() for s in nfa.states}
    for (s, a), targets in nfa.transitions.items():
        for t in targets:
            trans_by_state[s].add((a, t))

    def make_tuple_from_state(p):
        T = trans_by_state.get(p, set())
        b = p in nfa.accept_states
        return (frozenset(T), b)

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

    start_tuple = make_tuple_from_state(nfa.start_state)
    start_name, _ = register_tuple(start_tuple)

    alphabet = sorted(nfa.alphabet)
    queue = deque([start_name])

    while queue:
        cur_name = queue.popleft()
        T, b = name_to_tuple[cur_name]

        for a in alphabet:
            next_T = set()
            next_b = False
            for lab, p in T:
                if lab == a:
                    next_T |= trans_by_state.get(p, set())
                    if p in nfa.accept_states:
                        next_b = True
            P0 = (frozenset(next_T), next_b)
            name0, is_new = register_tuple(P0)
            dfa_transitions[(cur_name, a)] = name0
            if is_new:
                queue.append(name0)

    return DFA(state_names, nfa.alphabet, dfa_transitions, start_name, accept_names), merges_count

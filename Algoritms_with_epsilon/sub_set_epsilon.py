from collections import deque
from Algoritms.class_dfa_nfa import DFA
from Algoritms_with_epsilon.epsilon_closure import epsilon_closure, build_epsilon_table


def determinize_nfa_epsilon(nfa):
    subset_to_name = {}
    state_names = set()
    transitions = {}
    accept_names = set()
    subsets_processed = 0

    eps_table = build_epsilon_table(nfa.states, nfa.transitions)

    def new_name():
        return f"q{len(subset_to_name)}"

    start_subset = epsilon_closure({nfa.start_state}, nfa.transitions, eps_table)
    start_name = new_name()
    subset_to_name[start_subset] = start_name
    state_names.add(start_name)
    if start_subset & nfa.accept_states:
        accept_names.add(start_name)

    queue = deque([start_subset])

    alphabet = sorted(sym for sym in nfa.alphabet if sym != "")

    while queue:
        current = queue.popleft()
        cur_name = subset_to_name[current]
        subsets_processed += 1

        for symbol in alphabet:
            nxt = set()
            for p in sorted(current):
                nxt |= nfa.transitions.get((p, symbol), set())

            if not nxt:
                continue

            nxt = epsilon_closure(nxt, nfa.transitions, eps_table)

            if nxt not in subset_to_name:
                nm = new_name()
                subset_to_name[nxt] = nm
                state_names.add(nm)
                if nxt & nfa.accept_states:
                    accept_names.add(nm)
                queue.append(nxt)

            transitions[(cur_name, symbol)] = subset_to_name[nxt]

    result_alphabet = {sym for sym in nfa.alphabet if sym != ""}
    return DFA(state_names, result_alphabet, transitions, start_name, accept_names), subsets_processed

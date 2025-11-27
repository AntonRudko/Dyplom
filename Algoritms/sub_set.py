from collections import deque
from Algoritms.class_dfa_nfa import DFA

def determinize_nfa(nfa):
    subset_to_name = {}
    state_names = set()
    transitions = {}
    accept_names = set()

    def new_name():
        return f"q{len(subset_to_name)}"

    start_subset = frozenset([nfa.start_state])
    start_name = new_name()
    subset_to_name[start_subset] = start_name
    state_names.add(start_name)
    if nfa.start_state in nfa.accept_states:
        accept_names.add(start_name)

    queue = deque([start_subset])

    alphabet = sorted(nfa.alphabet)

    while queue:
        current = queue.popleft()
        cur_name = subset_to_name[current]

        for symbol in alphabet:
            nxt = set()
            for p in sorted(current):
                nxt |= nfa.transitions.get((p, symbol), set())
            nxt = frozenset(nxt)

            if not nxt:
                continue

            if nxt not in subset_to_name:
                nm = new_name()
                subset_to_name[nxt] = nm
                state_names.add(nm)
                if nxt & nfa.accept_states:
                    accept_names.add(nm)
                queue.append(nxt)

            transitions[(cur_name, symbol)] = subset_to_name[nxt]

    return DFA(state_names, nfa.alphabet, transitions, start_name, accept_names)

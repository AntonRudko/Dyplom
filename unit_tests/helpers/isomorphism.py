"""
DFA isomorphism check via BFS bijection construction.
"""

from collections import deque


def are_isomorphic(dfa1, dfa2):
    """
    Check if two DFAs are isomorphic by constructing a bijection via BFS.

    Two minimal DFAs recognizing the same language are always isomorphic.
    Returns True if a valid bijection exists, False otherwise.
    """
    alphabet = sorted(sym for sym in dfa1.alphabet if sym != "")
    alphabet2 = sorted(sym for sym in dfa2.alphabet if sym != "")

    if alphabet != alphabet2:
        return False

    if len(dfa1.states) != len(dfa2.states):
        return False

    if len(dfa1.accept_states) != len(dfa2.accept_states):
        return False

    # BFS bijection construction
    mapping = {}  # dfa1 state -> dfa2 state
    reverse_mapping = {}  # dfa2 state -> dfa1 state

    mapping[dfa1.start_state] = dfa2.start_state
    reverse_mapping[dfa2.start_state] = dfa1.start_state

    # Check start states have same acceptance
    s1_accept = dfa1.start_state in dfa1.accept_states
    s2_accept = dfa2.start_state in dfa2.accept_states
    if s1_accept != s2_accept:
        return False

    queue = deque([dfa1.start_state])

    while queue:
        s1 = queue.popleft()
        s2 = mapping[s1]

        for sym in alphabet:
            t1 = dfa1.transitions.get((s1, sym))
            t2 = dfa2.transitions.get((s2, sym))

            # Both must be defined or both undefined
            if (t1 is None) != (t2 is None):
                return False

            if t1 is None:
                continue

            if t1 in mapping:
                if mapping[t1] != t2:
                    return False
            else:
                if t2 in reverse_mapping:
                    return False
                # Check acceptance consistency
                if (t1 in dfa1.accept_states) != (t2 in dfa2.accept_states):
                    return False
                mapping[t1] = t2
                reverse_mapping[t2] = t1
                queue.append(t1)

    # All reachable states in dfa1 must be mapped
    return len(mapping) == len(dfa1.states)

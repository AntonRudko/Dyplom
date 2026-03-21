"""
DFA minimization via partition refinement (Hopcroft-style).
"""

from collections import deque


def minimize_dfa(dfa):
    """
    Minimize a DFA using partition refinement.

    Steps:
    1. BFS for reachable states
    2. Add dead state for totality
    3. Partition refinement {accept, non-accept} -> stable
    4. Build minimal DFA
    5. Remove dead state (partial DFA compatible with Transset/Subset output)

    Returns a new DFA-like object (namedtuple-style dict).
    """
    # Filter alphabet (no epsilon)
    alphabet = sorted(sym for sym in dfa.alphabet if sym != "")

    # Step 1: BFS for reachable states
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

    # Step 2: Add dead state for totality
    DEAD = "__dead__"
    total_transitions = {}
    needs_dead = False

    for s in states:
        for sym in alphabet:
            nxt = dfa.transitions.get((s, sym))
            if nxt is not None and nxt in states:
                total_transitions[(s, sym)] = nxt
            else:
                total_transitions[(s, sym)] = DEAD
                needs_dead = True

    if needs_dead:
        states = states | {DEAD}
        non_accept = non_accept | {DEAD}
        for sym in alphabet:
            total_transitions[(DEAD, sym)] = DEAD

    # Step 3: Partition refinement
    if not accept:
        # All states are non-accepting -> single partition
        partition = [states]
    elif not non_accept:
        partition = [accept]
    else:
        partition = [accept, non_accept]

    def get_partition_id(state, part):
        for i, group in enumerate(part):
            if state in group:
                return i
        return -1

    changed = True
    while changed:
        changed = False
        new_partition = []
        for group in partition:
            splits = {}
            for s in group:
                signature = tuple(
                    get_partition_id(total_transitions[(s, sym)], partition)
                    for sym in alphabet
                )
                if signature not in splits:
                    splits[signature] = set()
                splits[signature].add(s)
            parts = list(splits.values())
            if len(parts) > 1:
                changed = True
            new_partition.extend(parts)
        partition = new_partition

    # Step 4: Build minimal DFA
    state_to_group = {}
    for i, group in enumerate(partition):
        for s in group:
            state_to_group[s] = i

    start_group = state_to_group[dfa.start_state]

    min_states = set()
    min_transitions = {}
    min_accept = set()

    for i, group in enumerate(partition):
        rep = next(iter(group))
        min_states.add(i)
        if rep in accept:
            min_accept.add(i)
        for sym in alphabet:
            target_group = state_to_group[total_transitions[(rep, sym)]]
            min_transitions[(i, sym)] = target_group

    # Step 5: Remove dead state group
    if needs_dead:
        dead_group = state_to_group[DEAD]
        min_states.discard(dead_group)
        min_accept.discard(dead_group)
        min_transitions = {
            k: v for k, v in min_transitions.items()
            if k[0] != dead_group and v != dead_group
        }

    return MinimalDFA(
        states=min_states,
        alphabet=set(alphabet),
        transitions=min_transitions,
        start_state=start_group,
        accept_states=min_accept,
    )


class MinimalDFA:
    """Lightweight DFA container for minimized automata."""

    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_states = accept_states

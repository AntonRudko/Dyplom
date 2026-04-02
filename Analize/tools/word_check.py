def run_dfa(dfa, word):
    state = dfa.start_state
    for ch in word:
        if (state, ch) not in dfa.transitions:
            return False
        state = dfa.transitions[(state, ch)]
    return state in dfa.accept_states

def run_nfa(nfa, word):
    current = {nfa.start_state}
    for ch in word:
        next_states = set()
        for s in current:
            next_states |= nfa.transitions.get((s, ch), set())
        if not next_states:
            return False
        current = next_states
    return any(s in nfa.accept_states for s in current)

def run_words(nfa, dfa, words):
    equal = True
    for w in words:
        nfa_res = run_nfa(nfa, w)
        dfa_res = run_dfa(dfa, w)
        print(f'word: "{w}" -- for NFA : {nfa_res} -- for DFA: {dfa_res}')
        if nfa_res != dfa_res:
            equal = False
    print(f"Automats equal ? {equal}")
    return equal

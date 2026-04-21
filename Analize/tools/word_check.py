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

def run_words(nfa, dfa, words, method_name="unknown"):
    print(f"\n=== Метод детермінізації: {method_name} ===")
    equal = True
    lines = []
    for w in words:
        nfa_res = run_nfa(nfa, w)
        dfa_res = run_dfa(dfa, w)
        lines.append(f'слово: "{w}" -- для НСА : {nfa_res} -- для ДСА: {dfa_res}')
        if nfa_res != dfa_res:
            equal = False

    half = (len(lines) + 1) // 2
    left, right = lines[:half], lines[half:]
    width = max((len(l) for l in left), default=0)
    for i in range(half):
        l = left[i].ljust(width)
        r = right[i] if i < len(right) else ""
        print(f"{l} | {r}" if r else l)

    print(f"Автомати розпізнають одну й туж саму мову ? {equal}")
    return equal

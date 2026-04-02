from collections import deque
from Algoritms.class_dfa_nfa import DFA
from Algoritms_with_epsilon.epsilon_closure import epsilon_closure, build_epsilon_table


def determinize_brz_epsilon(nfa):
    alphabet = {sym for sym in nfa.alphabet if sym != ""}
    total_iterations = [0]

    eps_table = build_epsilon_table(nfa.states, nfa.transitions)

    def to_generic_from_nfa(nfa_obj):
        states = set(nfa_obj.states)
        start_states = epsilon_closure({nfa_obj.start_state}, nfa_obj.transitions, eps_table)
        accept_states = set(nfa_obj.accept_states)
        trans = {}
        for (p, a), dsts in nfa_obj.transitions.items():
            if a == "":
                continue
            trans[(p, a)] = set(dsts)
        return states, alphabet, start_states, accept_states, trans

    def reverse_automaton(states, alphabet, start_states, accept_states, trans):
        r_states = set(states)
        r_start_states = set(accept_states)
        r_accept_states = set(start_states)
        r_trans = {}
        for (p, a), dsts in trans.items():
            for q in dsts:
                key = (q, a)
                if key not in r_trans:
                    r_trans[key] = set()
                r_trans[key].add(p)
        return r_states, alphabet, r_start_states, r_accept_states, r_trans

    def determinize(states, alphabet, start_states, accept_states, trans):
        subset_to_name = {}
        name_to_subset = {}
        dfa_states = set()
        dfa_accept = set()
        dfa_trans = {}

        def new_name(subset):
            name = f"q{len(subset_to_name)}"
            subset_to_name[subset] = name
            name_to_subset[name] = subset
            dfa_states.add(name)
            if subset & accept_states:
                dfa_accept.add(name)
            return name

        start_subset = frozenset(start_states)
        start_name = new_name(start_subset)

        queue = deque([start_name])
        alpha_sorted = sorted(alphabet)

        while queue:
            cur_name = queue.popleft()
            cur_subset = name_to_subset[cur_name]
            total_iterations[0] += 1

            for a in alpha_sorted:
                nxt = set()
                for p in cur_subset:
                    nxt |= trans.get((p, a), set())
                if not nxt:
                    continue
                nxt_subset = frozenset(nxt)
                if nxt_subset not in subset_to_name:
                    nxt_name = new_name(nxt_subset)
                    queue.append(nxt_name)
                else:
                    nxt_name = subset_to_name[nxt_subset]
                dfa_trans[(cur_name, a)] = nxt_name

        return dfa_states, alphabet, start_name, dfa_accept, dfa_trans

    A_states, A_alpha, A_start, A_accept, A_trans = to_generic_from_nfa(nfa)

    # Додаємо ε-замикання до переходів
    eps_trans = {}
    for (p, a), dsts in A_trans.items():
        closed = set()
        for d in dsts:
            closed |= epsilon_closure({d}, nfa.transitions, eps_table)
        eps_trans[(p, a)] = closed
    A_trans = eps_trans

    R1 = reverse_automaton(A_states, A_alpha, A_start, A_accept, A_trans)
    D1_states, D1_alpha, D1_start, D1_accept, D1_trans = determinize(*R1)
    R2 = reverse_automaton(D1_states, D1_alpha, {D1_start}, D1_accept, {
        (p, a): {q} for (p, a), q in D1_trans.items()
    })
    D2_states, D2_alpha, D2_start, D2_accept, D2_trans = determinize(*R2)

    return DFA(D2_states, D2_alpha, D2_trans, D2_start, D2_accept), total_iterations[0]

from collections import deque
from Algoritms.class_dfa_nfa import DFA
from Algoritms_with_epsilon.epsilon_closure import epsilon_closure, build_epsilon_table


def determinize_qsc_epsilon(nfa):
    """
    Quick Subset Construction (Dusi & Lamperti, 2023) з ε-замиканнями.

    Аналогічно базовому QSC з bitset-оптимізацією, але кожна
    обчислена множина цілей додатково розширюється ε-замиканням.

    Фаза 1+2 — Клонування з негайною реструктуризацією:
        Стартовий стан = ε-closure({start}).
        Для кожного стану (extension = бітова маска після ε-closure):
        - Обчислюємо move(ext, sym) = ⋃ δ(s, sym) для s ∈ ext
        - Застосовуємо ε-closure до результату
        - Якщо результат новий — реєструємо і додаємо в чергу

    Фаза 3 — Прибирання:
        BFS від стартового стану, перейменування.

    Метрика:
        singularities_resolved — кількість переходів де move
        давав множину > 1 стану (до ε-closure).
    """
    states_list = sorted(nfa.states)
    n = len(states_list)
    state_to_bit = {s: i for i, s in enumerate(states_list)}
    alphabet = sorted(sym for sym in nfa.alphabet if sym != "")

    # Передобчислення ε-замикань
    eps_table = build_epsilon_table(nfa.states, nfa.transitions)

    # Бітова маска accepting станів
    accept_mask = 0
    for s in nfa.accept_states:
        accept_mask |= (1 << state_to_bit[s])

    # ε-closure як бітова маска для кожного стану
    eps_mask = [0] * n
    for s in states_list:
        idx = state_to_bit[s]
        for t in eps_table[s]:
            eps_mask[idx] |= (1 << state_to_bit[t])

    def eps_closure_mask(mask):
        """ε-замикання бітової маски."""
        result = 0
        bits = mask
        while bits:
            lowest = bits & (-bits)
            idx = lowest.bit_length() - 1
            result |= eps_mask[idx]
            bits ^= lowest
        return result

    # NFA-переходи (без ε): nfa_trans[bit_index][sym] = бітова маска
    nfa_trans = [None] * n
    for s in states_list:
        idx = state_to_bit[s]
        t = {}
        for sym in alphabet:
            mask = 0
            for tgt in nfa.transitions.get((s, sym), set()):
                mask |= (1 << state_to_bit[tgt])
            t[sym] = mask
        nfa_trans[idx] = t

    def nfa_move(ext_mask, sym):
        """move(ext, sym) без ε-closure."""
        result = 0
        bits = ext_mask
        while bits:
            lowest = bits & (-bits)
            idx = lowest.bit_length() - 1
            result |= nfa_trans[idx][sym]
            bits ^= lowest
        return result

    # --- Реєстр станів ---
    ext_to_id = {}
    id_to_ext = {}
    id_accept = {}
    next_id = 0

    def register(ext_mask):
        if ext_mask in ext_to_id:
            return ext_to_id[ext_mask], False
        nonlocal next_id
        sid = next_id
        next_id += 1
        ext_to_id[ext_mask] = sid
        id_to_ext[sid] = ext_mask
        id_accept[sid] = bool(ext_mask & accept_mask)
        return sid, True

    trans = {}
    singularities_resolved = 0
    needs_transitions = deque()

    # === Фаза 1+2 ===

    # Стартовий стан = ε-closure({start})
    start_mask = eps_closure_mask(1 << state_to_bit[nfa.start_state])
    start_id, _ = register(start_mask)
    needs_transitions.append(start_id)

    while needs_transitions:
        sid = needs_transitions.popleft()
        ext = id_to_ext[sid]

        for sym in alphabet:
            # move без ε-closure
            raw_move = nfa_move(ext, sym)
            if not raw_move:
                continue

            # Рахуємо singularities (>1 біт у raw_move)
            if raw_move & (raw_move - 1):
                singularities_resolved += 1

            # ε-closure результату
            targets_mask = eps_closure_mask(raw_move)

            child_id, is_new = register(targets_mask)
            trans[(sid, sym)] = child_id
            if is_new:
                needs_transitions.append(child_id)

    # === Фаза 3: BFS від старту + перейменування ===

    rename = {}
    final_trans = {}
    final_states = set()
    final_accept = set()
    idx = 0

    queue = deque([start_id])
    rename[start_id] = f"q{idx}"
    idx += 1

    while queue:
        sid = queue.popleft()
        s_new = rename[sid]
        final_states.add(s_new)
        if id_accept[sid]:
            final_accept.add(s_new)

        for sym in alphabet:
            tgt = trans.get((sid, sym))
            if tgt is not None:
                if tgt not in rename:
                    rename[tgt] = f"q{idx}"
                    idx += 1
                    queue.append(tgt)
                final_trans[(s_new, sym)] = rename[tgt]

    result_alphabet = set(alphabet)
    return DFA(final_states, result_alphabet, final_trans,
               "q0", final_accept), singularities_resolved

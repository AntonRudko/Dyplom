from collections import deque
from Algoritms.class_dfa_nfa import DFA


def determinize_qsc(nfa):
    """
    Quick Subset Construction (Dusi & Lamperti, 2023) — bitset-оптимізація.

    На відміну від класичного Subset Construction, який будує DFA з нуля,
    QSC починає з клону НКА і прогресивно виправляє лише недетерміновані місця
    (singularities). Детерміновані частини автомата зберігаються як є.

    Фаза 1+2 (об'єднані) — Клонування з негайною реструктуризацією:
        Кожен стан НКА клонується. Переходи перевіряються одразу:
        - Детермінований (1 ціль) → зберігається як є.
        - Singularity (>1 цілі) → створюється merged-стан з extension =
          об'єднання NFA-переходів, і перехід замінюється на один.
        Для нових merged-станів переходи обчислюються аналогічно.

    Фаза 3 — Прибирання:
        BFS від стартового стану, видалення недосяжних, перейменування.

    Використовує бітове представлення (extension = int бітова маска)
    для швидких операцій об'єднання через побітове OR.

    Метрика:
        singularities_resolved — кількість усунених точок недетермінізму.
    """
    states_list = sorted(nfa.states)
    n = len(states_list)
    state_to_bit = {s: i for i, s in enumerate(states_list)}
    alphabet = sorted(nfa.alphabet)

    # Бітова маска accepting станів
    accept_mask = 0
    for s in nfa.accept_states:
        accept_mask |= (1 << state_to_bit[s])

    # Передобчислення NFA-переходів: nfa_trans[bit_index][sym] = бітова маска цілей
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
        """Об'єднання NFA-переходів зі станів ext по символу sym (bitset OR)."""
        result = 0
        bits = ext_mask
        while bits:
            lowest = bits & (-bits)
            idx = lowest.bit_length() - 1
            result |= nfa_trans[idx][sym]
            bits ^= lowest
        return result

    # --- Реєстр станів: extension_mask -> state_id ---
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

    # Детерміновані переходи: (state_id, sym) -> target_state_id
    trans = {}
    singularities_resolved = 0

    # Черга merged-станів, яким потрібно обчислити переходи
    needs_transitions = deque()

    # === Фаза 1+2: Клонування з негайним вирішенням singularities ===

    def ensure_registered(mask):
        """Зареєструвати стан якщо ще не існує, повернути id."""
        if mask in ext_to_id:
            return ext_to_id[mask]
        sid, _ = register(mask)
        return sid

    # Реєструємо тільки стартовий стан, решта — за потребою
    start_mask = 1 << state_to_bit[nfa.start_state]
    start_id = ensure_registered(start_mask)
    needs_transitions.append(start_id)

    # Обробляємо стани: для singletons — перевіряємо singularities,
    # для merged — обчислюємо переходи через nfa_move
    while needs_transitions:
        sid = needs_transitions.popleft()
        ext = id_to_ext[sid]

        # Перевірка: singleton чи merged?
        is_singleton = not (ext & (ext - 1))

        for sym in alphabet:
            if is_singleton:
                # Singleton: беремо переходи з NFA напряму
                src_bit = ext.bit_length() - 1
                targets_mask = nfa_trans[src_bit][sym]
            else:
                # Merged: обчислюємо через nfa_move
                targets_mask = nfa_move(ext, sym)

            if not targets_mask:
                continue

            if is_singleton and not (targets_mask & (targets_mask - 1)):
                # Детермінований перехід singleton → singleton
                target_id = ensure_registered(targets_mask)
                trans[(sid, sym)] = target_id
                if targets_mask not in ext_to_id or ext_to_id[targets_mask] == target_id:
                    # Новий singleton — потрібно обробити його переходи
                    if (target_id, alphabet[0]) not in trans and target_id != sid:
                        needs_transitions.append(target_id)
            else:
                # Singularity або merged перехід
                if is_singleton:
                    singularities_resolved += 1
                child_id, is_new = register(targets_mask)
                trans[(sid, sym)] = child_id
                if is_new:
                    needs_transitions.append(child_id)

    # Обчислюємо переходи для нових merged-станів
    while needs_transitions:
        sid = needs_transitions.popleft()
        ext = id_to_ext[sid]
        for sym in alphabet:
            child_ext = nfa_move(ext, sym)
            if not child_ext:
                continue
            child_id, is_new = register(child_ext)
            trans[(sid, sym)] = child_id
            if is_new:
                needs_transitions.append(child_id)

    # === Фаза 3: BFS від старту + перейменування ===

    start_id = ext_to_id[1 << state_to_bit[nfa.start_state]]

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

    return DFA(final_states, set(alphabet), final_trans,
               "q0", final_accept), singularities_resolved

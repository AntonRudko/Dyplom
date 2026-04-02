from collections import deque


def build_epsilon_table(states, transitions):
    """
    Передобчислення ε-замикань для кожного стану.
    Один раз будує таблицю: state -> frozenset(досяжні через ε).
    Час: O(n * (n + eε)) ≤ O(n³).  Пам'ять: O(n²).
    """
    table = {}
    for s in states:
        closure = set()
        closure.add(s)
        queue = deque([s])
        while queue:
            cur = queue.popleft()
            for target in transitions.get((cur, ""), set()):
                if target not in closure:
                    closure.add(target)
                    queue.append(target)
        table[s] = frozenset(closure)
    return table


def epsilon_closure(states, transitions, table=None):
    """
    ε-замикання множини станів.
    Якщо table передано — union по таблиці за O(n).
    Інакше — BFS з нуля за O(n + eε).
    """
    if table is not None:
        result = set()
        for s in states:
            result |= table[s]
        return frozenset(result)

    closure = set(states)
    queue = deque(states)
    while queue:
        s = queue.popleft()
        for target in transitions.get((s, ""), set()):
            if target not in closure:
                closure.add(target)
                queue.append(target)
    return frozenset(closure)
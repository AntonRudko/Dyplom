from collections import deque


def epsilon_closure(states, transitions):
    """
    BFS по ε-переходах (ключ (state, "")).
    Приймає множину станів, повертає frozenset усіх досяжних станів.
    """
    closure = set(states)
    queue = deque(states)

    while queue:
        s = queue.popleft()
        for target in transitions.get((s, ""), set()):
            if target not in closure:
                closure.add(target)
                queue.append(target)

    return frozenset(closure)

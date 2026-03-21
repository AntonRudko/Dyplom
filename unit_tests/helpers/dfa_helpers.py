"""
Helpers for running DFA/NFA and generating test words.
"""

import random
import itertools
from collections import deque


def run_dfa(dfa, word):
    """Run a word on a DFA. Returns True if accepted, False otherwise."""
    state = dfa.start_state
    for ch in word:
        key = (state, ch)
        if key not in dfa.transitions:
            return False
        state = dfa.transitions[key]
    return state in dfa.accept_states


def _epsilon_closure(states, transitions):
    """Compute epsilon closure of a set of states."""
    closure = set(states)
    queue = deque(states)
    while queue:
        s = queue.popleft()
        for target in transitions.get((s, ""), set()):
            if target not in closure:
                closure.add(target)
                queue.append(target)
    return closure


def run_nfa(nfa, word):
    """
    Run a word on an NFA with epsilon-closure support.
    Returns True if accepted, False otherwise.
    """
    current = _epsilon_closure({nfa.start_state}, nfa.transitions)
    for ch in word:
        nxt = set()
        for s in current:
            nxt |= nfa.transitions.get((s, ch), set())
        current = _epsilon_closure(nxt, nfa.transitions)
        if not current:
            return False
    return bool(current & nfa.accept_states)


def gen_random_words(alphabet, count=200, max_len=15):
    """Generate random words over given alphabet."""
    alphabet = sorted(sym for sym in alphabet if sym != "")
    words = [""]  # always include empty word
    for _ in range(count - 1):
        length = random.randint(0, max_len)
        word = "".join(random.choice(alphabet) for _ in range(length))
        words.append(word)
    return words


def gen_systematic_words(alphabet, max_len=4):
    """Generate ALL words up to given length over alphabet."""
    alphabet = sorted(sym for sym in alphabet if sym != "")
    words = [""]
    for length in range(1, max_len + 1):
        for combo in itertools.product(alphabet, repeat=length):
            words.append("".join(combo))
    return words

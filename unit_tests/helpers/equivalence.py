"""
High-level equivalence checks for NFA/DFA comparison.
"""

from .dfa_helpers import run_dfa, run_nfa, gen_random_words, gen_systematic_words
from .minimization import minimize_dfa
from .isomorphism import are_isomorphic


def check_language_equivalence_by_words(nfa, dfa, count=300, max_len=15):
    """
    Check that DFA accepts the same language as NFA by testing on random
    and systematic words.

    Returns (ok, mismatches) where ok is True if no mismatches found.
    """
    alphabet = nfa.alphabet
    words = gen_random_words(alphabet, count=count, max_len=max_len)
    words += gen_systematic_words(alphabet, max_len=3)
    # deduplicate
    words = list(set(words))

    mismatches = []
    for word in words:
        nfa_result = run_nfa(nfa, word)
        dfa_result = run_dfa(dfa, word)
        if nfa_result != dfa_result:
            mismatches.append((word, nfa_result, dfa_result))

    return len(mismatches) == 0, mismatches


def check_dfa_equivalence_by_minimization(dfa1, dfa2):
    """
    Check that two DFAs are equivalent by minimizing both and checking isomorphism.

    After canonical minimization, a DFA accepting the empty language has
    zero states (dead-equivalence class removed). Handle that case explicitly.

    Returns True if the minimized DFAs are isomorphic.
    """
    min1 = minimize_dfa(dfa1)
    min2 = minimize_dfa(dfa2)
    if not min1.states and not min2.states:
        return True
    if len(min1.states) != len(min2.states):
        return False
    return are_isomorphic(min1, min2)


def check_all_algorithms_equivalent(nfa, algorithms):
    """
    Run all algorithms on an NFA and verify all produce equivalent DFAs.

    Parameters:
        nfa: The source NFA
        algorithms: list of (name, function) pairs where function(nfa) -> (DFA, int)

    Returns:
        (all_ok, results_dict) where:
        - all_ok: True if all algorithms produce equivalent DFAs
        - results_dict: {name: {'dfa': dfa, 'count': count, 'word_ok': bool, 'iso_ok': bool}}
    """
    results = {}

    # Run all algorithms
    dfas = []
    for name, func in algorithms:
        dfa, count = func(nfa)
        results[name] = {"dfa": dfa, "count": count}
        dfas.append((name, dfa))

    all_ok = True

    # Check word equivalence with NFA
    for name, dfa in dfas:
        ok, mismatches = check_language_equivalence_by_words(nfa, dfa)
        results[name]["word_ok"] = ok
        results[name]["word_mismatches"] = mismatches
        if not ok:
            all_ok = False

    # Check pairwise minimization + isomorphism
    for i in range(len(dfas)):
        for j in range(i + 1, len(dfas)):
            name_i, dfa_i = dfas[i]
            name_j, dfa_j = dfas[j]
            iso = check_dfa_equivalence_by_minimization(dfa_i, dfa_j)
            key = f"iso_{name_i}_vs_{name_j}"
            results[key] = iso
            if not iso:
                all_ok = False

    return all_ok, results

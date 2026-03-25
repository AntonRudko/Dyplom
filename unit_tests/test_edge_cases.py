"""
Edge case tests for determinization algorithms.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms.lazy_subset import determinize_lazy
from Algoritms.class_dfa_nfa import NFA

from unit_tests.helpers.dfa_helpers import run_dfa, run_nfa, gen_systematic_words
from unit_tests.helpers.equivalence import check_language_equivalence_by_words


ALGORITHMS = [
    ("Subset", determinize_nfa),
    ("Brzozowski", determinize_brz),
    ("Transset", determinize_transset),
    ("Lazy", determinize_lazy),
]


class TestEdgeCases(unittest.TestCase):

    def _check_all(self, nfa, label=""):
        """Check all algorithms produce correct DFA for given NFA."""
        for name, func in ALGORITHMS:
            with self.subTest(algorithm=name):
                dfa, _ = func(nfa)
                ok, mismatches = check_language_equivalence_by_words(nfa, dfa)
                self.assertTrue(ok, f"{label}/{name}: {mismatches[:5]}")

    def test_single_state_accepting(self):
        """NFA with one accepting state (accepts all words)."""
        nfa = NFA(
            states={"q0"},
            alphabet={"a", "b"},
            transitions={
                ("q0", "a"): {"q0"},
                ("q0", "b"): {"q0"},
            },
            start_state="q0",
            accept_states={"q0"},
        )
        self._check_all(nfa, "single_accept")

    def test_single_state_rejecting(self):
        """NFA with one non-accepting state (rejects everything except maybe empty)."""
        nfa = NFA(
            states={"q0"},
            alphabet={"a", "b"},
            transitions={
                ("q0", "a"): {"q0"},
                ("q0", "b"): {"q0"},
            },
            start_state="q0",
            accept_states=set(),
        )
        self._check_all(nfa, "single_reject")

    def test_no_transitions(self):
        """NFA with no transitions at all."""
        nfa = NFA(
            states={"q0", "q1"},
            alphabet={"a"},
            transitions={},
            start_state="q0",
            accept_states={"q1"},
        )
        for name, func in ALGORITHMS:
            with self.subTest(algorithm=name):
                dfa, _ = func(nfa)
                # Only empty word or nothing accepted
                self.assertFalse(run_dfa(dfa, "a"))
                self.assertFalse(run_dfa(dfa, "aa"))

    def test_all_states_accepting(self):
        """NFA where all states are accepting."""
        nfa = NFA(
            states={"q0", "q1", "q2"},
            alphabet={"a", "b"},
            transitions={
                ("q0", "a"): {"q1"},
                ("q0", "b"): {"q2"},
                ("q1", "a"): {"q0", "q2"},
                ("q1", "b"): {"q0"},
                ("q2", "a"): {"q0"},
                ("q2", "b"): {"q1"},
            },
            start_state="q0",
            accept_states={"q0", "q1", "q2"},
        )
        self._check_all(nfa, "all_accept")

    def test_unreachable_states(self):
        """NFA with unreachable states."""
        nfa = NFA(
            states={"q0", "q1", "q2", "unreachable"},
            alphabet={"a", "b"},
            transitions={
                ("q0", "a"): {"q1"},
                ("q1", "b"): {"q0"},
                ("unreachable", "a"): {"q2"},
                ("q2", "b"): {"unreachable"},
            },
            start_state="q0",
            accept_states={"q1"},
        )
        self._check_all(nfa, "unreachable")

    def test_already_deterministic(self):
        """NFA that is already deterministic (each transition has exactly one target)."""
        nfa = NFA(
            states={"q0", "q1", "q2"},
            alphabet={"a", "b"},
            transitions={
                ("q0", "a"): {"q1"},
                ("q0", "b"): {"q2"},
                ("q1", "a"): {"q2"},
                ("q1", "b"): {"q0"},
                ("q2", "a"): {"q0"},
                ("q2", "b"): {"q1"},
            },
            start_state="q0",
            accept_states={"q2"},
        )
        self._check_all(nfa, "already_det")

    def test_empty_target_sets(self):
        """NFA with some transitions having empty target sets (dead ends)."""
        nfa = NFA(
            states={"q0", "q1"},
            alphabet={"a", "b"},
            transitions={
                ("q0", "a"): {"q1"},
                ("q0", "b"): set(),
                ("q1", "a"): set(),
                ("q1", "b"): {"q0"},
            },
            start_state="q0",
            accept_states={"q1"},
        )
        self._check_all(nfa, "empty_targets")

    def test_self_loops_everywhere(self):
        """NFA with self-loops on every state and symbol."""
        nfa = NFA(
            states={"q0", "q1", "q2"},
            alphabet={"a", "b"},
            transitions={
                ("q0", "a"): {"q0", "q1"},
                ("q0", "b"): {"q0"},
                ("q1", "a"): {"q1"},
                ("q1", "b"): {"q1", "q2"},
                ("q2", "a"): {"q2"},
                ("q2", "b"): {"q2"},
            },
            start_state="q0",
            accept_states={"q2"},
        )
        self._check_all(nfa, "self_loops")


if __name__ == "__main__":
    unittest.main()

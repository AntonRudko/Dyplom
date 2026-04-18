"""
Edge case tests for determinization algorithms — validated via
minimization + isomorphism against Subset Construction.

Every test gives a 100% correctness guarantee (Myhill-Nerode theorem).
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms.class_dfa_nfa import NFA

from unit_tests.helpers.equivalence import check_dfa_equivalence_by_minimization


NON_REFERENCE_ALGORITHMS = [
    ("Brzozowski", determinize_brz),
    ("Transset", determinize_transset),
]


class TestEdgeCases(unittest.TestCase):
    """All algorithms must agree with Subset Construction on edge-case NFAs."""

    def _check_all_equivalent_to_subset(self, nfa, label):
        subset_dfa, _ = determinize_nfa(nfa)
        for name, func in NON_REFERENCE_ALGORITHMS:
            with self.subTest(algorithm=name):
                other_dfa, _ = func(nfa)
                self.assertTrue(
                    check_dfa_equivalence_by_minimization(subset_dfa, other_dfa),
                    f"{label}/{name}: not equivalent to Subset",
                )

    def test_single_state_accepting(self):
        """NFA with one accepting state (accepts Σ*)."""
        nfa = NFA(
            states={"q0"},
            alphabet={"a", "b"},
            transitions={("q0", "a"): {"q0"}, ("q0", "b"): {"q0"}},
            start_state="q0",
            accept_states={"q0"},
        )
        self._check_all_equivalent_to_subset(nfa, "single_accept")

    def test_single_state_rejecting(self):
        """NFA with one non-accepting state (empty language)."""
        nfa = NFA(
            states={"q0"},
            alphabet={"a", "b"},
            transitions={("q0", "a"): {"q0"}, ("q0", "b"): {"q0"}},
            start_state="q0",
            accept_states=set(),
        )
        self._check_all_equivalent_to_subset(nfa, "single_reject")

    def test_no_transitions(self):
        """NFA with no transitions at all."""
        nfa = NFA(
            states={"q0", "q1"},
            alphabet={"a"},
            transitions={},
            start_state="q0",
            accept_states={"q1"},
        )
        self._check_all_equivalent_to_subset(nfa, "no_transitions")

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
        self._check_all_equivalent_to_subset(nfa, "all_accept")

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
        self._check_all_equivalent_to_subset(nfa, "unreachable")

    def test_already_deterministic(self):
        """NFA that is already deterministic."""
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
        self._check_all_equivalent_to_subset(nfa, "already_det")

    def test_empty_target_sets(self):
        """NFA with transitions to empty target sets (dead ends)."""
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
        self._check_all_equivalent_to_subset(nfa, "empty_targets")

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
        self._check_all_equivalent_to_subset(nfa, "self_loops")


if __name__ == "__main__":
    unittest.main()

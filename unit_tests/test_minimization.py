"""
Tests for DFA minimization and isomorphism helpers.

These helpers are the foundation of the 100%-guarantee equivalence checks
used across all other test files. They are validated here against
hand-crafted reference DFAs.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Algoritms.class_dfa_nfa import DFA

from unit_tests.helpers.minimization import minimize_dfa
from unit_tests.helpers.isomorphism import are_isomorphic


class TestMinimization(unittest.TestCase):
    """Partition-refinement minimization (Moore's algorithm)."""

    def test_already_minimal_dfa(self):
        """Minimizing an already-minimal DFA does not reduce state count."""
        dfa = DFA(
            state_names={"q0", "q1"},
            alphabet={"a", "b"},
            transitions={
                ("q0", "a"): "q1", ("q0", "b"): "q0",
                ("q1", "a"): "q1", ("q1", "b"): "q0",
            },
            start_state="q0",
            accept_states={"q1"},
        )
        min_dfa = minimize_dfa(dfa)
        self.assertEqual(len(min_dfa.states), 2)

    def test_redundant_states_merged(self):
        """Minimization merges unreachable/equivalent states."""
        dfa = DFA(
            state_names={"q0", "q1", "q2"},
            alphabet={"a"},
            transitions={
                ("q0", "a"): "q1",
                ("q1", "a"): "q1",
                ("q2", "a"): "q2",
            },
            start_state="q0",
            accept_states={"q1", "q2"},
        )
        min_dfa = minimize_dfa(dfa)
        self.assertLessEqual(len(min_dfa.states), 2)


class TestIsomorphism(unittest.TestCase):
    """Isomorphism helper used in equivalence checks."""

    def test_reflexive(self):
        """A DFA is isomorphic to itself."""
        dfa = DFA(
            state_names={0, 1},
            alphabet={"a", "b"},
            transitions={
                (0, "a"): 1, (0, "b"): 0,
                (1, "a"): 1, (1, "b"): 0,
            },
            start_state=0,
            accept_states={1},
        )
        self.assertTrue(are_isomorphic(dfa, dfa))

    def test_renamed_states(self):
        """DFAs that differ only by state renaming are isomorphic."""
        dfa1 = DFA(
            state_names={0, 1},
            alphabet={"a", "b"},
            transitions={
                (0, "a"): 1, (0, "b"): 0,
                (1, "a"): 1, (1, "b"): 0,
            },
            start_state=0,
            accept_states={1},
        )
        dfa2 = DFA(
            state_names={"X", "Y"},
            alphabet={"a", "b"},
            transitions={
                ("X", "a"): "Y", ("X", "b"): "X",
                ("Y", "a"): "Y", ("Y", "b"): "X",
            },
            start_state="X",
            accept_states={"Y"},
        )
        self.assertTrue(are_isomorphic(dfa1, dfa2))

    def test_different_languages_not_isomorphic(self):
        """DFAs for different languages are not isomorphic."""
        dfa_ends_with_a = DFA(
            state_names={0, 1},
            alphabet={"a", "b"},
            transitions={
                (0, "a"): 1, (0, "b"): 0,
                (1, "a"): 1, (1, "b"): 0,
            },
            start_state=0,
            accept_states={1},
        )
        dfa_ends_with_b = DFA(
            state_names={0, 1},
            alphabet={"a", "b"},
            transitions={
                (0, "a"): 0, (0, "b"): 1,
                (1, "a"): 0, (1, "b"): 1,
            },
            start_state=0,
            accept_states={1},
        )
        self.assertFalse(are_isomorphic(dfa_ends_with_a, dfa_ends_with_b))


if __name__ == "__main__":
    unittest.main()

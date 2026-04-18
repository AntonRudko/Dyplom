"""
Unit tests for Subset Construction — validated against hand-crafted
reference minimal DFAs.

Subset Construction is the textbook reference algorithm. Its correctness
is anchored here via structural isomorphism against manually constructed
minimal DFAs for known languages. All other algorithms are then validated
against Subset via `check_dfa_equivalence_by_minimization`.

Every test gives a 100% correctness guarantee (Myhill-Nerode theorem:
two DFAs accept the same language iff their minimal forms are isomorphic).
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Algoritms.sub_set import determinize_nfa
from Algoritms.class_dfa_nfa import NFA, DFA

from unit_tests.helpers.equivalence import check_dfa_equivalence_by_minimization


class TestSubsetAgainstReference(unittest.TestCase):
    """Validate Subset Construction against hand-crafted minimal DFAs."""

    def test_sigma_star(self):
        """NFA accepting Σ* -> minimal DFA has 1 accepting state."""
        nfa = NFA(
            states={"q0"},
            alphabet={"a", "b"},
            transitions={("q0", "a"): {"q0"}, ("q0", "b"): {"q0"}},
            start_state="q0",
            accept_states={"q0"},
        )
        reference = DFA(
            state_names={0},
            alphabet={"a", "b"},
            transitions={(0, "a"): 0, (0, "b"): 0},
            start_state=0,
            accept_states={0},
        )
        dfa, _ = determinize_nfa(nfa)
        self.assertTrue(check_dfa_equivalence_by_minimization(dfa, reference))

    def test_ends_with_a(self):
        """NFA accepting strings ending in 'a' -> 2-state minimal DFA."""
        nfa = NFA(
            states={"q0", "q1"},
            alphabet={"a", "b"},
            transitions={
                ("q0", "a"): {"q0", "q1"},
                ("q0", "b"): {"q0"},
            },
            start_state="q0",
            accept_states={"q1"},
        )
        reference = DFA(
            state_names={0, 1},
            alphabet={"a", "b"},
            transitions={
                (0, "a"): 1, (0, "b"): 0,
                (1, "a"): 1, (1, "b"): 0,
            },
            start_state=0,
            accept_states={1},
        )
        dfa, _ = determinize_nfa(nfa)
        self.assertTrue(check_dfa_equivalence_by_minimization(dfa, reference))

    def test_contains_ab(self):
        """NFA accepting strings containing 'ab' -> 3-state minimal DFA."""
        nfa = NFA(
            states={"q0", "q1", "q2"},
            alphabet={"a", "b"},
            transitions={
                ("q0", "a"): {"q0", "q1"},
                ("q0", "b"): {"q0"},
                ("q1", "b"): {"q2"},
                ("q2", "a"): {"q2"},
                ("q2", "b"): {"q2"},
            },
            start_state="q0",
            accept_states={"q2"},
        )
        # Minimal DFA: s0 (haven't seen 'a'), s1 (last was 'a'), s2 (seen 'ab').
        reference = DFA(
            state_names={0, 1, 2},
            alphabet={"a", "b"},
            transitions={
                (0, "a"): 1, (0, "b"): 0,
                (1, "a"): 1, (1, "b"): 2,
                (2, "a"): 2, (2, "b"): 2,
            },
            start_state=0,
            accept_states={2},
        )
        dfa, _ = determinize_nfa(nfa)
        self.assertTrue(check_dfa_equivalence_by_minimization(dfa, reference))

    def test_empty_language(self):
        """NFA with no accepting states -> minimal DFA accepts nothing."""
        nfa = NFA(
            states={"q0"},
            alphabet={"a", "b"},
            transitions={("q0", "a"): {"q0"}, ("q0", "b"): {"q0"}},
            start_state="q0",
            accept_states=set(),
        )
        reference = DFA(
            state_names={0},
            alphabet={"a", "b"},
            transitions={(0, "a"): 0, (0, "b"): 0},
            start_state=0,
            accept_states=set(),
        )
        dfa, _ = determinize_nfa(nfa)
        self.assertTrue(check_dfa_equivalence_by_minimization(dfa, reference))


if __name__ == "__main__":
    unittest.main()

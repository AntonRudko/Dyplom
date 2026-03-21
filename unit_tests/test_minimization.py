"""
Tests_Diagram for DFA minimization and isomorphism helpers.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Algoritms.sub_set import determinize_nfa
from Algoritms.class_dfa_nfa import DFA, NFA
from Tests_Diagram.nfa_generators import gen_nth_from_last

from helpers.dfa_helpers import run_dfa, gen_systematic_words
from helpers.minimization import minimize_dfa
from helpers.isomorphism import are_isomorphic


class TestMinimization(unittest.TestCase):

    def test_already_minimal_dfa(self):
        """Minimizing an already minimal DFA returns same number of states."""
        # Simple 2-state DFA: accepts strings ending in 'a'
        dfa = DFA(
            state_names={"q0", "q1"},
            alphabet={"a", "b"},
            transitions={
                ("q0", "a"): "q1",
                ("q0", "b"): "q0",
                ("q1", "a"): "q1",
                ("q1", "b"): "q0",
            },
            start_state="q0",
            accept_states={"q1"},
        )
        min_dfa = minimize_dfa(dfa)
        self.assertEqual(len(min_dfa.states), 2)

    def test_states_merge(self):
        """Minimization merges equivalent states."""
        # DFA with redundant states: q1 and q2 behave identically
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
        # q2 is unreachable from q0, so after BFS only q0,q1 remain -> 2 states
        self.assertLessEqual(len(min_dfa.states), 2)

    def test_language_preserved_after_minimization(self):
        """Minimized DFA accepts the same language."""
        nfa = gen_nth_from_last(4)
        dfa, _ = determinize_nfa(nfa)
        min_dfa = minimize_dfa(dfa)

        words = gen_systematic_words(dfa.alphabet, max_len=5)
        for word in words:
            original = run_dfa(dfa, word)
            minimized = run_dfa(min_dfa, word)
            self.assertEqual(
                original, minimized,
                f"Word '{word}': original={original}, minimized={minimized}",
            )

    def test_isomorphism_reflexive(self):
        """A DFA is isomorphic to itself."""
        nfa = gen_nth_from_last(3)
        dfa, _ = determinize_nfa(nfa)
        min_dfa = minimize_dfa(dfa)
        self.assertTrue(are_isomorphic(min_dfa, min_dfa))

    def test_isomorphism_renamed_states(self):
        """Two DFAs that differ only in state names are isomorphic."""
        dfa1 = DFA(
            state_names={0, 1},
            alphabet={"a", "b"},
            transitions={
                (0, "a"): 1,
                (0, "b"): 0,
                (1, "a"): 1,
                (1, "b"): 0,
            },
            start_state=0,
            accept_states={1},
        )
        dfa2 = DFA(
            state_names={"X", "Y"},
            alphabet={"a", "b"},
            transitions={
                ("X", "a"): "Y",
                ("X", "b"): "X",
                ("Y", "a"): "Y",
                ("Y", "b"): "X",
            },
            start_state="X",
            accept_states={"Y"},
        )
        self.assertTrue(are_isomorphic(dfa1, dfa2))

    def test_isomorphism_negative(self):
        """Two DFAs for different languages are not isomorphic."""
        # DFA1: accepts strings ending in 'a'
        dfa1 = DFA(
            state_names={0, 1},
            alphabet={"a", "b"},
            transitions={
                (0, "a"): 1,
                (0, "b"): 0,
                (1, "a"): 1,
                (1, "b"): 0,
            },
            start_state=0,
            accept_states={1},
        )
        # DFA2: accepts strings ending in 'b'
        dfa2 = DFA(
            state_names={0, 1},
            alphabet={"a", "b"},
            transitions={
                (0, "a"): 0,
                (0, "b"): 1,
                (1, "a"): 0,
                (1, "b"): 1,
            },
            start_state=0,
            accept_states={1},
        )
        self.assertFalse(are_isomorphic(dfa1, dfa2))


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for Lazy Subset Construction algorithm.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Algoritms.lazy_subset import determinize_lazy
from Algoritms.sub_set import determinize_nfa
from Algoritms.class_dfa_nfa import NFA
from Analize.mocks.nfa import nfa_1, nfa_2, nfa_3, nfa_4, nfa_5
from Tests_Diagram.nfa_generators import gen_nth_from_last, gen_dense_random, gen_sparse_nfa

from unit_tests.helpers.dfa_helpers import run_dfa, run_nfa, gen_random_words, gen_systematic_words
from unit_tests.helpers.equivalence import check_language_equivalence_by_words


class TestLazySubset(unittest.TestCase):

    def _determinize(self, nfa):
        return determinize_lazy(nfa)

    def test_returns_dfa_and_count(self):
        """Algorithm returns (DFA, int) tuple."""
        nfa = gen_nth_from_last(3)
        result = self._determinize(nfa)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        dfa, count = result
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)

    def test_dfa_has_valid_structure(self):
        """DFA has valid states, start, accept, transitions."""
        nfa = gen_nth_from_last(3)
        dfa, _ = self._determinize(nfa)

        self.assertIn(dfa.start_state, dfa.states)
        self.assertTrue(dfa.accept_states.issubset(dfa.states))
        for (state, sym), target in dfa.transitions.items():
            self.assertIn(state, dfa.states)
            self.assertIn(target, dfa.states)
            self.assertIn(sym, dfa.alphabet)

    def test_dfa_is_deterministic(self):
        """Each (state, symbol) maps to exactly one state."""
        nfa = gen_nth_from_last(4)
        dfa, _ = self._determinize(nfa)

        for (state, sym), target in dfa.transitions.items():
            self.assertNotIsInstance(target, (set, frozenset, list))

    def test_language_equivalence_predefined_nfa1(self):
        """Lazy DFA accepts same language as nfa_1."""
        dfa, _ = self._determinize(nfa_1)
        ok, mismatches = check_language_equivalence_by_words(nfa_1, dfa)
        self.assertTrue(ok, f"Mismatches: {mismatches[:5]}")

    def test_language_equivalence_predefined_nfa2(self):
        """Lazy DFA accepts same language as nfa_2."""
        dfa, _ = self._determinize(nfa_2)
        ok, mismatches = check_language_equivalence_by_words(nfa_2, dfa)
        self.assertTrue(ok, f"Mismatches: {mismatches[:5]}")

    def test_language_equivalence_predefined_nfa3(self):
        """Lazy DFA accepts same language as nfa_3."""
        dfa, _ = self._determinize(nfa_3)
        ok, mismatches = check_language_equivalence_by_words(nfa_3, dfa)
        self.assertTrue(ok, f"Mismatches: {mismatches[:5]}")

    def test_language_equivalence_random_dense(self):
        """Lazy DFA accepts same language as a random dense NFA."""
        nfa = gen_dense_random(15, {"a", "b", "c"}, 0.15)
        dfa, _ = self._determinize(nfa)
        ok, mismatches = check_language_equivalence_by_words(nfa, dfa)
        self.assertTrue(ok, f"Mismatches: {mismatches[:5]}")

    def test_language_equivalence_random_sparse(self):
        """Lazy DFA accepts same language as a random sparse NFA."""
        nfa = gen_sparse_nfa(20, {"0", "1"}, 0.1)
        dfa, _ = self._determinize(nfa)
        ok, mismatches = check_language_equivalence_by_words(nfa, dfa)
        self.assertTrue(ok, f"Mismatches: {mismatches[:5]}")

    def test_alphabet_preserved(self):
        """DFA alphabet matches NFA alphabet."""
        nfa = gen_nth_from_last(3)
        dfa, _ = self._determinize(nfa)
        nfa_alpha = {sym for sym in nfa.alphabet if sym != ""}
        dfa_alpha = {sym for sym in dfa.alphabet if sym != ""}
        self.assertEqual(nfa_alpha, dfa_alpha)

    def test_same_dfa_size_as_subset(self):
        """Lazy produces same number of DFA states as standard Subset Construction."""
        for n in [3, 4, 5]:
            with self.subTest(n=n):
                nfa = gen_nth_from_last(n)
                dfa_lazy, _ = self._determinize(nfa)
                dfa_subset, _ = determinize_nfa(nfa)
                self.assertEqual(
                    len(dfa_lazy.states),
                    len(dfa_subset.states),
                    f"n={n}: Lazy={len(dfa_lazy.states)} vs Subset={len(dfa_subset.states)}",
                )


if __name__ == "__main__":
    unittest.main()

"""
Word-based language equivalence tests — NFA vs DFA.

Each test generates random + systematic words, runs them through both the
original NFA and the determinized DFA, and verifies the acceptance verdict
matches on every word.

This is a complementary check to the isomorphism-based tests. On its own
it gives statistical, not formal, confidence (finite sample of an infinite
language) — but it provides clearer diagnostic messages and intuitive
verification that determinization preserves language semantics.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Algoritms_with_epsilon.sub_set_epsilon import determinize_nfa_epsilon
from Algoritms_with_epsilon.brzozowski_epsilon import determinize_brz_epsilon
from Algoritms_with_epsilon.transset_epsilon import determinize_transset_epsilon
from Analize.mocks.nfa import (
    nfa_1, nfa_2, nfa_3, nfa_4, nfa_5,
    nfa_large_1, nfa_large_2, nfa_large_3,
    nfa_epsilon,
)
from Tests_Diagram.nfa_generators import (
    gen_nth_from_last, gen_dense_random, gen_sparse_nfa, gen_epsilon_chain,
)

from unit_tests.helpers.equivalence import check_language_equivalence_by_words


BASE_ALGORITHMS = [
    ("Subset", determinize_nfa),
    ("Brzozowski", determinize_brz),
    ("Transset", determinize_transset),
]

EPSILON_ALGORITHMS = [
    ("SubsetEps", determinize_nfa_epsilon),
    ("BrzEps", determinize_brz_epsilon),
    ("TranssetEps", determinize_transset_epsilon),
]


class TestWordEquivalenceBase(unittest.TestCase):
    """For each algorithm, verify DFA accepts the same words as the NFA."""

    def _assert_word_equivalent(self, nfa, label):
        for name, func in BASE_ALGORITHMS:
            with self.subTest(algorithm=name):
                dfa, _ = func(nfa)
                ok, mismatches = check_language_equivalence_by_words(nfa, dfa)
                self.assertTrue(
                    ok,
                    f"{label}/{name}: {len(mismatches)} mismatched words "
                    f"(first 5: {mismatches[:5]})",
                )

    def test_predefined_nfas(self):
        """Predefined NFAs nfa_1..nfa_5."""
        for i, nfa in enumerate([nfa_1, nfa_2, nfa_3, nfa_4, nfa_5], 1):
            with self.subTest(nfa=f"nfa_{i}"):
                self._assert_word_equivalent(nfa, f"nfa_{i}")

    def test_large_predefined_nfas(self):
        """Large predefined NFAs."""
        for i, nfa in enumerate([nfa_large_1, nfa_large_2, nfa_large_3], 1):
            with self.subTest(nfa=f"nfa_large_{i}"):
                self._assert_word_equivalent(nfa, f"nfa_large_{i}")

    def test_nth_from_last_family(self):
        """nth-from-last family (exponential blowup)."""
        for n in range(2, 6):
            with self.subTest(n=n):
                self._assert_word_equivalent(gen_nth_from_last(n), f"nth_from_last({n})")

    def test_dense_random(self):
        """Random dense NFAs."""
        for i in range(3):
            with self.subTest(i=i):
                nfa = gen_dense_random(12, {"a", "b"}, 0.15)
                self._assert_word_equivalent(nfa, f"dense_{i}")

    def test_sparse_random(self):
        """Random sparse NFAs."""
        for i in range(3):
            with self.subTest(i=i):
                nfa = gen_sparse_nfa(20, {"0", "1"}, 0.1)
                self._assert_word_equivalent(nfa, f"sparse_{i}")


class TestWordEquivalenceEpsilon(unittest.TestCase):
    """Word equivalence for epsilon-NFA algorithms."""

    def _assert_word_equivalent(self, nfa, label):
        for name, func in EPSILON_ALGORITHMS:
            with self.subTest(algorithm=name):
                dfa, _ = func(nfa)
                ok, mismatches = check_language_equivalence_by_words(nfa, dfa)
                self.assertTrue(
                    ok,
                    f"{label}/{name}: {len(mismatches)} mismatched words "
                    f"(first 5: {mismatches[:5]})",
                )

    def test_predefined_epsilon_nfa(self):
        """Predefined nfa_epsilon."""
        self._assert_word_equivalent(nfa_epsilon, "nfa_epsilon")

    def test_epsilon_chain_small(self):
        """Small epsilon-chain NFA."""
        self._assert_word_equivalent(gen_epsilon_chain(15, 5), "epsilon_chain(15,5)")

    def test_epsilon_chain_heavy(self):
        """Heavy epsilon-chain NFA."""
        self._assert_word_equivalent(gen_epsilon_chain(30, 15), "epsilon_chain(30,15)")


if __name__ == "__main__":
    unittest.main()

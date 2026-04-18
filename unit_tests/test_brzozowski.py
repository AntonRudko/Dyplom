"""
Unit tests for Brzozowski's algorithm — validated via minimization + isomorphism
against Subset Construction (the reference implementation).

Every test gives a 100% correctness guarantee (Myhill-Nerode theorem).
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Algoritms.brzozowski import determinize_brz
from Algoritms.sub_set import determinize_nfa
from Analize.mocks.nfa import (
    nfa_1, nfa_2, nfa_3, nfa_4, nfa_5,
    nfa_large_1, nfa_large_2, nfa_large_3,
)
from Tests_Diagram.nfa_generators import (
    gen_nth_from_last, gen_dense_random, gen_sparse_nfa,
)

from unit_tests.helpers.equivalence import check_dfa_equivalence_by_minimization


class TestBrzozowskiEquivalence(unittest.TestCase):
    """Brzozowski must produce DFAs equivalent to Subset Construction."""

    def _assert_equivalent(self, nfa, label):
        subset_dfa, _ = determinize_nfa(nfa)
        brz_dfa, _ = determinize_brz(nfa)
        self.assertTrue(
            check_dfa_equivalence_by_minimization(subset_dfa, brz_dfa),
            f"{label}: Brzozowski DFA not equivalent to Subset DFA",
        )

    def test_predefined_nfas(self):
        """Equivalence on predefined NFAs nfa_1..nfa_5."""
        for i, nfa in enumerate([nfa_1, nfa_2, nfa_3, nfa_4, nfa_5], 1):
            with self.subTest(nfa=f"nfa_{i}"):
                self._assert_equivalent(nfa, f"nfa_{i}")

    def test_large_predefined_nfas(self):
        """Equivalence on large predefined NFAs."""
        for i, nfa in enumerate([nfa_large_1, nfa_large_2, nfa_large_3], 1):
            with self.subTest(nfa=f"nfa_large_{i}"):
                self._assert_equivalent(nfa, f"nfa_large_{i}")

    def test_nth_from_last_family(self):
        """Equivalence on nth-from-last NFAs (exponential blowup family)."""
        for n in range(2, 6):
            with self.subTest(n=n):
                self._assert_equivalent(gen_nth_from_last(n), f"nth_from_last({n})")

    def test_dense_random(self):
        """Equivalence on randomly generated dense NFAs."""
        for i in range(3):
            with self.subTest(i=i):
                nfa = gen_dense_random(12, {"a", "b"}, 0.15)
                self._assert_equivalent(nfa, f"dense_random_{i}")

    def test_sparse_random(self):
        """Equivalence on randomly generated sparse NFAs."""
        for i in range(3):
            with self.subTest(i=i):
                nfa = gen_sparse_nfa(20, {"0", "1"}, 0.1)
                self._assert_equivalent(nfa, f"sparse_{i}")


if __name__ == "__main__":
    unittest.main()

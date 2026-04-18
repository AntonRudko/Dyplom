"""
Cross-algorithm pairwise equivalence tests.

Verifies that all determinization algorithms produce pairwise-equivalent
DFAs for a variety of NFA types, using minimization + isomorphism.

This provides a 100% correctness guarantee via the Myhill-Nerode theorem:
two DFAs accept the same language iff their minimal forms are isomorphic.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset
from Analize.mocks.nfa import (
    nfa_1, nfa_2, nfa_3, nfa_4, nfa_5,
    nfa_large_1, nfa_large_2, nfa_large_3, nfa_large_4, nfa_large_5,
)
from Tests_Diagram.nfa_generators import (
    gen_nth_from_last, gen_dense_random, gen_sparse_nfa, gen_multi_branch,
)

from unit_tests.helpers.equivalence import check_dfa_equivalence_by_minimization


ALGORITHMS = [
    ("Subset", determinize_nfa),
    ("Brzozowski", determinize_brz),
    ("Transset", determinize_transset),
]


class TestCrossAlgorithmEquivalence(unittest.TestCase):
    """All pairs of algorithms must produce isomorphic minimal DFAs."""

    def _check_all_pairwise_isomorphic(self, nfa, label):
        """Run all algorithms and verify pairwise minimal-DFA isomorphism."""
        dfas = [(name, func(nfa)[0]) for name, func in ALGORITHMS]

        for i in range(len(dfas)):
            for j in range(i + 1, len(dfas)):
                name_i, dfa_i = dfas[i]
                name_j, dfa_j = dfas[j]
                self.assertTrue(
                    check_dfa_equivalence_by_minimization(dfa_i, dfa_j),
                    f"{label}: {name_i} and {name_j} produce non-equivalent DFAs",
                )

    def test_predefined_nfas(self):
        """All predefined NFAs produce pairwise-equivalent DFAs."""
        for i, nfa in enumerate([nfa_1, nfa_2, nfa_3, nfa_4, nfa_5], 1):
            with self.subTest(nfa=f"nfa_{i}"):
                self._check_all_pairwise_isomorphic(nfa, f"nfa_{i}")

    def test_large_predefined_nfas(self):
        """Large predefined NFAs produce pairwise-equivalent DFAs."""
        for i, nfa in enumerate(
            [nfa_large_1, nfa_large_2, nfa_large_3, nfa_large_4, nfa_large_5], 1
        ):
            with self.subTest(nfa=f"nfa_large_{i}"):
                self._check_all_pairwise_isomorphic(nfa, f"nfa_large_{i}")

    def test_nth_from_last_family(self):
        """nth-from-last family (n=2..6) — classic exponential blowup."""
        for n in range(2, 7):
            with self.subTest(n=n):
                self._check_all_pairwise_isomorphic(
                    gen_nth_from_last(n), f"nth_from_last({n})"
                )

    def test_dense_random_nfas(self):
        """Random dense NFAs produce pairwise-equivalent DFAs."""
        for i in range(5):
            with self.subTest(i=i):
                nfa = gen_dense_random(12, {"a", "b"}, 0.15)
                self._check_all_pairwise_isomorphic(nfa, f"dense_{i}")

    def test_sparse_random_nfas(self):
        """Random sparse NFAs produce pairwise-equivalent DFAs."""
        for i in range(5):
            with self.subTest(i=i):
                nfa = gen_sparse_nfa(20, {"0", "1"}, 0.1)
                self._check_all_pairwise_isomorphic(nfa, f"sparse_{i}")

    def test_multi_branch_nfas(self):
        """Multi-branch NFAs produce pairwise-equivalent DFAs."""
        for n, k in [(3, 2), (3, 3), (4, 2)]:
            with self.subTest(n=n, k=k):
                self._check_all_pairwise_isomorphic(
                    gen_multi_branch(n, k), f"branch({n},{k})"
                )


if __name__ == "__main__":
    unittest.main()

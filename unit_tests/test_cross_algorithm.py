"""
Cross-algorithm equivalence tests — the key test file.

Verifies that all 4 determinization algorithms produce equivalent DFAs
for a variety of NFA types.
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
from Analize.mocks.nfa import (
    nfa_1, nfa_2, nfa_3, nfa_4, nfa_5,
    nfa_large_1, nfa_large_2, nfa_large_3, nfa_large_4, nfa_large_5,
)
from Tests_Diagram.nfa_generators import (
    gen_nth_from_last, gen_dense_random, gen_sparse_nfa, gen_multi_branch,
)

from unit_tests.helpers.dfa_helpers import run_dfa, run_nfa, gen_random_words, gen_systematic_words
from unit_tests.helpers.equivalence import (
    check_language_equivalence_by_words,
    check_dfa_equivalence_by_minimization,
)


ALGORITHMS = [
    ("Subset", determinize_nfa),
    ("Brzozowski", determinize_brz),
    ("Transset", determinize_transset),
    ("Lazy", determinize_lazy),
]


class TestCrossAlgorithm(unittest.TestCase):

    def _check_all_equivalent(self, nfa, label=""):
        """Run all algorithms and check all DFAs are word-equivalent."""
        dfas = []
        for name, func in ALGORITHMS:
            dfa, _ = func(nfa)
            dfas.append((name, dfa))

        # Check each DFA against NFA
        for name, dfa in dfas:
            ok, mismatches = check_language_equivalence_by_words(nfa, dfa)
            self.assertTrue(ok, f"{label}/{name} mismatches: {mismatches[:5]}")

        # Cross-check DFAs agree on words
        words = gen_random_words(nfa.alphabet, count=200, max_len=15)
        words += gen_systematic_words(nfa.alphabet, max_len=3)
        words = list(set(words))

        for word in words:
            results = {name: run_dfa(dfa, word) for name, dfa in dfas}
            values = list(results.values())
            self.assertTrue(
                all(v == values[0] for v in values),
                f"{label}: disagreement on '{word}': {results}",
            )

    def test_predefined_nfas(self):
        """All predefined NFAs produce equivalent DFAs across all algorithms."""
        for i, nfa in enumerate([nfa_1, nfa_2, nfa_3, nfa_4, nfa_5], 1):
            with self.subTest(nfa=f"nfa_{i}"):
                self._check_all_equivalent(nfa, f"nfa_{i}")

    def test_large_predefined_nfas(self):
        """Large predefined NFAs produce equivalent DFAs."""
        for i, nfa in enumerate(
            [nfa_large_1, nfa_large_2, nfa_large_3, nfa_large_4, nfa_large_5], 1
        ):
            with self.subTest(nfa=f"nfa_large_{i}"):
                self._check_all_equivalent(nfa, f"nfa_large_{i}")

    def test_nth_from_last_family(self):
        """nth-from-last NFAs n=2..6 produce equivalent DFAs."""
        for n in range(2, 7):
            with self.subTest(n=n):
                nfa = gen_nth_from_last(n)
                self._check_all_equivalent(nfa, f"nth_from_last({n})")

    def test_dense_random_nfas(self):
        """5 random dense NFAs produce equivalent DFAs."""
        for i in range(5):
            with self.subTest(i=i):
                nfa = gen_dense_random(12, {"a", "b"}, 0.15)
                self._check_all_equivalent(nfa, f"dense_{i}")

    def test_sparse_nfas(self):
        """5 sparse NFAs produce equivalent DFAs."""
        for i in range(5):
            with self.subTest(i=i):
                nfa = gen_sparse_nfa(20, {"0", "1"}, 0.1)
                self._check_all_equivalent(nfa, f"sparse_{i}")

    def test_multi_branch(self):
        """Multi-branch NFAs produce equivalent DFAs."""
        for n, k in [(3, 2), (3, 3), (4, 2)]:
            with self.subTest(n=n, k=k):
                nfa = gen_multi_branch(n, k)
                self._check_all_equivalent(nfa, f"branch({n},{k})")

    def test_minimized_dfas_isomorphic(self):
        """Minimized DFAs from all algorithms are isomorphic."""
        nfa = gen_nth_from_last(4)
        dfas = [(name, func(nfa)[0]) for name, func in ALGORITHMS]

        for i in range(len(dfas)):
            for j in range(i + 1, len(dfas)):
                name_i, dfa_i = dfas[i]
                name_j, dfa_j = dfas[j]
                iso = check_dfa_equivalence_by_minimization(dfa_i, dfa_j)
                self.assertTrue(
                    iso,
                    f"Minimized {name_i} and {name_j} are not isomorphic",
                )

    def test_systematic_small_nfa(self):
        """Exhaustive word check up to length 5 on small NFA."""
        nfa = gen_nth_from_last(3)
        dfas = [(name, func(nfa)[0]) for name, func in ALGORITHMS]

        words = gen_systematic_words(nfa.alphabet, max_len=5)

        for word in words:
            nfa_result = run_nfa(nfa, word)
            for name, dfa in dfas:
                dfa_result = run_dfa(dfa, word)
                self.assertEqual(
                    nfa_result,
                    dfa_result,
                    f"{name}: word '{word}' NFA={nfa_result} DFA={dfa_result}",
                )


if __name__ == "__main__":
    unittest.main()

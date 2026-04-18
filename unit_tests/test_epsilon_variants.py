"""
Unit tests for epsilon-transition algorithm variants — validated via
minimization + isomorphism against SubsetEps (the reference).

Every test gives a 100% correctness guarantee (Myhill-Nerode theorem).
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Algoritms.class_dfa_nfa import NFA
from Algoritms_with_epsilon.sub_set_epsilon import determinize_nfa_epsilon
from Algoritms_with_epsilon.brzozowski_epsilon import determinize_brz_epsilon
from Algoritms_with_epsilon.transset_epsilon import determinize_transset_epsilon
from Analize.mocks.nfa import nfa_epsilon
from Tests_Diagram.nfa_generators import gen_epsilon_chain

from unit_tests.helpers.equivalence import check_dfa_equivalence_by_minimization


NON_REFERENCE_EPSILON_ALGORITHMS = [
    ("BrzEps", determinize_brz_epsilon),
    ("TranssetEps", determinize_transset_epsilon),
]


class TestEpsilonVariantsEquivalence(unittest.TestCase):
    """All epsilon algorithms must agree with SubsetEps on minimal DFA."""

    def _check_all_equivalent_to_subset_eps(self, nfa, label):
        subset_dfa, _ = determinize_nfa_epsilon(nfa)
        for name, func in NON_REFERENCE_EPSILON_ALGORITHMS:
            with self.subTest(algorithm=name):
                other_dfa, _ = func(nfa)
                self.assertTrue(
                    check_dfa_equivalence_by_minimization(subset_dfa, other_dfa),
                    f"{label}/{name}: not equivalent to SubsetEps",
                )

    def test_predefined_epsilon_nfa(self):
        """Predefined nfa_epsilon — all algorithms agree."""
        self._check_all_equivalent_to_subset_eps(nfa_epsilon, "nfa_epsilon")

    def test_epsilon_chain_small(self):
        """Small epsilon-chain NFA — all algorithms agree."""
        nfa = gen_epsilon_chain(15, 5)
        self._check_all_equivalent_to_subset_eps(nfa, "epsilon_chain(15,5)")

    def test_epsilon_chain_heavy(self):
        """Heavy epsilon-chain NFA — all algorithms agree."""
        nfa = gen_epsilon_chain(30, 15)
        self._check_all_equivalent_to_subset_eps(nfa, "epsilon_chain(30,15)")

    def test_epsilon_only_nfa(self):
        """NFA with only epsilon transitions (accepts only empty word)."""
        nfa = NFA(
            states={"q0", "q1"},
            alphabet={"a", ""},
            transitions={("q0", ""): {"q1"}},
            start_state="q0",
            accept_states={"q1"},
        )
        self._check_all_equivalent_to_subset_eps(nfa, "epsilon_only")


if __name__ == "__main__":
    unittest.main()

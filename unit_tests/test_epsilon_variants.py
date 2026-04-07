"""
Unit tests for epsilon-transition algorithm variants.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Algoritms.class_dfa_nfa import NFA
from Algoritms_with_epsilon.sub_set_epsilon import determinize_nfa_epsilon
from Algoritms_with_epsilon.brzozowski_epsilon import determinize_brz_epsilon
from Algoritms_with_epsilon.transset_epsilon import determinize_transset_epsilon
from Algoritms_with_epsilon.qsc_epsilon import determinize_qsc_epsilon
from Analize.mocks.nfa import nfa_epsilon
from Tests_Diagram.nfa_generators import gen_epsilon_chain

from unit_tests.helpers.dfa_helpers import run_dfa, run_nfa, gen_random_words, gen_systematic_words
from unit_tests.helpers.equivalence import check_language_equivalence_by_words


class TestEpsilonVariants(unittest.TestCase):

    EPSILON_ALGORITHMS = [
        ("SubsetEps", determinize_nfa_epsilon),
        ("BrzEps", determinize_brz_epsilon),
        ("TranssetEps", determinize_transset_epsilon),
        ("QSCEps", determinize_qsc_epsilon),
    ]

    def test_predefined_epsilon_nfa_all_algorithms(self):
        """All epsilon algorithms produce equivalent DFAs for nfa_epsilon."""
        results = {}
        for name, func in self.EPSILON_ALGORITHMS:
            dfa, _ = func(nfa_epsilon)
            ok, mismatches = check_language_equivalence_by_words(nfa_epsilon, dfa)
            results[name] = ok
            self.assertTrue(ok, f"{name} mismatches: {mismatches[:5]}")

        # Cross-check: all DFAs agree on words
        dfas = [(name, func(nfa_epsilon)[0]) for name, func in self.EPSILON_ALGORITHMS]
        words = gen_systematic_words(nfa_epsilon.alphabet, max_len=5)
        for word in words:
            accepts = {name: run_dfa(dfa, word) for name, dfa in dfas}
            values = list(accepts.values())
            self.assertTrue(
                all(v == values[0] for v in values),
                f"Disagreement on word '{word}': {accepts}",
            )

    def test_epsilon_chain_all_algorithms(self):
        """All epsilon algorithms handle epsilon chains correctly."""
        nfa = gen_epsilon_chain(15, 5)
        for name, func in self.EPSILON_ALGORITHMS:
            dfa, _ = func(nfa)
            ok, mismatches = check_language_equivalence_by_words(nfa, dfa)
            self.assertTrue(ok, f"{name} mismatches on epsilon_chain: {mismatches[:5]}")

    def test_dfa_alphabet_no_epsilon(self):
        """DFA alphabet does not contain epsilon (empty string)."""
        nfa = nfa_epsilon
        for name, func in self.EPSILON_ALGORITHMS:
            dfa, _ = func(nfa)
            self.assertNotIn("", dfa.alphabet, f"{name}: DFA alphabet contains epsilon")

    def test_epsilon_only_nfa(self):
        """NFA with only epsilon transitions (accepts only empty word)."""
        # NFA: q0 -eps-> q1 (accepting). Accepts only "".
        nfa = NFA(
            states={"q0", "q1"},
            alphabet={"a", ""},
            transitions={("q0", ""): {"q1"}},
            start_state="q0",
            accept_states={"q1"},
        )
        for name, func in self.EPSILON_ALGORITHMS:
            dfa, _ = func(nfa)
            self.assertTrue(
                run_dfa(dfa, ""),
                f"{name}: should accept empty word",
            )
            self.assertFalse(
                run_dfa(dfa, "a"),
                f"{name}: should reject 'a'",
            )
            self.assertFalse(
                run_dfa(dfa, "aa"),
                f"{name}: should reject 'aa'",
            )

    def test_heavy_epsilon_chain(self):
        """Large epsilon chain with many epsilon transitions."""
        nfa = gen_epsilon_chain(30, 15)
        for name, func in self.EPSILON_ALGORITHMS:
            dfa, _ = func(nfa)
            ok, mismatches = check_language_equivalence_by_words(nfa, dfa)
            self.assertTrue(ok, f"{name} mismatches on heavy epsilon: {mismatches[:5]}")


if __name__ == "__main__":
    unittest.main()

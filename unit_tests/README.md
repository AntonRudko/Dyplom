# Unit Tests for NFA-to-DFA Determinization Algorithms

## Structure

```
unit_tests/
  helpers/
    dfa_helpers.py         # run_dfa, run_nfa (with epsilon), word generation
    minimization.py        # DFA minimization (partition refinement)
    isomorphism.py         # DFA isomorphism check (BFS bijection)
    equivalence.py         # High-level equivalence checks
  test_subset.py           # Subset Construction tests
  test_brzozowski.py       # Brzozowski algorithm tests
  test_transset.py         # Transset algorithm tests
  test_qsc.py              # Quick Subset Construction tests
  test_lazy.py             # Lazy Subset Construction tests
  test_epsilon_variants.py # Epsilon-transition algorithm tests
  test_cross_algorithm.py  # Cross-algorithm equivalence (key file)
  test_edge_cases.py       # Edge cases (single state, no transitions, etc.)
  test_minimization.py     # Minimization & isomorphism tests
```

## Helpers

### `dfa_helpers.py`
- `run_dfa(dfa, word)` — deterministic word execution
- `run_nfa(nfa, word)` — NFA execution **with epsilon-closure** (BFS)
- `gen_random_words(alphabet, count, max_len)` — random test words
- `gen_systematic_words(alphabet, max_len)` — all words up to given length

### `minimization.py`
- `minimize_dfa(dfa)` — Hopcroft-style partition refinement:
  1. BFS for reachable states
  2. Dead state for totality
  3. Partition refinement until stable
  4. Build minimal DFA
  5. Remove dead state (compatible with partial DFA outputs)

### `isomorphism.py`
- `are_isomorphic(dfa1, dfa2)` — BFS bijection construction between states

### `equivalence.py`
- `check_language_equivalence_by_words(nfa, dfa)` — word-based check
- `check_dfa_equivalence_by_minimization(dfa1, dfa2)` — minimize + isomorphism
- `check_all_algorithms_equivalent(nfa, algorithms)` — run all + both checks

## Test Coverage

| File | Tests | Description |
|------|-------|-------------|
| `test_subset.py` | 9 | Subset Construction: structure, determinism, language, blowup |
| `test_brzozowski.py` | 8 | Brzozowski: structure, language, minimality |
| `test_transset.py` | 8 | Transset: structure, language, dead states |
| `test_qsc.py` | 8 | QSC: structure, language, singularities |
| `test_lazy.py` | 10 | Lazy Subset: structure, language, equivalence with Subset |
| `test_epsilon_variants.py` | 5 | All 5 epsilon algorithms, epsilon-only NFA |
| `test_cross_algorithm.py` | 8 | Cross-algorithm equivalence (all 5), isomorphism |
| `test_edge_cases.py` | 8 | Single state, no transitions, unreachable, etc. (all 5) |
| `test_minimization.py` | 6 | Minimization correctness, isomorphism properties |

**Total: ~70 tests**

## How to Run

```bash
# From Dyplom_Top directory:
python -m unittest discover -s unit_tests -p "test_*.py" -v

# Run a specific test file:
python -m unittest unit_tests.test_cross_algorithm -v

# Run a specific test:
python -m unittest unit_tests.test_subset.TestSubsetConstruction.test_nth_from_last_exponential_blowup -v
```

## Algorithms Under Test

### Without Epsilon
- **Subset Construction** (`Algoritms/sub_set.py`) — standard power set construction
- **Brzozowski** (`Algoritms/brzozowski.py`) — double reversal + determinization
- **Transset** (`Algoritms/transset.py`) — behavioral signature merging
- **QSC** (`Algoritms/quick_subset.py`) — preserves deterministic parts
- **Lazy Subset** (`Algoritms/lazy_subset.py`) — on-demand transition caching (DFS)

### With Epsilon
- **Subset + epsilon** (`Algoritms_with_epsilon/sub_set_epsilon.py`)
- **Brzozowski + epsilon** (`Algoritms_with_epsilon/brzozowski_epsilon.py`)
- **Transset + epsilon** (`Algoritms_with_epsilon/transset_epsilon.py`)
- **QSC + epsilon** (`Algoritms_with_epsilon/quick_subset_epsilon.py`)
- **Lazy + epsilon** (`Algoritms_with_epsilon/lazy_subset_epsilon.py`)

## NFA Sources
- **Predefined:** `Analize/nfa.py` (nfa_1..5, nfa_large_1..5, nfa_epsilon)
- **Generators:** `Tests/nfa_generators.py` (nth_from_last, dense, sparse, branch, epsilon_chain)
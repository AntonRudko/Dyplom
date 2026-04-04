# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Diploma project: comparative analysis of NFA-to-DFA determinization algorithms. Implements and benchmarks 4 algorithms (with and without epsilon-transitions).

## Commands

```bash
# Main demo (transition tables, graphs)
python main.py

# Visual correctness (language equivalence + isomorphism)
python visual_correctness.py

# Test results summary table (PNG)
python generate_test_table.py

# All benchmark tests (base algorithms)
python -m Tests_Diagram.run_all

# All benchmark tests (epsilon variants)
python -m Tests_Diagram.run_all_epsilon

# Single benchmark test
python -m Tests_Diagram.test2_density_impact

# All unit tests
python -m unittest discover -s unit_tests -p "test_*.py" -v

# Single unit test file
python -m unittest unit_tests.test_subset -v

# Heatmap comparison
python -m Tests_Diagram.heatmap_comparison
```

## Dependencies

- Python 3.10+
- `matplotlib`, `numpy`, `graphviz`

## Architecture

### Core Data Structures (`Algoritms/class_dfa_nfa.py`)

```python
NFA: states, alphabet, transitions {(state, symbol): set}, start_state, accept_states
DFA: states, alphabet, transitions {(state, symbol): state}, start_state, accept_states
```

### Algorithm Interface

Every algorithm follows this signature:
```python
def determinize_*(nfa: NFA) -> (DFA, int)
```
The second return value is an algorithm-specific operation count (e.g., `subsets_processed`, `merges_count`, `transitions_computed`).

### Algorithms (`Algoritms/`)

| File | Function | Operation metric |
|------|----------|-----------------|
| `sub_set.py` | `determinize_nfa` | `subsets_processed` |
| `brzozowski.py` | `determinize_brz` | `total_iterations` |
| `transset.py` | `determinize_transset` | `merges_count` |
| `lazy_subset.py` | `determinize_lazy` | `transitions_computed` |

Epsilon variants in `Algoritms_with_epsilon/` mirror the same interface, using `epsilon_closure.py` for closure computation.

### Test NFA Library (`Analize/mocks/nfa.py`)

Predefined NFAs: `nfa_1`..`nfa_5`, `nfa_large_1`..`nfa_large_5`, `nfa_test1`, `nfa_test2`, `nfa_epsilon`, `nfa_15_states`. Imported by `main.py`, unit tests, and visualization scripts.

### Test Words (`Analize/mocks/words.py`)

Static word sets for manual verification: `words`, `words_1`..`words_5`.

### Visualization Tools (`Analize/tools/`)

- `graph_visualizer.py` — Graphviz-based automaton graph generation (PNG)
- `table_visualizer.py` — matplotlib-based transition table generation (PNG)
- `word_check.py` — word acceptance testing (`run_dfa`, `run_nfa`, `run_words`)

### NFA Generators (`Tests_Diagram/nfa_generators.py`)

Programmatic NFA generation for benchmarks:
- `gen_nth_from_last(n)` — worst-case exponential blowup
- `gen_dense_random(states, alphabet, density)`
- `gen_sparse_nfa(states, alphabet, density)`
- `gen_multi_branch`, `gen_epsilon_chain`, `gen_variable_alphabet`, `gen_variable_nondet`

### Unit Tests (`unit_tests/`)

65 tests across 8 test files. Helpers in `unit_tests/helpers/`: `dfa_helpers.py`, `equivalence.py`, `minimization.py`, `isomorphism.py`. Test files: `test_subset`, `test_transset`, `test_brzozowski`, `test_lazy`, `test_minimization`, `test_cross_algorithm`, `test_edge_cases`, `test_epsilon_variants`.

### Root Scripts

- `main.py` — generates transition tables and automaton graphs for all algorithms
- `generate_test_table.py` — runs 16 test categories across 8 algorithm variants, generates color-coded PNG matrix (`Outputs/test_results_table.png`)
- `visual_correctness.py` — language equivalence verification + structural isomorphism analysis with graph/matrix visualizations (`Outputs/Visual_Correctness/`)

### Outputs

- `Outputs/tables/` — transition table PNGs
- `Outputs/graphs/` — automaton graph PNGs (Graphviz)
- `Outputs/epsilon_tables/`, `Outputs/epsilon_graphs/` — epsilon variants
- `Outputs/Visual_Correctness/` — isomorphism graphs, tables, and matrices
- `Outputs/test_results_table.png` — unit test results summary matrix
- `At_Simple_Tests/Graphs/` — benchmark comparison plots
- `Tests_Diagram/Hitmaps/` — algorithm comparison heatmaps
- `Tests_Diagram/Tests_Diagram/` — base benchmark result graphs
- `Tests_Diagram/Tests_Diagram_Epsilon/` — epsilon benchmark result graphs

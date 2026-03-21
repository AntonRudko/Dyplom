# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Diploma project: comparative analysis of NFA-to-DFA determinization algorithms. Implements and benchmarks 5 algorithms (with and without epsilon-transitions).

## Commands

```bash
# Main demo (transition tables, graphs, benchmark)
python main.py

# All benchmark tests
python -m Tests_Diagram.run_all

# Single benchmark test
python -m Tests_Diagram.test2_density_impact

# All unit tests
python -m unittest discover -s unit_tests -p "test_*.py" -v

# Single unit test file
python -m unittest unit_tests.test_subset -v

# Heatmap comparison
python -m Analize.heatmap_comparison
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

### Test NFA Library (`Analize/nfa.py`)

Predefined NFAs: `nfa_1`..`nfa_5`, `nfa_large_1`..`nfa_large_5`, `nfa_epsilon`, `nfa_test1`. Imported by `main.py` and unit tests.

### NFA Generators (`Tests_Diagram/nfa_generators.py`)

Programmatic NFA generation for benchmarks:
- `gen_nth_from_last(n)` — worst-case exponential blowup
- `gen_dense_random(states, alphabet, density)`
- `gen_sparse_nfa(states, alphabet, density)`
- `gen_multi_branch`, `gen_epsilon_chain`, `gen_variable_alphabet`, `gen_variable_nondet`

### Unit Tests (`unit_tests/`)

Tests run from the `unit_tests/` directory; helpers are imported as `from helpers.*`. The `sys.path` manipulation in each test file adds the project root. Test files cover: `test_subset`, `test_transset`, `test_brzozowski`, `test_lazy`, `test_minimization`, `test_cross_algorithm`, `test_edge_cases`, `test_epsilon_variants`.

### Outputs

- `Table/tables/` — transition table PNGs
- `Table/graphs/` — automaton graph PNGs (Graphviz)
- `Table/epsilon_tables/`, `Table/epsilon_graphs/` — epsilon variants
- `At_Simple_Tests/Graphs/` — benchmark comparison plots

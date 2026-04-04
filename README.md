# Порівняльний аналіз алгоритмів детермінізації НКА

Дипломний проєкт: реалізація, тестування та бенчмаркінг 4-х алгоритмів перетворення НКА в ДКА, включаючи варіанти з epsilon-переходами.

## Структура проєкту

```
Dyplom_Top/
├── Algoritms/                     # Основні алгоритми (4 шт.)
├── Algoritms_with_epsilon/        # Epsilon-варіанти алгоритмів (4 шт.)
├── Analize/                       # Аналіз, візуалізація, моки, бенчмарки
│   ├── mocks/                     #   Предвизначені НКА та тестові слова
│   └── tools/                     #   Візуалізатори та перевірка слів
├── Tests_Diagram/                 # Бенчмарк-тести (8 сценаріїв)
├── unit_tests/                    # Unit-тести (65 тестів)
├── Outputs/                       # Вихідні файли (графи, таблиці, heatmap)
├── At_Simple_Tests/               # Додаткові графіки
├── main.py                        # Точка входу (візуалізація таблиць та графів)
├── generate_test_table.py         # Генерація зведеної таблиці результатів тестів
├── visual_correctness.py          # Візуалізація коректності (ізоморфізм, еквівалентність)
└── difficulties.md                # Теоретичний аналіз алгоритмів
```

## Алгоритми

### Без epsilon (`Algoritms/`)

| Файл | Алгоритм | Опис | Метрика (ops) |
|------|----------|------|---------------|
| `sub_set.py` | Subset Construction | Стандартна побудова підмножин (baseline) | subsets_processed |
| `brzozowski.py` | Brzozowski | Подвійне обернення + детермінізація, дає мінімальний ДКА | total_iterations |
| `transset.py` | Transset | Злиття станів з однаковими поведінковими сигнатурами | merges_count |
| `lazy_subset.py` | Lazy Subset | Лінива детермінізація з кешуванням переходів (DFS замість BFS) | transitions_computed |

### З epsilon (`Algoritms_with_epsilon/`)

Ті ж 4 алгоритми + обчислення epsilon-замикання (`epsilon_closure.py`):

| Файл | Алгоритм |
|------|----------|
| `sub_set_epsilon.py` | Subset Construction + epsilon |
| `brzozowski_epsilon.py` | Brzozowski + epsilon |
| `transset_epsilon.py` | Transset + epsilon |
| `lazy_subset_epsilon.py` | Lazy Subset + epsilon |

### Класи даних (`Algoritms/class_dfa_nfa.py`)

```python
NFA: states, alphabet, transitions {(state, symbol): set}, start_state, accept_states
DFA: states, alphabet, transitions {(state, symbol): state},  start_state, accept_states
```

Кожен алгоритм: `func(nfa) -> (DFA, operation_count)`

## Аналіз та візуалізація (`Analize/`)

| Шлях | Призначення |
|------|-------------|
| `mocks/nfa.py` | Предвизначені тестові НКА (nfa_1..5, nfa_large_1..5, nfa_test1, nfa_test2, nfa_epsilon, nfa_15_states) |
| `mocks/words.py` | Тестові набори слів |
| `tools/graph_visualizer.py` | Граф автомата (Graphviz) |
| `tools/table_visualizer.py` | Таблиця переходів (PNG) |
| `tools/word_check.py` | Перевірка прийняття слів |
| `simple_benchmark.py` | Бенчмарк на випадкових НКА (всі 4 алгоритми) |

## Бенчмарк-тести (`Tests_Diagram/`)

| Файл | Що вимірює |
|------|------------|
| `test1_exponential_blowup.py` | Експоненційний розрив (nth-from-last) |
| `test2_density_impact.py` | Вплив щільності переходів |
| `test3_sparse_nondeterminism.py` | Розріджений недетермінізм |
| `test4_branch_structure.py` | Розгалужені структури |
| `test5_alphabet_size.py` | Розмір алфавіту |
| `test6_epsilon_overhead.py` | Накладні витрати epsilon |
| `test7_nondet_degree.py` | Ступінь недетермінізму |
| `test8_correctness.py` | Коректність (всі алгоритми еквівалентні) |

Всі бенчмарк-тести включають 4 алгоритми (+ epsilon-варіанти в test6, test8).

Генератори НКА (`nfa_generators.py`): `gen_nth_from_last`, `gen_dense_random`, `gen_sparse_nfa`, `gen_multi_branch`, `gen_epsilon_chain`, `gen_variable_alphabet`, `gen_variable_nondet`.

## Unit-тести (`unit_tests/`)

65 тестів: коректність кожного алгоритму, крос-алгоритмова еквівалентність, граничні випадки, мінімізація, ізоморфізм. Детальніше: `unit_tests/README.md`.

## Вихідні файли (`Outputs/`)

```
Outputs/
├── tables/                # Таблиці переходів (НКА та ДКА кожного алгоритму)
├── graphs/                # Графи автоматів
├── epsilon_tables/        # Таблиці для epsilon-автоматів
├── epsilon_graphs/        # Графи для epsilon-автоматів
├── Visual_Correctness/    # Ізоморфізм графів та матриці порівнянь
└── test_results_table.png # Зведена таблиця результатів тестів
```

## Як запускати

```bash
# Основна демонстрація (таблиці, графи)
python main.py

# Візуалізація коректності (еквівалентність мов + ізоморфізм)
python visual_correctness.py

# Генерація зведеної таблиці тестів (PNG)
python generate_test_table.py

# Всі бенчмарк-тести (базові алгоритми)
python -m Tests_Diagram.run_all

# Всі бенчмарк-тести (epsilon-варіанти)
python -m Tests_Diagram.run_all_epsilon

# Окремий бенчмарк-тест
python -m Tests_Diagram.test2_density_impact

# Unit-тести
python -m unittest discover -s unit_tests -p "test_*.py" -v

# Heatmap порівняння
python -m Tests_Diagram.heatmap_comparison
```

## Залежності

- Python 3.10+
- matplotlib
- numpy
- graphviz (для візуалізації графів)

# Карта проекту Dyplom_Top

## Порівняння алгоритмів детермінізації NFA -> DFA

```
Dyplom_Top/
│
├── main.py                          # Точка входу — генерація таблиць переходів та графів
├── generate_test_table.py           # Генерація зведеної PNG-таблиці результатів тестів
├── visual_correctness.py            # Візуалізація коректності (еквівалентність + ізоморфізм)
├── README.md                        # Опис проекту
├── CLAUDE.md                        # Інструкції для Claude Code
├── map.md                           # Ця карта проекту
├── difficulties.md                  # Нотатки про складнощі/проблеми
│
├── Algoritms/                       # Алгоритми детермінізації (без ε-переходів)
│   ├── class_dfa_nfa.py             #   Класи DFA та NFA (структури даних)
│   ├── sub_set.py                   #   Класичний Subset Construction
│   ├── brzozowski.py                #   Алгоритм Бжозовського (подвійна реверсія)
│   ├── transset.py                  #   Transset Construction
│   ├── lazy_subset.py               #   Lazy Subset Construction
│   └── __init__.py
│
├── Algoritms_with_epsilon/          # Ті ж алгоритми, але з підтримкою ε-переходів
│   ├── epsilon_closure.py           #   Функція обчислення ε-замикання
│   ├── sub_set_epsilon.py           #   Subset Construction + ε
│   ├── brzozowski_epsilon.py        #   Бжозовський + ε
│   ├── transset_epsilon.py          #   Transset + ε
│   ├── lazy_subset_epsilon.py       #   Lazy Subset + ε
│   ├── README.md
│   └── __init__.py
│
├── Analize/                         # Аналіз, візуалізація, допоміжні інструменти
│   ├── mocks/                       #   Предвизначені тестові дані
│   │   ├── nfa.py                   #     Тестові НКА (nfa_1..5, nfa_large_1..5, nfa_epsilon та ін.)
│   │   ├── words.py                 #     Набори тестових слів
│   │   └── __init__.py
│   ├── tools/                       #   Візуалізація та перевірка
│   │   ├── graph_visualizer.py      #     Графи автоматів (GraphViz → PNG)
│   │   ├── table_visualizer.py      #     Таблиці переходів (matplotlib → PNG)
│   │   ├── word_check.py            #     Ручна перевірка слів на НКА/ДКА
│   │   └── __init__.py
│   ├── simple_benchmark.py          #   Бенчмарк: час алгоритмів на випадкових НКА
│   ├── README.md
│   └── __init__.py
│
├── Tests_Diagram/                   # Бенчмарк-тести (порівняння продуктивності)
│   ├── nfa_generators.py            #   Генератори спеціальних НКА для бенчмарків
│   ├── run_all.py                   #   Запуск усіх базових бенчмарк-тестів
│   ├── run_all_epsilon.py           #   Запуск усіх epsilon-бенчмарк-тестів
│   ├── heatmap_comparison.py        #   Генерація heatmap-порівнянь (щільність × розмір)
│   ├── heatmap_algorithmic.py       #   Алгоритмічні heatmap-порівняння
│   ├── test1_exponential_blowup.py  #   Тест: експоненційний вибух (n-th from last)
│   ├── test2_density_impact.py      #   Тест: вплив щільності переходів
│   ├── test3_sparse_nondeterminism.py  # Тест: розріджений недетермінізм
│   ├── test4_branch_structure.py    #   Тест: паралельні гілки
│   ├── test5_alphabet_size.py       #   Тест: вплив розміру алфавіту
│   ├── test6_epsilon_overhead.py    #   Тест: overhead від ε-переходів
│   ├── test7_nondet_degree.py       #   Тест: змінний ступінь недетермінізму
│   ├── test8_correctness.py         #   Тест: коректність результатів
│   ├── Hitmaps/                     #   Згенеровані heatmap-зображення
│   ├── Tests_Diagram/               #   Згенеровані графіки базових тестів
│   ├── Tests_Diagram_Epsilon/       #   Згенеровані графіки epsilon-тестів
│   ├── README.md
│   └── __init__.py
│
├── unit_tests/                      # Unit-тести (коректність алгоритмів)
│   ├── helpers/                     #   Допоміжні функції для тестів
│   │   ├── dfa_helpers.py           #     Запуск DFA/NFA на словах, генерація слів
│   │   ├── equivalence.py           #     Перевірка еквівалентності мов
│   │   ├── isomorphism.py           #     Перевірка ізоморфізму DFA
│   │   ├── minimization.py          #     Мінімізація DFA (для порівняння)
│   │   ├── README.md
│   │   └── __init__.py
│   ├── test_subset.py               #   Тести Subset Construction
│   ├── test_brzozowski.py           #   Тести Бжозовського
│   ├── test_transset.py             #   Тести Transset
│   ├── test_lazy.py                 #   Тести Lazy Subset
│   ├── test_cross_algorithm.py      #   Крос-тести (всі алгоритми дають однаковий результат)
│   ├── test_edge_cases.py           #   Граничні випадки
│   ├── test_epsilon_variants.py     #   Тести ε-версій алгоритмів
│   ├── test_minimization.py         #   Тести мінімізації
│   ├── README.md
│   ├── unit_tests.md
│   └── __init__.py
│
├── Outputs/                         # Згенеровані зображення (результати)
│   ├── tables/                      #   Таблиці переходів НКА/ДКА
│   ├── graphs/                      #   Графи автоматів
│   ├── epsilon_tables/              #   Таблиці для ε-варіантів
│   ├── epsilon_graphs/              #   Графи для ε-варіантів
│   ├── Visual_Correctness/          #   Ізоморфізм графів та матриці
│   └── test_results_table.png       #   Зведена таблиця результатів тестів
│
└── At_Simple_Tests/                 # Додаткові графіки бенчмарків
    ├── graphs.py                    #   Скрипт генерації графіків
    └── Graphs/                      #   Згенеровані PNG (час, пам'ять, розмір DFA)
```

## Коротко

- **Algoritms/** — самі алгоритми (4 штуки x 2 версії: з/без ε)
- **Tests_Diagram/** — бенчмарки (вимірюють *швидкість*)
- **unit_tests/** — тести коректності (перевіряють *правильність*)
- **Analize/** — візуалізація + допоміжні НКА/слова + simple benchmark
- **Outputs/** + **At_Simple_Tests/** — згенеровані результати (картинки)

# Карта проекту Dyplom_Top

## Порівняння алгоритмів детермінізації NFA -> DFA

```
Dyplom_Top/
│
├── main.py                          # Точка входу — запуск візуалізацій та бенчмарків
├── README.md                        # Опис проекту
├── difficulties.md                  # Нотатки про складнощі/проблеми
│
├── Algoritms/                       # Алгоритми детермінізації (без ε-переходів)
│   ├── class_dfa_nfa.py             #   Класи DFA та NFA (структури даних)
│   ├── sub_set.py                   #   Класичний Subset Construction
│   ├── quick_subset.py              #   Quick Subset Construction (QSC)
│   ├── brzozowski.py                #   Алгоритм Бжозовського (подвійна реверсія)
│   ├── transset.py                  #   Transset Construction
│   └── lazy_subset.py               #   Lazy Subset Construction
│
├── Algoritms_with_epsilon/          # Ті ж алгоритми, але з підтримкою ε-переходів
│   ├── epsilon_closure.py           #   Функція обчислення ε-замикання
│   ├── sub_set_epsilon.py           #   Subset Construction + ε
│   ├── quick_subset_epsilon.py      #   QSC + ε
│   ├── brzozowski_epsilon.py        #   Бжозовський + ε
│   ├── transset_epsilon.py          #   Transset + ε
│   └── lazy_subset_epsilon.py       #   Lazy Subset + ε
│
├── Analize/                         # Аналіз, візуалізація, допоміжні інструменти
│   ├── nfa.py                       #   Предвизначені NFA для тестування (nfa_1..nfa_5)
│   ├── simple_benchmark.py          #   Простий бенчмарк: час алгоритмів на випадкових NFA
│   ├── heatmap_comparison.py        #   Генерація heatmap-порівнянь (щільність × розмір)
│   ├── graph_visualizer.py          #   Візуалізація графів NFA/DFA (graphviz)
│   ├── table_visualizer.py          #   Візуалізація таблиць переходів
│   ├── word_check.py                #   Перевірка прийняття слів автоматом
│   └── words.py                     #   Генерація тестових слів
│
├── Tests/                           # Бенчмарк-тести (порівняння продуктивності)
│   ├── nfa_generators.py            #   Генератори спеціальних NFA для бенчмарків
│   ├── run_all.py                   #   Запуск усіх бенчмарк-тестів
│   ├── test1_exponential_blowup.py  #   Тест: експоненційний вибух (n-th from last)
│   ├── test2_density_impact.py      #   Тест: вплив щільності переходів
│   ├── test3_sparse_nondeterminism.py  # Тест: розріджений недетермінізм
│   ├── test4_branch_structure.py    #   Тест: паралельні гілки
│   ├── test5_alphabet_size.py       #   Тест: вплив розміру алфавіту
│   ├── test6_epsilon_overhead.py    #   Тест: overhead від ε-переходів
│   ├── test7_nondet_degree.py       #   Тест: змінний ступінь недетермінізму
│   └── test8_correctness.py         #   Тест: коректність результатів
│
├── unit_tests/                      # Unit-тести (коректність алгоритмів)
│   ├── helpers/                     #   Допоміжні функції для тестів
│   │   ├── dfa_helpers.py           #     Запуск DFA/NFA на словах, генерація слів
│   │   ├── equivalence.py           #     Перевірка еквівалентності мов
│   │   ├── isomorphism.py           #     Перевірка ізоморфізму DFA
│   │   └── minimization.py          #     Мінімізація DFA (для порівняння)
│   ├── test_subset.py               #   Тести Subset Construction
│   ├── test_qsc.py                  #   Тести QSC
│   ├── test_brzozowski.py           #   Тести Бжозовського
│   ├── test_transset.py             #   Тести Transset
│   ├── test_lazy.py                 #   Тести Lazy Subset
│   ├── test_cross_algorithm.py      #   Крос-тести (всі алгоритми дають однаковий результат)
│   ├── test_edge_cases.py           #   Граничні випадки
│   ├── test_epsilon_variants.py     #   Тести ε-версій алгоритмів
│   └── test_minimization.py         #   Тести мінімізації
│
├── Table/                           # Згенеровані зображення (результати)
│   ├── graphs/                      #   Графи NFA/DFA
│   ├── tables/                      #   Таблиці переходів
│   ├── epsilon_graphs/              #   Графи для ε-варіантів
│   └── epsilon_tables/              #   Таблиці для ε-варіантів
│
└── At_Tests/                        # Додаткові графіки бенчмарків
    ├── graphs.py                    #   Скрипт генерації графіків
    └── Graphs/                      #   Згенеровані PNG (час, пам'ять, розмір DFA)
```

## Коротко

- **Algoritms/** — самі алгоритми (5 штук × 2 версії: з/без ε)
- **Tests/** — бенчмарки (вимірюють *швидкість*)
- **unit_tests/** — тести коректності (перевіряють *правильність*)
- **Analize/** — візуалізація + допоміжні NFA/слова
- **Table/** + **At_Tests/** — згенеровані результати (картинки)
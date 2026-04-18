"""
Запуск усіх 4 тестів детермінізації.

Використання:
    python -m Tests_Diagram.run_all          # всі тести
    python -m Tests_Diagram.run_all 1 3      # тільки тести 1 і 3
    python -m Tests_Diagram.run_all --no-cache   # ігнорувати кеш
"""

import sys
import os


def main():
    os.makedirs("Tests_Diagram", exist_ok=True)

    tests = {
        "1": ("Exponential Blowup (nth-from-last)", "Tests_Diagram.test1_exponential_blowup"),
        "2": ("Density Impact (dense random)", "Tests_Diagram.test2_density_impact"),
        "3": ("Sparse Nondeterminism", "Tests_Diagram.test3_sparse_nondeterminism"),
        "4": ("Branch Structure (multi-branch)", "Tests_Diagram.test4_branch_structure"),
        "5": ("Alphabet Size Impact", "Tests_Diagram.test5_alphabet_size"),
        "6": ("Epsilon Overhead", "Tests_Diagram.test6_epsilon_overhead"),
        "7": ("Nondeterminism Degree", "Tests_Diagram.test7_nondet_degree"),
        "8": ("Correctness Verification", "Tests_Diagram.test8_correctness"),
    }

    selected = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not selected:
        selected = list(tests.keys())

    for key in selected:
        if key not in tests:
            print(f"Unknown test: {key}. Available: {', '.join(tests.keys())}")
            continue

        title, module = tests[key]
        print(f"\n{'='*60}")
        print(f"  Test {key}: {title}")
        print(f"{'='*60}\n")

        mod = __import__(module, fromlist=["run"])
        mod.run()


if __name__ == "__main__":
    main()

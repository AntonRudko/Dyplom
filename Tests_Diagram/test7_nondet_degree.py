"""
Тест 7: Вплив ступеня недетермінізму на продуктивність.

Фіксований розмір НКА (100 станів), змінюється частка
недетермінованих переходів від 0% до 50%.

Очікувані результати:
- Subset: час майже не залежить від nd (завжди будує з нуля)
- Transset: помірна залежність від nd (менше злиттів при високому nd)
- Brzozowski: слабка залежність від nd (домінує overhead 4 проходів)
- Розмір DFA зростає з nd
"""

import random
import matplotlib.pyplot as plt

from Tests_Diagram.nfa_generators import gen_variable_nondet, measure
from Tests_Diagram.cache import load_cache, save_cache, BASE_SOURCES
from Algoritms.sub_set import determinize_nfa
from Algoritms.brzozowski import determinize_brz
from Algoritms.transset import determinize_transset

ALGORITHMS = [
    ("Subset",     determinize_nfa,  "ro-"),
    ("Brzozowski", determinize_brz,  "ms-"),
    ("Transset",   determinize_transset, "b^-"),
]

NUM_STATES = 18
ALPHABET = {"0", "1"}
NONDET_FRACTIONS = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5]
SAMPLES = 2
REPEATS = 3

_PARAMS = {
    "NUM_STATES": NUM_STATES,
    "ALPHABET": sorted(ALPHABET),
    "NONDET_FRACTIONS": NONDET_FRACTIONS,
    "SAMPLES": SAMPLES,
    "REPEATS": REPEATS,
    "SEED": 53,
}


def _compute():
    random.seed(53)
    results = {name: {"time": [], "mem": [], "dfa_size": [], "ops": []}
               for name, _, _ in ALGORITHMS}

    for nd in NONDET_FRACTIONS:
        print(f"nondet_fraction={nd:.0%}, states={NUM_STATES}")
        nfas = [gen_variable_nondet(NUM_STATES, ALPHABET, nd) for _ in range(SAMPLES)]

        for name, alg, _ in ALGORITHMS:
            times, mems, sizes, all_ops = [], [], [], []
            for nfa in nfas:
                t, m, s, ops = measure(alg, nfa, REPEATS)
                times.append(t)
                mems.append(m)
                sizes.append(s)
                all_ops.append(ops)

            avg_t = sum(times) / len(times)
            avg_m = sum(mems) / len(mems)
            avg_s = sum(sizes) / len(sizes)
            avg_ops = sum(all_ops) / len(all_ops)

            results[name]["time"].append(avg_t)
            results[name]["mem"].append(avg_m)
            results[name]["dfa_size"].append(avg_s)
            results[name]["ops"].append(avg_ops)

            print(f"  {name:12s}: time={avg_t:.4f}s  mem={avg_m:.1f}KB  DFA≈{avg_s:.0f}  ops≈{avg_ops:.0f}")

    return results


def _plot(results):
    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(NONDET_FRACTIONS, results[name]["time"], style, label=name, markersize=6)
    ax.set_xlabel("Частка недетермінізму (nd)")
    ax.set_ylabel("Час (с)")
    ax.set_yscale("log")
    ax.set_title(f"Тест 7: Ступінь недетермінізму — Час (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test7_nondet_degree_time.png", dpi=150)
    plt.close()
    print("\nSaved: Tests_Diagram/test7_nondet_degree_time.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(NONDET_FRACTIONS, results[name]["mem"], style, label=name, markersize=6)
    ax.set_xlabel("Частка недетермінізму (nd)")
    ax.set_ylabel("Пікова RAM (КБ)")
    ax.set_yscale("log")
    ax.set_title(f"Тест 7: Ступінь недетермінізму — Пам'ять (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test7_nondet_degree_memory.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test7_nondet_degree_memory.png")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, _, style in ALGORITHMS:
        ax.plot(NONDET_FRACTIONS, results[name]["dfa_size"], style, label=name, markersize=6)
    ax.plot(NONDET_FRACTIONS, [NUM_STATES] * len(NONDET_FRACTIONS),
            "k--", label="Розмір НСА (орієнтир)", alpha=0.5)
    ax.set_xlabel("Частка недетермінізму (nd)")
    ax.set_ylabel("Станів ДСА")
    ax.set_title(f"Тест 7: Ступінь недетермінізму — Розмір ДСА (n={NUM_STATES})")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend()
    plt.tight_layout()
    plt.savefig("Tests_Diagram/test7_nondet_degree_dfa_size.png", dpi=150)
    plt.close()
    print("Saved: Tests_Diagram/test7_nondet_degree_dfa_size.png")


def run():
    results = load_cache("test7", _PARAMS, BASE_SOURCES)
    if results is None:
        results = _compute()
        save_cache("test7", _PARAMS, BASE_SOURCES, results)
    _plot(results)


if __name__ == "__main__":
    run()

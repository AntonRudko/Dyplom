"""
Кешування результатів бенчмарків.

Зберігає результати обчислень у JSON-файли в папці Tests_Diagram/Cache/.
Кеш інвалідується автоматично при зміні:
  - параметрів тесту (SIZES, REPEATS, SAMPLES, ...)
  - вихідного коду алгоритмів
  - вихідного коду генераторів НКА

Використання:
    --no-cache    примусово перерахувати (ігнорувати кеш)
"""

import hashlib
import json
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(_DIR, "Cache")

# Шляхи до вихідних файлів, що впливають на результати
_BASE_ALG_FILES = [
    os.path.join(_DIR, "..", "Algoritms", f)
    for f in ("sub_set.py", "brzozowski.py", "transset.py")
]

_EPS_ALG_FILES = [
    os.path.join(_DIR, "..", "Algoritms_with_epsilon", f)
    for f in ("sub_set_epsilon.py", "brzozowski_epsilon.py",
              "transset_epsilon.py", "epsilon_closure.py")
]

_GENERATOR_FILE = os.path.join(_DIR, "nfa_generators.py")

BASE_SOURCES = _BASE_ALG_FILES + [_GENERATOR_FILE]
EPS_SOURCES = _EPS_ALG_FILES + [_GENERATOR_FILE]
ALL_SOURCES = _BASE_ALG_FILES + _EPS_ALG_FILES + [_GENERATOR_FILE]


def _file_hash(filepath):
    path = os.path.normpath(filepath)
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _fingerprint(params, source_files):
    h = hashlib.sha256()
    h.update(json.dumps(params, sort_keys=True, default=str).encode())
    for sf in sorted(source_files):
        h.update(_file_hash(sf).encode())
    return h.hexdigest()[:20]


def no_cache_requested():
    return "--no-cache" in sys.argv or "--force" in sys.argv


def load_cache(test_name, params, source_files):
    """Завантажити кешовані результати. Повертає dict або None."""
    if no_cache_requested():
        return None

    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{test_name}.json")

    if not os.path.exists(cache_file):
        return None

    try:
        with open(cache_file, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    fp = _fingerprint(params, source_files)
    if data.get("fingerprint") != fp:
        print(f"  [cache] {test_name}: fingerprint змінився — перераховуємо")
        return None

    print(f"  [cache] {test_name}: використовую кешовані результати")
    return data["results"]


def save_cache(test_name, params, source_files, results):
    """Зберегти результати в кеш."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    fp = _fingerprint(params, source_files)
    cache_file = os.path.join(CACHE_DIR, f"{test_name}.json")

    data = {
        "fingerprint": fp,
        "params": params,
        "results": results,
    }

    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"  [cache] {test_name}: результати збережено")

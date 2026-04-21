"""
Pretty test runner for thesis screenshots.

Groups unit tests by file with a section header per file, prints each test
with PASS/FAIL status and execution time, and produces a summary table.

Usage:
    python run_unit_tests.py
"""

import os
import sys
import time
import unittest
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(__file__))

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

FILE_TITLES = {
    "test_subset": "Subset Construction — еталонна перевірка",
    "test_brzozowski": "Brzozowski — еквівалентність з Subset",
    "test_transset": "Transset — еквівалентність з Subset",
    "test_lazy": "Lazy Subset — еквівалентність з Subset",
    "test_minimization": "Мінімізація ДСА та ізоморфізм",
    "test_cross_algorithm": "Перехресна еквівалентність алгоритмів",
    "test_edge_cases": "Граничні випадки",
    "test_epsilon_variants": "ε-варіанти алгоритмів",
    "test_word_equivalence": "Еквівалентність через прогін слів",
}

SECTION_ORDER = [
    "test_brzozowski",
    "test_minimization",
    "test_subset",
    "test_transset",
    "test_word_equivalence",
    "test_lazy",
]

EXCLUDED_MODULES = {
    "test_cross_algorithm",
    "test_edge_cases",
    "test_epsilon_variants",
}


class PrettyResult(unittest.TestResult):
    def __init__(self) -> None:
        super().__init__()
        self.records: List[Tuple[str, str, str, float, str]] = []
        self._start = 0.0

    def startTest(self, test: unittest.TestCase) -> None:
        super().startTest(test)
        self._start = time.perf_counter()

    def _record(self, test: unittest.TestCase, status: str, detail: str = "") -> None:
        elapsed = time.perf_counter() - self._start
        module = test.__class__.__module__.split(".")[-1]
        name = test._testMethodName
        doc = (test._testMethodDoc or "").strip().split("\n")[0] or name
        self.records.append((module, name, doc, elapsed, status))
        color = {"PASS": GREEN, "FAIL": RED, "ERROR": RED, "SKIP": YELLOW}[status]
        mark = {"PASS": "✓", "FAIL": "✗", "ERROR": "✗", "SKIP": "○"}[status]
        print(f"  {color}{mark}{RESET} {doc} {DIM}({elapsed * 1000:.1f} ms){RESET}")
        if detail:
            print(f"    {RED}{detail}{RESET}")

    def addSuccess(self, test):
        super().addSuccess(test)
        self._record(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._record(test, "FAIL", str(err[1]).splitlines()[0])

    def addError(self, test, err):
        super().addError(test, err)
        self._record(test, "ERROR", str(err[1]).splitlines()[0])

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._record(test, "SKIP", reason)


def _iter_tests(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _iter_tests(item)
        else:
            yield item


def _collect_by_module(suite: unittest.TestSuite) -> Dict[str, List[unittest.TestCase]]:
    buckets: Dict[str, List[unittest.TestCase]] = {}
    for test in _iter_tests(suite):
        module = test.__class__.__module__.split(".")[-1]
        buckets.setdefault(module, []).append(test)
    return buckets


def _display_width(text: str) -> int:
    import re

    stripped = re.sub(r"\033\[[0-9;]*m", "", text)
    return len(stripped)


def _pad(text: str, width: int) -> str:
    return text + " " * max(0, width - _display_width(text))


def main() -> int:
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=os.path.join(os.path.dirname(__file__), "unit_tests"),
        pattern="test_*.py",
        top_level_dir=os.path.dirname(__file__),
    )

    buckets = _collect_by_module(suite)
    for m in EXCLUDED_MODULES:
        buckets.pop(m, None)
    total = sum(len(v) for v in buckets.values())

    ordered_modules = [m for m in SECTION_ORDER if m in buckets]
    for m in sorted(buckets.keys()):
        if m not in ordered_modules:
            ordered_modules.append(m)

    print(f"\n{BOLD}{CYAN}═══ Запуск юніт-тестів ({total} тестів) ═══{RESET}\n")

    result = PrettyResult()
    overall_start = time.perf_counter()
    for module in ordered_modules:
        tests = buckets[module]
        title = FILE_TITLES.get(module, module)
        print(
            f"{BOLD}{CYAN}▸{RESET} {BOLD}{title}{RESET} "
            f"{DIM}[{module}.py • {len(tests)} тестів]{RESET}"
        )
        for test in tests:
            test.run(result)
        print()
    elapsed = time.perf_counter() - overall_start

    passed = sum(1 for r in result.records if r[4] == "PASS")
    failed = sum(1 for r in result.records if r[4] in ("FAIL", "ERROR"))
    skipped = sum(1 for r in result.records if r[4] == "SKIP")

    print(f"{BOLD}{CYAN}═══ Підсумок ═══{RESET}")
    header = f"  {BOLD}{_pad('Розділ', 44)}{_pad('Тестів', 12)}{'Статус'}{RESET}"
    print(header)
    print("  " + "─" * 72)
    for module in ordered_modules:
        mod_records = [r for r in result.records if r[0] == module]
        ok = sum(1 for r in mod_records if r[4] == "PASS")
        n = len(mod_records)
        status = (
            f"{GREEN}✓ УСПІХ{RESET}" if ok == n else f"{RED}✗ ПОМИЛКА{RESET}"
        )
        title = FILE_TITLES.get(module, module)
        print(f"  {_pad(title, 44)}{_pad(f'{ok}/{n}', 12)}{status}")
    print("  " + "─" * 72)
    print(
        f"  {BOLD}Всього:{RESET} {total}   "
        f"{GREEN}✓ пройдено: {passed}{RESET}   "
        f"{RED}✗ провалено: {failed}{RESET}   "
        f"{YELLOW}○ пропущено: {skipped}{RESET}"
    )
    print(f"  {BOLD}Час виконання:{RESET} {elapsed:.2f} с")

    status_line = (
        f"{GREEN}{BOLD}✓ Усі тести пройдено успішно{RESET}"
        if failed == 0
        else f"{RED}{BOLD}✗ Є провалені тести{RESET}"
    )
    print(f"\n{status_line}\n")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

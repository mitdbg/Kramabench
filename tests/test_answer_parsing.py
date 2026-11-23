import os

from benchmark.metrics import F1, F1Approximate

MARKER = "KRAMABENCH_TEST_MARKER"
CODE_ANSWER = f"__import__('os').environ.setdefault('{MARKER}', '1')"


def test_f1_parses_python_literal_lists():
    assert F1()("['Bucks Creek', 'Forest Street']", ["Bucks Creek", "Forest Street"])[0] == 1.0
    assert F1()("('a', 'b')", ["a", "b"])[0] == 1.0


def test_f1_does_not_execute_answer():
    os.environ.pop(MARKER, None)
    F1()(CODE_ANSWER, ["a"])
    assert MARKER not in os.environ


def test_f1_approximate_does_not_execute_answer():
    os.environ.pop(MARKER, None)
    F1Approximate()(CODE_ANSWER, [1.0])
    assert MARKER not in os.environ

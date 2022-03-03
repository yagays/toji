import pytest

from tohji.util import Counter


@pytest.fixture()
def c():
    c = Counter()
    c.set_total(10)
    return c


def test_counter_next_previous(c):

    assert c.index == 0
    c.next()
    assert c.index == 1
    c.next()
    assert c.index == 2

    c.previous()
    assert c.index == 1
    c.previous()
    assert c.index == 0


def test_counter_current_first_item(c):
    assert c.index == 0
    c.previous()
    assert c.index == 0


def test_counter_current_last_item(c):
    c.index = 9
    c.next()
    assert c.index == 9


def test_counter_total_is_none():
    c = Counter()
    assert c.index == 0
    assert c.total is None

    # don't increment when total is None
    c.next()
    assert c.index == 0


def test_counter_progress_percent(c):
    assert c.progress_percent == 0.1
    c.next()
    assert c.progress_percent == 0.2
    c.next()
    assert c.progress_percent == 0.3

    for _ in range(10):
        c.next()
    assert c.progress_percent == 1.0


def test_counter_only_1_item():
    c = Counter()
    c.set_total(1)

    assert c.index == 0
    assert c.progress_percent == 1.0

    c.next()
    assert c.index == 0  # not increment

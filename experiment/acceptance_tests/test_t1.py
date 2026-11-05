
import pytest

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


@pytest.fixture
def db():
    """Create a fresh in-memory TinyDB instance for each test."""
    database = TinyDB(storage=MemoryStorage)
    yield database
    database.close()


Q = Query()


# T1 - Scenario 1:
# Generator-based search must return every matching document.

def test_generator_search_returns_all_documents(db):
    db.insert_multiple([
        {"x": 2},
        {"x": 1},
        {"x": 3},
    ])

    query = Q.x.one_of(v for v in [1, 2])

    result = db.search(query)

    assert {doc["x"] for doc in result} == {1, 2}


# T1 - Scenario 2:
# Repeated evaluation and cached searches must remain correct.

def test_repeated_evaluation_and_cached_search(db):
    db.insert_multiple([
        {"x": 2},
        {"x": 1},
        {"x": 3},
    ])

    query = Q.x.one_of(v for v in [1, 2])

    # Direct evaluation three times
    assert query({"x": 1}) is True
    assert query({"x": 1}) is True
    assert query({"x": 1}) is True

    # Repeated database searches
    first_result = db.search(query)
    second_result = db.search(query)

    assert {doc["x"] for doc in first_result} == {1, 2}
    assert {doc["x"] for doc in second_result} == {1, 2}

    # Reuse the same query in other table operations
    assert db.count(query) == 2
    assert db.contains(query) is True


# T1 - Scenario 3:
# Equivalent candidate values must produce equivalent queries.

def test_generator_and_list_query_identity(db):
    q1 = Q.x.one_of(v for v in [1, 2])
    q2 = Q.x.one_of([1, 2])

    assert q1 == q2
    assert hash(q1) == hash(q2)

    q3 = Q.x.one_of(v for v in [3])

    assert q1 != q3

    db.insert_multiple([
        {"x": 1},
        {"x": 2},
        {"x": 3},
    ])

    assert {doc["x"] for doc in db.search(q1)} == {1, 2}
    assert {doc["x"] for doc in db.search(q3)} == {3}


# T1 - Scenario 4:
# Existing supported input types and unhashable candidates
# must continue to work.


def test_existing_one_of_behaviour(db):
    # Numeric candidates are tested against numeric field values.
    db.insert_multiple([
        {"x": 1},
        {"x": 2},
        {"x": 3},
    ])

    # List input
    assert {doc["x"] for doc in db.search(Q.x.one_of([1, 2]))} == {1, 2}

    # Tuple input
    assert {doc["x"] for doc in db.search(Q.x.one_of((1, 2)))} == {1, 2}

    # Set input
    assert {doc["x"] for doc in db.search(Q.x.one_of({1, 2}))} == {1, 2}

    # Range input
    assert {doc["x"] for doc in db.search(Q.x.one_of(range(1,4)))} == {1, 2, 3}

    # Empty generator
    assert db.search(Q.x.one_of(v for v in [])) == []

    # Missing field
    missing_query = Q.missing.one_of([1, 2])
    assert missing_query({"x": 1}) is False

    # Test unhashable candidates in a separate table.
    unhashable_table = db.table("unhashable")

    unhashable_table.insert_multiple([
        {"x": [1]},
        {"x": {"a": 1}},
    ])

    result = unhashable_table.search(
        Q.x.one_of([[1], {"a": 1}])
    )

    assert [doc["x"] for doc in result] == [[1], {"a": 1}]


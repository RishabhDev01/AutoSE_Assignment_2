
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


# T2 - Scenario 1:
# Inclusive and exclusive boundaries must work correctly.
def test_between_boundary_behaviour(db):
    db.insert_multiple([
        {"x": 1},
        {"x": 2},
        {"x": 3},
    ])

    inclusive = Q.x.between(1, 3)
    exclusive = Q.x.between(1, 3, inclusive=False)

    assert {doc["x"] for doc in db.search(inclusive)} == {1, 2, 3}
    assert {doc["x"] for doc in db.search(exclusive)} == {2}

    # Equal bounds
    equal_inclusive = Q.x.between(2, 2)
    equal_exclusive = Q.x.between(2, 2, inclusive=False)

    assert {doc["x"] for doc in db.search(equal_inclusive)} == {2}
    assert db.search(equal_exclusive) == []

    # Invalid bounds
    with pytest.raises(ValueError):
        Q.x.between(3, 1)

    with pytest.raises(TypeError):
        Q.x.between(1, "three")


# T2 - Scenario 2:
# Query identity and caching must include all arguments.
def test_between_query_identity_and_cache(db):
    db.insert_multiple([
        {"x": 1},
        {"x": 2},
        {"x": 3},
        {"x": 4},
    ])

    q1 = Q.x.between(1, 3)
    q2 = Q.x.between(1, 3)
    q3 = Q.x.between(1, 3, inclusive=False)
    q4 = Q.x.between(2, 4)

    assert q1 == q2
    assert hash(q1) == hash(q2)

    assert q1 != q3
    assert q1 != q4

    first_result = db.search(q1)
    second_result = db.search(q1)

    assert {doc["x"] for doc in first_result} == {1, 2, 3}
    assert {doc["x"] for doc in second_result} == {1, 2, 3}

    assert db.count(q1) == 3


# T2 - Scenario 3:
# Nested paths, missing fields, mixed values and map must work.
def test_between_nested_paths_and_map(db):
    db.insert_multiple([
        {"a": {"b": 1}},
        {"a": {"b": 2}},
        {"a": {"b": 3}},
        {"a": {"b": "hello"}},
        {"a": {"b": None}},
        {"a": "not-a-dictionary"},
        {"other": 10},
    ])

    query = Q.a.b.between(1, 3)

    result = db.search(query)

    assert {doc["a"]["b"] for doc in result} == {1, 2, 3}

    # Invalid or missing values must not cause exceptions.
    assert query({"a": {"b": "hello"}}) is False
    assert query({"a": {"b": None}}) is False
    assert query({"a": "not-a-dictionary"}) is False
    assert query({"other": 10}) is False

    # Map should work with between.
    mapped_query = Q.a.map(len).between(1, 2)

    mapped_db = db.table("mapped")
    mapped_db.insert_multiple([
        {"a": [1]},
        {"a": [1, 2]},
        {"a": [1, 2, 3]},
    ])

    mapped_result = mapped_db.search(mapped_query)

    assert [len(doc["a"]) for doc in mapped_result] == [1, 2]


# T2 - Scenario 4:
# between must work with query composition and table operations.
def test_between_query_composition_and_table_operations(db):
    db.insert_multiple([
        {"x": 1, "active": True},
        {"x": 2, "active": True},
        {"x": 3, "active": False},
        {"x": 4, "active": True},
        {"x": 5, "active": False},
    ])

    between_query = Q.x.between(2, 4)

    # AND
    and_query = between_query & (Q.active == True)
    assert {doc["x"] for doc in db.search(and_query)} == {2, 4}

    # OR
    or_query = Q.x.between(1, 2) | Q.x.between(4, 5)
    assert {doc["x"] for doc in db.search(or_query)} == {1, 2, 4, 5}

    # NOT
    not_query = ~(Q.x.between(2, 4))
    assert {doc["x"] for doc in db.search(not_query)} == {1, 5}

    # Count
    assert db.count(between_query) == 3

    # Remove
    removed = db.remove(between_query)

    assert {doc["x"] for doc in removed} == {2, 3, 4}
    assert db.count(between_query) == 0

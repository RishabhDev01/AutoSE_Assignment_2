
import gzip
import importlib
import json

import pytest

from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware


def get_compressed_storage():
    """Import the new storage class without breaking baseline test collection."""
    module = importlib.import_module("tinydb.storages")
    return getattr(module, "CompressedJSONStorage")


# T3 - Scenario 1:
# Compressed storage must write valid gzip JSON and support round trips.
def test_compressed_storage_round_trip(tmp_path):
    storage_class = get_compressed_storage()
    db_path = tmp_path / "database.json.gz"

    db = TinyDB(db_path, storage=storage_class)

    db.insert({"name": "Alice", "age": 25})
    db.insert({"name": "Bob", "age": 30})

    db.close()

    # Verify gzip magic bytes.
    raw_bytes = db_path.read_bytes()
    assert raw_bytes[:2] == b"\x1f\x8b"

    # Verify that the compressed content is valid JSON.
    with gzip.open(db_path, "rt", encoding="utf-8") as file:
        json.load(file)

    # Reopen and verify the original documents.
    reopened_db = TinyDB(db_path, storage=storage_class)

    assert reopened_db.all() == [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
    ]

    reopened_db.close()


# T3 - Scenario 2:
# Compressed storage must work with CachingMiddleware.
def test_compressed_storage_with_caching_middleware(tmp_path):
    storage_class = get_compressed_storage()
    db_path = tmp_path / "cached_database.json.gz"

    marker = "pending-cache-write-unique-marker"

    db = TinyDB(
        db_path,
        storage=CachingMiddleware(storage_class),
    )

    db.insert({"marker": marker})

    # Before close, the cached write should not yet be on disk.
    if db_path.exists():
        raw_bytes = db_path.read_bytes()

        if raw_bytes:
            try:
                content = gzip.decompress(raw_bytes).decode("utf-8")
            except (OSError, EOFError):
                content = ""

            assert marker not in content

    # Closing should flush the cache.
    db.close()

    reopened_db = TinyDB(db_path, storage=storage_class)

    assert reopened_db.all() == [{"marker": marker}]

    reopened_db.close()

    # Using the closed database should raise ValueError.
    with pytest.raises(ValueError):
        db.insert({"after_close": True})


# T3 - Scenario 3:
# Rewriting a smaller database must not leave stale compressed data.
def test_compressed_storage_after_deletions(tmp_path):
    storage_class = get_compressed_storage()
    db_path = tmp_path / "shrinking_database.json.gz"

    db = TinyDB(db_path, storage=storage_class)

    db.insert_multiple([
        {"id": i, "value": f"record-{i}"}
        for i in range(200)
    ])

    db.close()

    # Reopen and remove every document except one.
    db = TinyDB(db_path, storage=storage_class)

    db.remove(lambda document: document["id"] != 100)

    db.close()

    # Reopen again and verify the final database.
    reopened_db = TinyDB(db_path, storage=storage_class)

    assert reopened_db.all() == [
        {"id": 100, "value": "record-100"}
    ]

    reopened_db.close()

    # The final file must still be valid gzip JSON.
    with gzip.open(db_path, "rt", encoding="utf-8") as file:
        json.load(file)


# T3 - Scenario 4:
# Edge cases, constructor options, read-only mode and public exports.
def test_compressed_storage_edge_cases_and_exports(tmp_path):
    storage_class = get_compressed_storage()

    # Both public import paths must expose the same class.
    storages_module = importlib.import_module("tinydb.storages")
    tinydb_module = importlib.import_module("tinydb")

    top_level_class = getattr(tinydb_module, "CompressedJSONStorage")

    assert top_level_class is storage_class
    assert "CompressedJSONStorage" in storages_module.__all__
    assert "CompressedJSONStorage" in tinydb_module.__all__

    # A missing writable file should be created.
    missing_path = tmp_path / "new_database.json.gz"

    db = TinyDB(missing_path, storage=storage_class)

    assert db.all() == []

    db.insert({"x": 1})
    db.close()

    assert missing_path.exists()

    # A zero-byte file should be treated as an empty database.
    zero_path = tmp_path / "zero.json.gz"
    zero_path.write_bytes(b"")

    db = TinyDB(zero_path, storage=storage_class)

    assert db.all() == []

    db.close()

    # Read-only mode should allow reading.
    readonly_path = tmp_path / "readonly.json.gz"

    db = TinyDB(readonly_path, storage=storage_class)
    db.insert({"name": "ReadOnlyTest"})
    db.close()

    original_bytes = readonly_path.read_bytes()

    readonly_db = TinyDB(
        readonly_path,
        storage=storage_class,
        access_mode="r",
    )

    assert readonly_db.all() == [{"name": "ReadOnlyTest"}]

    with pytest.raises(OSError):
        readonly_db.insert({"name": "ShouldNotBeWritten"})

    readonly_db.close()

    assert readonly_path.read_bytes() == original_bytes

    # Missing file in read-only mode must raise FileNotFoundError.
    nonexistent_readonly_path = tmp_path / "does_not_exist.json.gz"

    with pytest.raises(FileNotFoundError):
        TinyDB(
            nonexistent_readonly_path,
            storage=storage_class,
            access_mode="r",
        )

    # Plain JSON must not be silently overwritten as compressed data.
    plain_json_path = tmp_path / "plain.json.gz"
    plain_json_path.write_text(
        '{"_default": {"1": {"name": "PlainJSON"}}}',
        encoding="utf-8",
    )

    original_plain_bytes = plain_json_path.read_bytes()

    with pytest.raises((OSError, ValueError)):
        TinyDB(plain_json_path, storage=storage_class)

    assert plain_json_path.read_bytes() == original_plain_bytes

    # JSON serialization options must be forwarded.
    sorted_path = tmp_path / "sorted.json.gz"

    db = TinyDB(
        sorted_path,
        storage=storage_class,
        sort_keys=True,
    )

    db.insert({"z": 1, "a": 2})
    db.close()

    with gzip.open(sorted_path, "rt", encoding="utf-8") as file:
        serialized_content = file.read()

    assert serialized_content.index('"a"') < serialized_content.index('"z"')

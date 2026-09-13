import pytest

from app.storage.mongodb import database


@pytest.fixture(autouse=True)
def cleanup_database():
    database.datasets.delete_many({})
    database.fs.files.delete_many({})
    database.fs.chunks.delete_many({})

    yield

    database.datasets.delete_many({})
    database.fs.files.delete_many({})
    database.fs.chunks.delete_many({})
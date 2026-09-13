from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import settings


client: MongoClient | None = None
database = None


def connect_to_mongodb() -> None:
    """Establish connection to MongoDB."""
    global client, database

    try:
        client = MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,
        )

        client.admin.command("ping")

        database = client[settings.mongodb_db_name]

        print("MongoDB connection successful.")

    except PyMongoError as exc:
        client = None
        database = None
        raise RuntimeError(
            f"MongoDB connection failed: {exc}"
        ) from exc


def close_mongodb_connection() -> None:
    """Close MongoDB connection."""
    global client, database

    if client is not None:
        client.close()

    client = None
    database = None


def get_datasets_collection():
    """Return the datasets MongoDB collection."""
    if database is None:
        raise RuntimeError("MongoDB is not connected.")

    return database["datasets"]
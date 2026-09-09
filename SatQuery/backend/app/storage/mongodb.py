from pymongo import MongoClient

from app.core.config import settings


client = MongoClient(settings.mongodb_uri)

database = client[settings.mongodb_database]
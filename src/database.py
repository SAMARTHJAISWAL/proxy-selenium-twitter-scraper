from pymongo import MongoClient

from config.config import Config


class Database:
    """Thin wrapper around the MongoDB collection that stores scrape results."""

    def __init__(self, uri: str = Config.MONGO_URI, db_name: str = Config.MONGO_DB,
                 collection: str = Config.MONGO_COLLECTION):
        # MongoClient connects lazily, so creating it does not require a running server.
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.collection = self.client[db_name][collection]

    def insert_trends(self, data: dict):
        return self.collection.insert_one(data)

    def get_latest_trends(self):
        return self.collection.find_one(sort=[("datetime", -1)])

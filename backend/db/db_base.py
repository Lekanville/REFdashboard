import os

from motor.motor_asyncio import AsyncIOMotorClient


def get_db_handle() -> AsyncIOMotorClient:
    """
    This function returns the database handle
    """

    user = os.environ.get("MONGO_INITDB_ROOT_USERNAME", "")
    password = os.environ.get("MONGO_INITDB_ROOT_PASSWORD", "")
    client = AsyncIOMotorClient(f"mongodb://{user}:{password}@mongo:27017")
    return client
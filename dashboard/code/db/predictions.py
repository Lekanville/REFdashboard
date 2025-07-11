import os

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio


async def get_predictions():
    """
    This function returns the database handle
    """

    user = os.environ.get("MONGO_INITDB_ROOT_USERNAME", "")
    password = os.environ.get("MONGO_INITDB_ROOT_PASSWORD", "")
    db_name = os.environ.get("DB_NAME", "")
    prediction_col_name = os.environ.get("RESEARCH_OUTPUT_PREDICTIONS", "")
    ref_embedding_col_name = os.environ.get("REF_EMBEDDINGS_PCA", "")

    client = AsyncIOMotorClient(f"mongodb://{user}:{password}@mongo:27017")
    database = client.get_database(db_name)
    prediction_collection = database.get_collection(prediction_col_name)
    ref_embedding_collection = database.get_collection(ref_embedding_col_name)

    # Fetch all predictions
    data_predictions = await prediction_collection.find({}, {"_id": 0}).to_list(100000)

    # Fetch all REF embeddings
    data_ref_embeddings = await ref_embedding_collection.find({}, {"_id": 0}).to_list(100000)

    # docs = []
    # async for doc in cursor:
    #     docs.append(doc)
    return data_predictions, data_ref_embeddings

# Run the async function and display results

def get_predictions_sync():
    """
    Synchronous wrapper for the async get_predictions function.
    """
    return asyncio.run(get_predictions())
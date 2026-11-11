import os
import io
import datetime
import pandas as pd
from db.db_base import get_db_handle

async def  upload_ref_embedding_pcas(REF_EMBEDDINGS_PCA):
    """
    Uploads the REF embedding data to the database.
    This uploads the REF embedding data of the research output from other Universities.
    """

    db_name = os.environ.get("DB_NAME", "")
    ref_embeddings_col_name = os.environ.get("REF_EMBEDDINGS_PCA", "")
    CLIENT = get_db_handle()
    database = CLIENT.get_database(db_name)
    ref_embeddings_pca_collection = database.get_collection(ref_embeddings_col_name)
    date = datetime.datetime.now()

    df = pd.read_csv(io.StringIO(REF_EMBEDDINGS_PCA.decode("utf-8")))

    for i in range(len(df)):
        # Convert each row to a dictionary
        data = df.iloc[i].to_dict()
        data['created_at'] = date
        await ref_embeddings_pca_collection.insert_one(data)

    return True
import os
import io
import datetime
import pandas as pd
from db.db_base import get_db_handle

async def upload_predictions_data(PREDICTIONS):
    """
    Uploads predictions data from a CSV file to the database.

    Args:
        INPUT_FILE (str): Path to the input CSV file containing predictions data.
    """

    db_name = os.environ.get("DB_NAME", "")
    prediction_col_name = os.environ.get("RESEARCH_OUTPUT_PREDICTIONS", "")
    CLIENT = get_db_handle()
    database = CLIENT.get_database(db_name)
    prediction_collection = database.get_collection(prediction_col_name)
    date = datetime.datetime.now()

    # Read the CSV file into a DataFrame
    df = pd.read_csv(io.StringIO(PREDICTIONS.decode("utf-8")))
    df = df[df['article_type'] == "ContributionToJournal"]
    df.drop(columns=['Unnamed: 0'], inplace=True)

    for i in range(len(df)):
        # Convert each row to a dictionary
        research_uuid = df.iloc[i]['research_uuid']
        query = {"research_uuid": research_uuid}
        article_count = await prediction_collection.count_documents(query)

        if article_count == 0:
            # If no document exists, insert a new one
            data = df.iloc[i].to_dict()
            data['created_at'] = date
            await prediction_collection.insert_one(data)
        else:
            # If a document exists, update it
            data = df.iloc[i].to_dict()
            data['updated_at'] = date
            await prediction_collection.update_one(query, {"$set": data})

    return True



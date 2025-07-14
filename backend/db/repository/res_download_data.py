import os
import io
import pandas as pd
from db.db_base import get_db_handle
import datetime
from fastapi.responses import StreamingResponse


async def download_research_data():
    db_name = os.environ.get("DB_NAME", "")
    res_output_col_name = os.environ.get("RESEARCH_OUTPUT_COLLECTION", "")
    res_journal_details_col_name = os.environ.get("RESEARCH_JOURNAL_DETAILS_COLLECTION", "")

    CLIENT = get_db_handle()
    database = CLIENT.get_database(db_name)
    output_collection = database.get_collection(res_output_col_name)
    journal_details_collection = database.get_collection(res_journal_details_col_name)

    research_outputs_fields = {  
                                "_id":0,
                                "research_uuid": 1,
                                "school_uuid": 1,
                                "pure_id": 1, 
                                "article_type": 1, 
                                "title": 1, 
                                "year": 1, 
                                "abstract": 1, 
                                "doi": 1, 
                                "issn": 1, 
                                "authors": 1, 
                                "journal_title": 1, 
                                "external_author_uuids": 1, 
                                "internal_author_uuids": 1
                            }
    
    journal_details_fields = {  
                                "_id":0,
                                "research_uuid": 1,
                                "sjr": 1,
                                "altmetric_score": 1,
                            }

    research_outputs = await output_collection.find({}, research_outputs_fields).to_list(100000)
    research_outputs_df = pd.DataFrame(research_outputs)

    journal_details = await journal_details_collection.find({}, journal_details_fields).to_list(100000)
    journal_details_df = pd.DataFrame(journal_details)

    all_features = pd.merge(research_outputs_df, journal_details_df, on="research_uuid", how="left")


    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_FILE = f"all_research_data_{timestamp}.csv"
    csv_buffer = io.StringIO()
    all_features.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return StreamingResponse(
                csv_buffer,
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=OUTPUT_FILE"}
            )


    # all_features.to_csv(OUTPUT_FILE, index=False)
    # return 1
import os
import re
import datetime
import io 
import pandas as pd
import datetime
from fastapi.responses import StreamingResponse
from db.db_base import get_db_handle

async def download_new_research_data():
    """
    Downloads new research data from the database and saves it to a CSV file.

    Args:
        OUTPUT_FILE (str): Path to the output CSV file where the data will be saved.
    """

    db_name = os.environ.get("DB_NAME", "")
    res_output_col_name = os.environ.get("RESEARCH_OUTPUT_COLLECTION", "")
    res_journal_details_col_name = os.environ.get("RESEARCH_JOURNAL_DETAILS_COLLECTION", "")
    prediction_col_name = os.environ.get("RESEARCH_OUTPUT_PREDICTIONS", "")

    CLIENT = get_db_handle()
    database = CLIENT.get_database(db_name)
    research_output_collection = database.get_collection(res_output_col_name)
    journal_details_collection = database.get_collection(res_journal_details_col_name)
    prediction_collection = database.get_collection(prediction_col_name)

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
    # Fetch all predictions
    predictions = await prediction_collection.find({}, {"_id": 0, "research_uuid": 1}).to_list(100000)



    # fetching and cleaning wrangled research outputs
    # Fetch all wrangled research outputs and journal details
    research_outputs = await research_output_collection.find({}, research_outputs_fields).to_list(100000)
    research_outputs_df = pd.DataFrame(research_outputs)

    # Filter research outputs to only include those of type "ContributionToJournal"
    research_outputs_df_journal = research_outputs_df[research_outputs_df['article_type'] == "ContributionToJournal"]

    # Filter research abstracts with missing or empty abstracts
    research_outputs_df_abstracts = research_outputs_df_journal[
        (research_outputs_df_journal['abstract'].notnull()) & 
        (research_outputs_df_journal['abstract'] != "" ) &
        (research_outputs_df_journal['abstract'] != "<p>[Figure: see text].</p>") &
        (research_outputs_df_journal['abstract'] != "<br/>") &
        (research_outputs_df_journal['abstract'] != "<p>Logo for Physiological Reports' 10th anniversary year.</p>")
        ]
    
    # Reset index after after this filtering
    research_outputs_df_abstracts.reset_index(drop=True, inplace=True)
    
    # Use regular expression to flter out "no abstract"

    research_outputs_df_abstracts_clean = pd.DataFrame()
    for i in range(len(research_outputs_df_abstracts)):
        abstract = research_outputs_df_abstracts.loc[i, 'abstract']
        if (not re.search("no abstract*", abstract.lower())) and \
            (not re.search("this corrects the article doi:*", abstract.lower())):
            new = research_outputs_df_abstracts[research_outputs_df_abstracts.index == i]
            research_outputs_df_abstracts_clean = pd.concat([research_outputs_df_abstracts_clean, new], ignore_index=True)
    
    # reset index after filtering
    research_outputs_df_abstracts_clean.reset_index(drop=True, inplace=True)


    # Filter research outputs that are not in predictions
    predicted_uuids = [pred['research_uuid'] for pred in predictions]
    new_research_outputs_df = research_outputs_df_abstracts_clean[~research_outputs_df_abstracts_clean['research_uuid'].isin(predicted_uuids)]


    # Fetch all journal details
    if new_research_outputs_df.empty:
        print("No new research data to download.")
    
    else:
        journal_details = await journal_details_collection.find({}, journal_details_fields).to_list(100000)
        journal_details_df = pd.DataFrame(journal_details)

        # Merge new research outputs with journal details
        new_features = pd.merge(new_research_outputs_df, journal_details_df, on="research_uuid", how="left")

        # Save DataFrame to CSV
        if new_features.empty:
            print("No new research data to download.")
        else:
            # Add a timestamp to the output file name
            # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # OUTPUT_FILE = OUTPUT_FILE.replace(".csv", f"_{timestamp}.csv")
            # Save the new features DataFrame to the specified output file
            # new_features.to_csv(OUTPUT_FILE, index=False)
            # print(f"New research data downloaded and saved to {OUTPUT_FILE}")

            # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # OUTPUT_FILE = f"new_research_data_{timestamp}.csv"
            csv_buffer = io.StringIO()
            new_features.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            return StreamingResponse(
                        csv_buffer,
                        media_type="text/csv",
                        headers={"Content-Disposition": "attachment; filename=OUTPUT_FILE"}
                    )

import os
import datetime
from db.db_base import get_db_handle
from utils.journal_details.requests import author_details
from db.models.res_outputs import ResearchOutputAuthors


async def research_journal_authors():
    db_name = os.environ.get("DB_NAME", "")
    res_output_col_name = os.environ.get("RESEARCH_OUTPUT_COLLECTION", "")
    res_output_authors = os.environ.get("RESEARCH_OUTPUT_AUTHORS", "")

    CLIENT = get_db_handle()
    database = CLIENT.get_database(db_name)
    output_collection = database.get_collection(res_output_col_name)
    res_output_authors_collection = database.get_collection(res_output_authors)

    research_outputs_authors = await output_collection.find({}, {"_id":0, "internal_author_uuids": 1}).to_list(100000)

    for result in research_outputs_authors:
        author_uuids = result["internal_author_uuids"]
        for author_uuid in author_uuids:
            query = {"author_uuid": author_uuid}
            author_count = await res_output_authors_collection.count_documents(query)
            if (author_count == 0):
                data =  author_details(author_uuid)
                try:
                    item = data["items"][0]
                    fname = item["name"]["firstName"]
                    lname = item["name"]["lastName"]
                    author_name = f"{fname} {lname}"
                except(IndexError, KeyError):
                    author_name = ""

                date = str(datetime.datetime.now())
                author_detail={
                        "author_uuid": author_uuid,
                        "author_name": author_name,
                        "uoa": "",
                        "date":date
                        }
                journal_details = dict(ResearchOutputAuthors(author_detail))
                await res_output_authors_collection.insert_one(journal_details)

    return 1 

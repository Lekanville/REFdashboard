import os
import re
import datetime
from db.db_base import get_db_handle
from utils.journal_details.scopus_details import get_scopus_details
from utils.journal_details.altmetric_score import get_altmetric_score
from db.models.res_outputs import ResearchJournalDetails

async def research_journal_details():
    db_name = os.environ.get("DB_NAME", "")
    res_output_col_name = os.environ.get("RESEARCH_OUTPUT_COLLECTION", "")
    res_journal_details_col_name = os.environ.get("RESEARCH_JOURNAL_DETAILS_COLLECTION", "")

    CLIENT = get_db_handle()
    database = CLIENT.get_database(db_name)
    output_collection = database.get_collection(res_output_col_name)
    journal_details_collection = database.get_collection(res_journal_details_col_name)

    research_outputs = await output_collection.find({}, {"_id":0, "research_uuid": 1, "abstract":1, "journal_title":1, "doi":1, "issn":1}).to_list(100000)

    for research_output in research_outputs:
        research_uuid = research_output["research_uuid"]
        #research_journal_details = await journal_details_collection.find({"research_uuid": research_uuid}, {"_id":0, "research_uuid": 1}).to_list(100000)

        query = {"research_uuid": research_uuid}
        article_count = await journal_details_collection.count_documents(query)
        if (article_count == 0):
            research_output_abstract = research_output["abstract"]
            research_output_journal_title = research_output["journal_title"]
            research_output_doi = research_output["doi"]
            research_output_issn = research_output["issn"]

            scopus_data = get_scopus_details(research_output_doi, research_output_journal_title, research_output_issn)
            altmetric_score = get_altmetric_score(research_output_doi)

            #Replace abstract if missing in PURE and availbale in Scopus
            scopus_abstract = scopus_data["abstract"]
            if (((research_output_abstract == "") or (re.search("no abstract*", research_output_abstract.lower()))) and scopus_abstract != ""):
                update = {"abstract":scopus_abstract}

                await output_collection.find_one_and_update(
                                    {"research_uuid": research_uuid},
                                    {"$set": update}
                                )
                
            scopus_and_altmetric = dict(scopus_data, **altmetric_score)
            date = str(datetime.datetime.now())
            scopus_and_altmetric["date"] = date
            scopus_and_altmetric["research_uuid"] = research_uuid
            # combined_data = dict(scopus_and_altmetric, **date)
            journal_details = dict(ResearchJournalDetails(**scopus_and_altmetric))
            await journal_details_collection.insert_one(journal_details)

    return 1  
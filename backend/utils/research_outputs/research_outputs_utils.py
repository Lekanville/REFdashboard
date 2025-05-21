import json
import os
import requests
import datetime
from typing import List
from db.db_base import get_db_handle
from db.models.res_outputs import ResearchOutput
from utils.journal_details.requests import pure_research_output_uuid

scopus_api_key = os.environ.get("SCOPUS_API_KEY")
pure_api_key = os.environ.get("PURE_API_KEY")


# For the all dependents to an organization
# def all_research_outputs(school_uuid: str):
#     """
#     To get all dependents to an organization from the pure API
#     :param uuid: The uuid of the research output
#     """
#     # Get the pure_id from the uuid
#     req_pure = requests.get(
#         f"https://research-information.bris.ac.uk/ws/api/organizations/{school_uuid}/dependents",
#         headers={
#             "accept": "application/json",
#             "api-key": f"{pure_api_key}",
#             "content-type": "application/json",
#         }
#     )

#     if req_pure.status_code != 200:
#         raise Exception(f"Error: {req_pure.status_code} - {req_pure.text}")
#     else:
#         data = req_pure.json()
        
#         # with open(f'{school_uuid}_data.json', 'w', encoding='utf-8') as f:
#         #     json.dump(data, f, ensure_ascii=False, indent=4)
        
#         return data

# Research output UUIDS
async def get_research_output_uuids(school_uuid: str, all_outputs: str):
    """
    To get the research output from all dependdents to an organization
    :param uuid: The uuid of the research output
    """
    db_name = os.environ.get("DB_NAME", "")
    uuid_col_name = os.environ.get("RESEARCH_OUTPUT_UUIDS", "")
    CLIENT = get_db_handle()
    database = CLIENT.get_database(db_name)
    collection = database.get_collection(uuid_col_name)
    date = datetime.datetime.now()

    #research_output_uuids = []
    all_linked_outputs = all_outputs["items"]
    for linked_output in all_linked_outputs:
        if linked_output["systemName"] == "ResearchOutput":
           research_uuid = linked_output["uuid"]
           research_type = linked_output["systemName"]
           query = {"research_uuid": research_uuid}
           article_count = await collection.count_documents(query)
           if (article_count == 0):
                detail={
                    "research_uuid": research_uuid,
                    "school_uuid":school_uuid,
                    "research_type":research_type,
                    "check_details": 0,
                    "check_details_date":date,
                }
                await collection.insert_one(detail)
    return 1

        # research_output_uuids.append(i["uuid"])   
    #research_output_len = len(research_output_uuids)
    #print("The number of research outputs is: ", research_output_len)
    #return (research_output_len)

    # return research_output_uuids

# Research output details from PURE
async def get_research_output_details(research_outputs_uuids: List[str]):
    """
    To get the research output from the pure API
    :param uuids: The uuid of the research output
    """

    db_name = os.environ.get("DB_NAME", "")
    uuid_col_name = os.environ.get("RESEARCH_OUTPUT_UUIDS", "")
    details_col_name = os.environ.get("RESEARCH_OUTPUT_COLLECTION", "")
    CLIENT = get_db_handle()
    database = CLIENT.get_database(db_name)
    collection_uuids = database.get_collection(uuid_col_name)
    collection_details = database.get_collection(details_col_name)

    for research_output in research_outputs_uuids:
        check_details = research_output["check_details"]

        if (check_details == 0):
            research_uuid = research_output["research_uuid"]
            school_uuid = research_output["school_uuid"]

            #Check if the research detail has not been added before
            query = {"research_uuid": research_uuid}
            article_count = await collection_details.count_documents(query)
            if (article_count == 0):
                data = pure_research_output_uuid(research_uuid)
                item = data["items"][0]

                article_type = item["typeDiscriminator"]
                year = item["publicationStatuses"][0]["publicationDate"]["year"]

                #Add only research outputs added after 2020
                #if (article_type == "ContributionToJournal") & (int(year) > 2020):
                if (int(year) > 2020):
                    title = item["title"]["value"]

                    # Pure ID
                    try:
                        pure_id = item["pureId"]
                    except (IndexError, KeyError):
                        pure_id = ""

                    # Abstract
                    # abstract = ""
                    # if (abstract == "") | (str(abstract) == "None"):
                    try:
                        abstract = item["abstract"]["en_GB"]
                    except (IndexError, KeyError):
                        abstract = ""

                    # if (abstract == "") | (str(abstract) == "None"):
                    #     try:
                    #         abstract = item["abstract"]["en_GB"]
                    #     except (IndexError, KeyError):
                    #         abstract = ""

                    #Journal Title
                    try:
                        journal_title = item["journalAssociation"]["title"]["title"]
                    except (IndexError, KeyError):
                        journal_title = ""   
                        
                    #DOI
                    try:
                        doi = item["electronicVersions"][0]["doi"]
                    except (IndexError, KeyError):
                        doi = ""

                    #ISSN
                    # try:
                    #     ISSN = item["publicationSeries"][0]["printIssn"]
                    # except (IndexError, KeyError):
                    #     ISSN = ""
                    #    if ISSN == "":
                        
                    try:
                        issn = item["journalAssociation"]["issn"]["issn"]
                    except (IndexError, KeyError):
                        issn = ""   

                    # Contributors
                    authors = []
                    try:
                        contributors = item["contributors"]
                        for contributor in contributors:
                            fname = contributor["name"]["firstName"]
                            lname = contributor["name"]["lastName"]
                            author = f"{fname} {lname}"
                            authors.append(author)
                    except (IndexError, KeyError):
                        authors = ""

                    external_author_uuids = []
                    internal_author_uuids = []
                    try:
                        contributors = item["contributors"]
                        for contributor in contributors:
                            if contributor["typeDiscriminator"] == "ExternalContributorAssociation":
                                external_author_uuid = contributor["externalPerson"]["uuid"]
                                external_author_uuids.append(external_author_uuid)
                            elif contributor["typeDiscriminator"] == "InternalContributorAssociation":
                                internal_author_uuid = contributor["person"]["uuid"]
                                internal_author_uuids.append(internal_author_uuid)
                    except (IndexError, KeyError):
                        external_author_uuids = external_author_uuids
                        internal_author_uuids = internal_author_uuids
                        

                    output_detail={
                        "research_uuid": research_uuid,
                        "school_uuid": school_uuid,
                        "pure_id": pure_id,
                        "article_type": article_type,
                        "title": title,
                        "year": year,
                        "abstract": abstract,
                        "journal_title":journal_title,
                        "doi": doi,
                        "issn": issn,
                        "authors": authors,
                        "external_author_uuids": external_author_uuids,
                        "internal_author_uuids": internal_author_uuids
                    }

                    #research_ouput = dict(ResearchOutput(**output_detail))
                    await collection_details.insert_one(output_detail)

                await update_reads(collection_uuids, research_uuid)    

            else:
                await update_reads(collection_uuids, research_uuid)
    return 1   


async def update_reads(col, research_uuid):
    update = {"check_details":1}
    await col.find_one_and_update(
                                    {"research_uuid": research_uuid},
                                    {"$set": update}
                                )
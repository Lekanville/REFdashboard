import json
import os
import requests
from typing import List
from db.db_base import get_db_handle
from db.models.res_outputs import ResearchOutput

scopus_api_key = os.environ.get("SCOPUS_API_KEY")
pure_api_key = os.environ.get("PURE_API_KEY")


# For the all dependents to an organization
def all_research_outputs(school_uuid: str):
    """
    To get all dependents to an organization from the pure API
    :param uuid: The uuid of the research output
    """
    # Get the pure_id from the uuid
    req_pure = requests.get(
        f"https://research-information.bris.ac.uk/ws/api/organizations/{school_uuid}/dependents",
        headers={
            "accept": "application/json",
            "api-key": f"{pure_api_key}",
            "content-type": "application/json",
        }
    )

    if req_pure.status_code != 200:
        raise Exception(f"Error: {req_pure.status_code} - {req_pure.text}")
    else:
        data = req_pure.json()
        
        with open(f'{school_uuid}_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return data

# Research output UUIDS
def get_research_output_uuids(all_outputs: str):
    """
    To get the research output from all dependdents to an organization
    :param uuid: The uuid of the research output
    """
    research_output_uuids = []
    all_linked_outputs = all_outputs["items"]
    for i in all_linked_outputs:
        if i["systemName"] == "ResearchOutput":
            research_output_uuids.append(i["uuid"])

    research_output_len = len(research_output_uuids)
    print("The number of research outputs is: ", research_output_len)
    #return (research_output_len)

    return research_output_uuids

# Research output details from PURE
async def get_research_output_details(all_outputs: List[str], school_uuid: str):
    """
    To get the research output from the pure API
    :param uuids: The uuid of the research output
    """
    # output_details = []
    db_name = os.environ.get("DB_NAME", "")
    col_name = os.environ.get("RESEARCH_OUTPUT_COLLECTION", "")
    CLIENT = get_db_handle()
    database = CLIENT.get_database(db_name)
    collection = database.get_collection(col_name)
    
    for i, research_uuid in enumerate(all_outputs):
        query = {"research_uuid": research_uuid}
        article_count = await collection.count_documents(query)
        print (f'article at {i}')
        print (f'article count is {article_count}')

        if (article_count == 0):
            # Get the pure_id from the uuid
            req_pure = requests.post(
                "https://research-information.bris.ac.uk/ws/api/research-outputs/search",
                headers={
                    "accept": "application/json",
                    "api-key": f"{pure_api_key}",
                    "content-type": "application/json",
                },
                data=json.dumps({"uuids": [research_uuid]}),
            )

            if req_pure.status_code != 200:
                raise Exception(f"Error: {req_pure.status_code} - {req_pure.text}")
            else:
                data = req_pure.json()
                item = data["items"][0]
                article_type = item["typeDiscriminator"]
                year = item["publicationStatuses"][0]["publicationDate"]["year"]

                #if (article_type == "ContributionToJournal") & (int(year) > 2020):
                if (int(year) > 2020):
                    title = item["title"]["value"]

                    # Pure ID
                    try:
                        pure_id = item["pureId"]
                    except (IndexError, KeyError):
                        pure_id = ""

                    # Abstract
                    abstract = ""
                    if (abstract == "") | (str(abstract) == "None"):
                        try:
                            abstract = item["abstract"]["en_GB"]
                        except (IndexError, KeyError):
                            abstract = ""

                    if (abstract == "") | (str(abstract) == "None"):
                        try:
                            abstract = item["abstract"]["en_GB"]
                        except (IndexError, KeyError):
                            abstract = ""

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
                        ISSN = item["journalAssociation"]["issn"]["issn"]
                    except (IndexError, KeyError):
                        ISSN = ""   

                    # Contributors
                    authors = []
                    try:
                        contributors = item["contributors"]
                        for contributor in contributors:
                            fname = contributor["name"]["firstName"]
                            lname = contributor["name"]["lastName"]
                        #     if contributor["contributorType"] == "Author":
                        #         author = contributor["name"]
                        #         break
                            author = f"{fname} {lname}"
                            authors.append(author)
                    except (IndexError, KeyError):
                        authors = ""  

                    output_detail={
                        "research_uuid": research_uuid,
                        "school_uuid": school_uuid,
                        "pure_id": pure_id,
                        "article_type": article_type,
                        "title": title,
                        "year": year,
                        "abstract": abstract,
                        "doi": doi,
                        "issn": ISSN,
                        "authors": authors,
                    }

                    #research_ouput = dict(ResearchOutput(**output_detail))
                    await collection.insert_one(output_detail)
                    # output_details.append(output_detail)

                    # with open('output_details.json', 'w', encoding='utf-8') as f:
                    #     json.dump(output_details, f, ensure_ascii=False, indent=4)
    
    # if i == len(all_outputs):
    return 1   

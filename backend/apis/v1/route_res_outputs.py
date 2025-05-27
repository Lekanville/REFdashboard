from fastapi import APIRouter, HTTPException, status
from fastapi_utilities import repeat_every, repeat_at
#from schemas.pure_output import ResearchOutput
from db.repository.res_outputs_uuids import research_outputs_uuids
from db.repository.res_outputs_details import research_outputs_details
from db.repository.res_journal_features import research_journal_details
from db.repository.res_journal_authors import research_journal_authors
import yaml
from yaml.loader import SafeLoader

with open('../data.yaml') as file:
    schools = yaml.load(file, Loader=SafeLoader)


router = APIRouter()

@router.post("/api/research_uuids", status_code=status.HTTP_201_CREATED)
async def get_research_output_uuids(school_uuid: str):
    """
    To get the research output UUIDs from the pure server
    :param uuid: The uuid of the research output
    This gets the UUIDs for research ouputs and then saves them in the database. 
    All UUIDs are initailly assigned a "check_detail" value 0
    """
    # Get the all research for a school uuid from 2021
    response = await research_outputs_uuids(school_uuid)
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")

@router.get("/api/research_outputs/{school_uuid}", status_code=status.HTTP_201_CREATED)
async def get_research_output_details(school_uuid: str):
    """
    To get the research output details from the pure server
    :param uuid: The uuid of the research output

    This gets the details of the the research outputs (title, abstracts, etc). 
    It then updates "check_detail" value to 1
    """
    # Get the all research for a school uuid from 2021
    response = await research_outputs_details(school_uuid)
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")

@router.get("/api/journal_details/", status_code=status.HTTP_201_CREATED)
async def get_journal_features():
    """
    To get SJR and altmeric scores of the research articles
    """

    # Get journal features for articles after 2021
    response = await research_journal_details()
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")

@router.get("/api/authors_details/", status_code=status.HTTP_201_CREATED)
async def get_author_details():
    """
    To get the authors
    """

    # Get journal features for articles after 2021
    response = await research_journal_authors()
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")


@router.on_event("startup")
@repeat_every(seconds=60*60*60)  # 1 hour
async def get_research_output_uuids_automated():
    """
    This is the automated version of the "get_research_ouput_uuids" route. 
    The route is repeated as defined.

    To get the research output UUIDs from the pure server
    :param uuid: The uuid of the research output
    This gets the UUIDs for research ouputs and then saves them in the database. 
    All UUIDs are initailly assigned a "check_detail" value 0
    """

    #the schools
    for school in schools["schools"]:
        school_uuid = school["school_uuid"]
        print (school_uuid)
        # Get the all research for a school uuid from 2021
        response = await research_outputs_uuids(school_uuid)
        if response:
            return 1
        else:
            raise HTTPException(400, detail="Something went wrong")

@router.on_event("startup")
@repeat_every(seconds=60*60*60)  # 1 hour
async def get_research_output_details_automated():
    """
    This is the automated version of the "get_research_ouput_uuids" route. 
    The route is repeated as defined.

    To get the research output details from the pure server
    :param uuid: The uuid of the research output

    This gets the details of the the research outputs (title, abstracts, etc). 
    It then updates "check_detail" value to 1
    """

    #the schools
    for school in schools["schools"]:
        school_uuid = school["school_uuid"]
        print (school_uuid)
        # Get the all research for a school uuid from 2021
        response = await research_outputs_details(school_uuid)
        if response:
            return 1
        else:
            raise HTTPException(400, detail="Something went wrong")
    

@router.on_event("startup")
#@repeat_at(cron="0 12 1 * *") #every month at 12 noon
@repeat_every(seconds=60*60*60)  # 60 hours
async def get_journal_features_automated():
    """
    This is the automated version of the "get_journal_feature" route. 
    The route is repeated as defined.

    To get SJR and altmeric scores of the research articles
    """

    # Get journal features for articles after 2021
    response = await research_journal_details()
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")
    
import os
import datetime
from db.db_base import get_db_handle
from utils.journal_details.requests import pure_research_output_uuid
from db.models.res_outputs import ResearchOutputAuthors
@router.get("/api/get_authors/", status_code=status.HTTP_201_CREATED)
async def get_authors():
    db_name = os.environ.get("DB_NAME", "")
    res_output_col_name = os.environ.get("RESEARCH_OUTPUT_COLLECTION", "")
    res_output_authors = os.environ.get("RESEARCH_OUTPUT_AUTHORS", "")
    CLIENT = get_db_handle()
    database = CLIENT.get_database(db_name)
    collection = database.get_collection(res_output_col_name)
    res_output_authors_collection = database.get_collection(res_output_authors)

    research_outputs = await collection.find({}, {"_id":0, "research_uuid": 1, "external_author_uuids": 1, "internal_author_uuids":1}).to_list(100000)
    for research_output in research_outputs:
        research_output_uuid = research_output["research_uuid"]
        try:
            research_journal_title = research_output["external_author_uuids"]
        except KeyError:
            data = pure_research_output_uuid(research_output_uuid)
            item = data["items"][0]
            external_author_uuids = []
            try:
                contributors = item["contributors"]
                for contributor in contributors:
                    if contributor["typeDiscriminator"] == "ExternalContributorAssociation":
                        try:
                            external_author_uuid = contributor["externalPerson"]["uuid"]
                            external_author_uuids.append(external_author_uuid)
                        except(KeyError):
                            external_author_uuids = external_author_uuids
            except (IndexError, KeyError):
                external_author_uuids = external_author_uuids

        try:
            research_journal_title = research_output["internal_author_uuids"]
        except KeyError:
            data = pure_research_output_uuid(research_output_uuid)
            item = data["items"][0]
            internal_author_uuids = []
            try:
                contributors = item["contributors"]
                for contributor in contributors:
                    if contributor["typeDiscriminator"] == "InternalContributorAssociation":
                        try:
                            internal_author_uuid = contributor["person"]["uuid"]
                            internal_author_uuids.append(internal_author_uuid)
                        except(KeyError):
                            fname = contributor["name"]["firstName"]
                            lname = contributor["name"]["lastName"]
                            author_name = f"{fname} {lname}"
                            query = {"author_name": author_name}
                            author_count = await res_output_authors_collection.count_documents(query)
                            if (author_count == 0):
                                date = str(datetime.datetime.now())
                                author_detail={
                                        "author_uuid": "",
                                        "author_name": author_name,
                                        "uoa": "",
                                        "date":date
                                        }
                                journal_details = dict(ResearchOutputAuthors(author_detail))
                                await res_output_authors_collection.insert_one(journal_details)
                                internal_author_uuids = internal_author_uuids
            except (IndexError, KeyError):
                internal_author_uuids = internal_author_uuids

            update = {
                "external_author_uuids":external_author_uuids,
                "internal_author_uuids":internal_author_uuids
                }
            await collection.find_one_and_update(
                                        {"research_uuid": research_output_uuid},
                                        {"$set": update}
                                    )
    return 1                   

# import os
# from db.db_base import get_db_handle
# from utils.journal_details.requests import pure_research_output_uuid

# @router.get("/api/get_journal_titles/", status_code=status.HTTP_201_CREATED)
# async def get_research_ouput_journal_titles():
#     db_name = os.environ.get("DB_NAME", "")
#     res_output_col_name = os.environ.get("RESEARCH_OUTPUT_COLLECTION", "")
#     CLIENT = get_db_handle()
#     database = CLIENT.get_database(db_name)
#     collection = database.get_collection(res_output_col_name)

#     research_outputs = await collection.find({}, {"_id":0, "research_uuid": 1, "journal_title":1}).to_list(100000)

#     for research_output in research_outputs:
#         research_output_uuid = research_output["research_uuid"]
#         try:
#             research_journal_title = research_output["journal_title"]
#         except KeyError:
#             data = pure_research_output_uuid(research_output_uuid)
#             item = data["items"]

#             if len(item) > 0:
#                 values = data["items"][0]

#                 #Journal Title
#                 try:
#                     journal_title = values["journalAssociation"]["title"]["title"]
#                 except (IndexError, KeyError):
#                     journal_title = ""
#             else:
#                 journal_title = ""

#             update = {"journal_title":journal_title}
#             await collection.find_one_and_update(
#                                         {"research_uuid": research_output_uuid},
#                                         {"$set": update}
#                                     )
#     return 1
        


# @router.on_event("startup")
# @repeat_every(seconds=60*60)  # 1 hour
# async def get_new_research_outputs():
    # date = datetime.datetime.now()
    # print(date)
    # for school in schools["schools"]:
    #     print (school["school_name"])
    # for school in schools:
    #     print (school)
    # uuid_response = await research_outputs_uuids(school_uuid)
    # if uuid_response:
    #     pure_details_response = await research_outputs_details(school_uuid)
    #     if pure_details_response:
    #         return 1
    #     else:
    #         raise HTTPException(400, detail="Something went wrong")

    # else:
    #     raise HTTPException(400, detail="Something went wrong")

# @router.post("/api/research_time/", status_code=status.HTTP_201_CREATED)
# async def test_repeat():
    # date = datetime.datetime.now()
    # # print(date)
    # for school in schools["schools"]:
    #     print (school["school_name"])



# import os
# from db.db_base import get_db_handle

# @router.post("/api/journal_details/", status_code=status.HTTP_201_CREATED)
# async def get_unset():
#     db_name = os.environ.get("DB_NAME", "")
#     uuid_col_name = os.environ.get("RESEARCH_OUTPUT_UUIDS", "")
#     CLIENT = get_db_handle()
#     database = CLIENT.get_database(db_name)
#     collection = database.get_collection(uuid_col_name)
#     update =    {
#                 "journal_details": 1,
#                 "journal_details_date": 1
#             }
#     await collection.update_many({}, {"$unset": update})

#     return 1



# import datetime
# import os
# from db.db_base import get_db_handle

# @router.post("/api/journal_details/", status_code=status.HTTP_201_CREATED)
# async def get_journal_details():

#     db_name = os.environ.get("DB_NAME", "")
#     uuid_col_name = os.environ.get("RESEARCH_OUTPUT_UUIDS", "")
#     CLIENT = get_db_handle()
#     database = CLIENT.get_database(db_name)
#     collection = database.get_collection(uuid_col_name)
#     date = datetime.datetime.now()

#     research_outputs_uuids = await collection.find({}, {"_id":0, "research_uuid": 1}).to_list(100000)

#     for research_outputs_uuid in research_outputs_uuids:
#         research_uuid = research_outputs_uuid["research_uuid"]
#         update =    {
#                         "journal_details": 0,
#                         "journal_details_date":"None"
#                     }
#         await collection.find_one_and_update(
#                                     {"research_uuid": research_uuid},
#                                     {"$set": update}
#                                 )
#     return 1



# import datetime
# import os
# from db.db_base import get_db_handle

# @router.post("/api/research_time/", status_code=status.HTTP_201_CREATED)
# async def get_time():

#     db_name = os.environ.get("DB_NAME", "")
#     uuid_col_name = os.environ.get("RESEARCH_OUTPUT_UUIDS", "")
#     CLIENT = get_db_handle()
#     database = CLIENT.get_database(db_name)
#     collection = database.get_collection(uuid_col_name)
#     date = datetime.datetime.now()

#     research_outputs_uuids = await collection.find({}, {"_id":0, "research_uuid": 1}).to_list(100000)

#     for i in research_outputs_uuids:
#         research_uuid = i["research_uuid"]
#         update = {"check_details_date":date}
#         await collection.find_one_and_update(
#                                     {"research_uuid": research_uuid},
#                                     {"$set": update}
#                                 )
#     return 1


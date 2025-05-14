from fastapi import APIRouter, HTTPException, status
from fastapi_utils.tasks import repeat_every
#from schemas.pure_output import ResearchOutput
from db.repository.res_outputs_uuids import research_outputs_uuids
from db.repository.res_outputs_details import research_outputs_details



router = APIRouter()

@router.post("/api/research_uuids", status_code=status.HTTP_201_CREATED)
async def get_research_ouput_uuids(school_uuid: str):
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
async def get_research_ouput_details(school_uuid: str):
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

@router.on_event("startup")
@repeat_every(seconds=60 * 60)  # 1 hour
def remove_expired_tokens_task() -> None:
    with sessionmaker.context_session() as db:
        remove_expired_tokens(db=db)






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

#     for i in research_outputs_uuids:
#         research_uuid = i["research_uuid"]
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


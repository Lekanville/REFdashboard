import os
import json
from bson import ObjectId
from utils.research_outputs.research_outputs_utils import (get_research_output_details)
from db.db_base import get_db_handle

# For the pure requests
# async def research_outputs(school_uuid: str):
async def research_outputs_details(school_uuid: str):
    """
    To get the research output from the pure API
    :param uuid: The uuid of the research output
    """

    # #All dependents to an organization
    # all_outputs = all_research_outputs(school_uuid)
    # #Research output UUIDS
    # research_outputs_uuids = get_research_output_uuids(all_outputs)

    db_name = os.environ.get("DB_NAME", "")
    uuid_col_name = os.environ.get("RESEARCH_OUTPUT_UUIDS", "")
    CLIENT = get_db_handle()
    database = CLIENT.get_database(db_name)
    collection = database.get_collection(uuid_col_name)

    research_outputs_uuids = await collection.find({"school_uuid":school_uuid}, {"_id":0, "research_uuid": 1, "school_uuid": 1, "check_details":1}).to_list(100000)
    research_output_details = await get_research_output_details(research_outputs_uuids)

    if research_output_details:
        return 1




    # Research output details from PURE
    # with open(f'{school_uuid}_research_output_uuids.json', 'w', encoding='utf-8') as f:
    #     json.dump(research_outputs_uuids, f, ensure_ascii=False, indent=4)

    # research_output_details = await get_research_output_details(research_outputs_uuids)
    # if research_output_details:
    #     return 1

    # class JSONEncoder(json.JSONEncoder):
    #     def default(self, o):
    #         if isinstance(o, ObjectId):
    #             return str(o)
    #         return json.JSONEncoder.default(self, o)

    # research_outputs_encoded = JSONEncoder().encode(research_outputs_uuids)
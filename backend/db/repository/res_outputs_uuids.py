from utils.research_outputs.research_outputs_utils import (all_research_outputs, get_research_output_uuids)


# For the pure requests
async def research_outputs_uuids(school_uuid: str):
    """
    To get the research output UUIDS from the pure API
    :param uuid: The uuid of the research output
    This will get all dependents to an organization from pure, extract research outputs from it
    and store their UUIDs in the database. This ensures effective tracking of new articles
    """

    #All dependents to an organization
    all_outputs = all_research_outputs(school_uuid)
    
    #Research output UUIDS
    research_outputs_uuids = await get_research_output_uuids(school_uuid, all_outputs)

    if research_outputs_uuids:
        return 1

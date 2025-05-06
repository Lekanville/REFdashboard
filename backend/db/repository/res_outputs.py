from utils.research_outputs.all_outputs import (all_research_outputs, 
                                                get_research_output_uuids, 
                                                get_research_output_details)


# For the pure requests
async def research_outputs(school_uuid: str):
    """
    To get the research output from the pure API
    :param uuid: The uuid of the research output
    """

    #All dependents to an organization
    all_outputs = all_research_outputs(school_uuid)
    #Research output UUIDS
    research_outputs_uuids = get_research_output_uuids(all_outputs)
    # Research output details from PURE
    research_output_details = await get_research_output_details(research_outputs_uuids, school_uuid)
    if research_output_details:
        return 1

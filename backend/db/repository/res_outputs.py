from utils.research_outputs.all_outputs import all_research_outputs

# For the pure requests
def research_outputs(uuid: str):
    """
    To get the research output from the pure API
    :param uuid: The uuid of the research output
    """
    # Get the pure_id from the uuid

    all_outputs = all_research_outputs(uuid)

    #import this as research_output_uuids
    research_output_uuids = []
    all_linked_outputs = all_outputs["items"]
    for i in all_linked_outputs:
        if i["systemName"] == "ResearchOutput":
            research_output_uuids.append(i["uuid"])

    research_output_len = len(research_output_uuids)
    print("The number of research outputs is: ", research_output_len)
    #return (research_output_len)

    return 1

import json
import os
import requests

scopus_api_key = os.environ.get("SCOPUS_API_KEY")
pure_api_key = os.environ.get("PURE_API_KEY")


# For the pure requests
def all_research_outputs(uuid: str):
    """
    To get the research output from the pure API
    :param uuid: The uuid of the research output
    """
    # Get the pure_id from the uuid
    req_pure = requests.get(
        f"https://research-information.bris.ac.uk/ws/api/organizations/{uuid}/dependents",
        headers={
            "accept": "application/json",
            "api-key": f"{pure_api_key}",
            "content-type": "application/json",
        }
    )

    data = req_pure.json()

    if req_pure.status_code != 200:
        raise Exception(f"Error: {req_pure.status_code} - {req_pure.text}")
    else:
        data = req_pure.json()
        
        # with open('new_data.json', 'w', encoding='utf-8') as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)
        
        return data
    
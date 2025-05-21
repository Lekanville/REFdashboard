import json
import os
import requests

scopus_api_key = os.environ.get("SCOPUS_API_KEY")
pure_api_key = os.environ.get("PURE_API_KEY")

#to get all dependants to an organization
def organization_dependants(school_uuid: str):
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
        
        # with open(f'{school_uuid}_data.json', 'w', encoding='utf-8') as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)
        
        return data

def pure_research_output_uuid(research_uuid):
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
        return (data)


# For the pure requests
def pure_research_output(pure_id):
    req_pure = requests.post(
        "https://research-information.bris.ac.uk/ws/api/research-outputs/search",
        headers={
            "accept": "application/json",
            "api-key": f"{pure_api_key}",
            "content-type": "application/json",
        },
        data=json.dumps({"searchString": pure_id}),
    )
    data = req_pure.json()

    return data



# For scopus abstracts
def scopus_abstract(DOI):
    req_scopus = requests.get(
        f"https://api.elsevier.com/content/abstract/doi/{DOI}?apiKey={scopus_api_key}",
        headers={"accept": "application/json"},
    )
    data = req_scopus.json()

    return data


# For serial titiles (SJR, SNIP)
def scopus_titles(ISSN):
    req_snip = requests.get(
        f"https://api.elsevier.com/content/serial/title?issn={ISSN}&apiKey={scopus_api_key}"
    )
    data_issn = req_snip.json()["serial-metadata-response"]

    return data_issn

#for Author details
def author_details(author_uuid):
    req_pure = requests.post(
        "https://research-information.bris.ac.uk/ws/api/persons/search",
        headers={
            "accept": "application/json",
            "api-key": f"{pure_api_key}",
            "content-type": "application/json",
        },
        data=json.dumps({"uuids": [author_uuid]}),
    )

    if req_pure.status_code != 200:
        raise Exception(f"Error: {req_pure.status_code} - {req_pure.text}")
    else:
        data = req_pure.json()
        return (data)    
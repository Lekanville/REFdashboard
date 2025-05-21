import requests


def get_altmetric_score(DOI):
    req = requests.get(f"https://api.altmetric.com/v1/doi/{DOI}")
    """
    This exception handling is neccessary because some articles do not have altmetric scores. In this case,
    a null value is passed.
    """
    if req.status_code == 200:
        req_json = req.json()
        altmetric_score = req_json["score"]
        altmetric_data = {"altmetric_score": str(altmetric_score)}
    elif req.status_code == 404:
        altmetric_data = {"altmetric_score": "Not Available"}
    return altmetric_data

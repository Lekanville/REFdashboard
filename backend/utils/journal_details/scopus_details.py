import os
from utils.journal_details.requests import scopus_abstract, scopus_titles

def get_scopus_details(research_outputs_doi, research_output_journal_title, research_output_issn):
    data_abstracts = scopus_abstract(research_outputs_doi)

    # 1. Abstract
    """
    The exception handling below is necesssary because some journals do not have absract from the SCOPUS API.
    In any case of missing abstract, an empty string is returned
    """
    try:
        abstract = data_abstracts["abstracts-retrieval-response"]["item"]["bibrecord"][
            "head"
        ]["abstracts"]
    except KeyError:
            abstract = ""

    
    # 2. ISSN
    """
    Getting ISSN from scopus incase the one from PURE is missing or I could not get SJR with it
    The condition below is necesssary because some journals have multiple ISSN numbers.
    In any case of multiple ISSN numbers, select the print (some electronic ISSNs are missing)
    """
    try:
        ISSN_DATA = data_abstracts["abstracts-retrieval-response"]["item"]["bibrecord"][
            "head"
        ]["source"]["issn"]
    except KeyError:
        ISSN_DATA = ""
        issn_scopus = ""

    if (type(ISSN_DATA) is dict) & (ISSN_DATA != ""):
        issn_scopus = ISSN_DATA["$"]
    elif (type(ISSN_DATA) is list) & (ISSN_DATA != ""):
        for i in range(len(ISSN_DATA)):
            if ISSN_DATA[i]["@type"] == "print":
                issn_scopus = ISSN_DATA[i]["$"]

    # 3. Get SJR using the ISSN.First with PURE ISSN and then with SCOPUS ISSN

    #First with PURE ISSN
    if research_output_issn != "":
        PURE_issn_result = scopus_titles(research_output_issn)
        it = iter(PURE_issn_result)
        first, second = next(it), next(it)

        """
        The condition below is necesssary because some journals do not have SJR and SNIP scores using the ISSNs from SCOPUS abstracts.
        In such cases, the ISSN from the input data is used
        """
        if second == "entry":
            values = PURE_issn_result["entry"][0]
            try:
                sjr = values["SJRList"]["SJR"][0]["$"]
            except KeyError:
                sjr = ""
        else:
            sjr = ""
    else:
        sjr = ""

    #Second with SCOPUS ISSN
    if (sjr == "") & (issn_scopus != ""):
            SCOPUS_issn_result = scopus_titles(issn_scopus)
            it = iter(SCOPUS_issn_result)
            first, second = next(it), next(it)

            """
            The condition below is necesssary because some journals do not have SJR and SNIP scores using the ISSNs from SCOPUS abstracts.
            In such cases, the ISSN from the input data is used
            """
            if second == "entry":
                values = SCOPUS_issn_result["entry"][0]
                try:
                    sjr = values["SJRList"]["SJR"][0]["$"]
                except KeyError:
                    sjr = ""
            else:
                sjr = ""
    """
    Some journal (e.g. Cochrane Database of Systematic Reviews) do not have a SJR and SNIP scores on the scopus API.
    we however found a value for their SJR. Also Some articles are unclassified
    """
    Cochrane_Database_of_Systematic_Reviews = os.environ.get("Cochrane_Database_of_Systematic_Reviews")
    BMJ = os.environ.get("BMJ")
    Journals_of_Gerontology_Series_A= os.environ.get("Journals_of_Gerontology_Series_A")

    if (research_output_journal_title == "Cochrane Database of Systematic Reviews") & (sjr == ""):
        sjr = Cochrane_Database_of_Systematic_Reviews
    else:
        sjr = sjr

    # The article here doesnt have DOI
    if (research_output_journal_title == "BMJ") & (sjr == ""):
        sjr = BMJ
    else:
        sjr = sjr

    # The article here doesnt have the print DOI for abstract
    if (research_output_journal_title == "Journals of Gerontology, Series A") & (sjr == ""):
        sjr = Journals_of_Gerontology_Series_A
    else:
        sjr = sjr

    data = {
        "abstract": abstract,
        "sjr": sjr,
    }

    return data
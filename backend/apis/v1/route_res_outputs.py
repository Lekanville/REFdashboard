from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi_utilities import repeat_every, repeat_at
#from schemas.pure_output import ResearchOutput
from db.repository.res_outputs_uuids import research_outputs_uuids
from db.repository.res_outputs_details import research_outputs_details
from db.repository.res_journal_features import research_journal_details
from db.repository.res_journal_authors import research_journal_authors
from db.repository.res_download_data import download_research_data  
from db.repository.res_download_new_data import download_new_research_data
from db.repository.res_upload_predictions import upload_predictions_data
from db.repository.ref_embeddings import upload_ref_embedding_pcas
import yaml
from yaml.loader import SafeLoader
from fastapi.responses import StreamingResponse
import pandas as pd

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
    

@router.post("/api/download_all_research_data/", status_code=status.HTTP_201_CREATED)
async def get_download_data():
    """
    To download the wrangled data (research output abstracts, SJR, Altmetric etc) from the database.
    This is used to download the data for the research outputs, journal features, and authors.
    """

    response = await download_research_data()
    if response:
        return response
    else:
        raise HTTPException(400, detail="Something went wrong")
    

@router.post("/api/download_new_research_data/", status_code=status.HTTP_201_CREATED)
async def get_download_new_data():
    """
    To download the new wrangled data (research output abstracts, SJR, Altmetric etc) from the database.
    This is used to download the new data for the research outputs, abstracts, journal features (SJR and almetric scores).
    The new data is defined as the data that has been added to the database since the last download.
    The file will be saved in the CSV format.
    """
    
    response = await download_new_research_data()
    if response:
        return response
    else:
        raise HTTPException(400, detail="Something went wrong")

@router.post("/api/upload_predictions/", status_code=status.HTTP_201_CREATED)
async def get_upload_predictions(file: UploadFile = File(...)):
    """
    To upload the predictions data to the database.
    This is used to upload the predictions data for the research outputs.
    """

    predictions = await file.read()
    response = await upload_predictions_data(predictions)
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")
    

@router.post("/api/upload_ref_embedding_pcas/", status_code=status.HTTP_201_CREATED)
async def get_upload_ref_embedding_pcas(file: UploadFile = File(...)):
    """
    To upload the predictions REF embedding data to the database.
    This uploads the REF embedding data of the research output from other Universities
    """

    ref_data = await file.read()
    response = await upload_ref_embedding_pcas(ref_data)
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")


@router.on_event("startup")
@repeat_every(seconds=60*60*60)  # 60 hour
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
        # Get the all research for a school uuid from 2021
        response = await research_outputs_uuids(school_uuid)
        if response:
            return 1
        else:
            raise HTTPException(400, detail="Something went wrong")

@router.on_event("startup")
@repeat_every(seconds=60*60*60)  # 60 hour
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


@router.on_event("startup")
#@repeat_at(cron="0 12 1 * *") #every month at 12 noon
@repeat_every(seconds=60*60*60)  # 60 hours
async def get_author_details_automated():
    """
    To get the authors
    """

    # Get journal features for articles after 2021
    response = await research_journal_authors()
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")

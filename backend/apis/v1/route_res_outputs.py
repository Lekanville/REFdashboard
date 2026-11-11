from pathlib import Path

import yaml
from fastapi import APIRouter, File, Header, HTTPException, UploadFile, status
from fastapi_utilities import repeat_every
from yaml.loader import SafeLoader

from core.security import require_api_key
from db.repository.ref_embeddings import upload_ref_embedding_pcas
from db.repository.res_download_data import download_research_data
from db.repository.res_download_new_data import download_new_research_data
from db.repository.res_journal_authors import research_journal_authors
from db.repository.res_journal_features import research_journal_details
from db.repository.res_outputs_details import research_outputs_details
from db.repository.res_outputs_uuids import research_outputs_uuids
from db.repository.res_upload_predictions import upload_predictions_data

DATA_YAML = Path(__file__).resolve().parents[3] / "backend" / "data.yaml"
with DATA_YAML.open() as file:
    schools = yaml.load(file, Loader=SafeLoader)

STARTUP_TASKS_REGISTERED = set()


def register_startup_task(func):
    task_key = f"{func.__module__}:{func.__qualname__}"
    if task_key in STARTUP_TASKS_REGISTERED:
        return func
    STARTUP_TASKS_REGISTERED.add(task_key)
    return func


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
async def download_all_outputs_data(
    x_api_key: str | None = Header(default=None, alias="X-API-Key")
):
    """
    To download the wrangled data (research output abstracts, SJR, Altmetric etc) from the database.
    This will download the all the research outputs with journal features, and authors.
    """
    require_api_key(x_api_key)

    response = await download_research_data()
    if response:
        return response
    else:
        raise HTTPException(400, detail="Something went wrong")
    

@router.post("/api/download_new_research_data/", status_code=status.HTTP_201_CREATED)
async def download_new_outputs_data(
    x_api_key: str | None = Header(default=None, alias="X-API-Key")
):
    """
    To download the new wrangled data (research output abstracts, SJR, Altmetric etc) from the database.
    This is used to download the new data for the research outputs, abstracts, journal features (SJR and almetric scores).
    The new data is defined as the data that has been added to the database since the last download.
    The file will be saved in the CSV format. The outputs that were filtered during predictions (possibly out due to incomplete
    LLM features) will also be included.
    """
    
    require_api_key(x_api_key)

    response = await download_new_research_data()
    if response:
        return response
    else:
        raise HTTPException(400, detail="Something went wrong")

@router.post("/api/upload_predictions/", status_code=status.HTTP_201_CREATED)
async def upload_predictions(
    file: UploadFile = File(...),
    x_api_key: str | None = Header(default=None, alias="X-API-Key")
):
    """
    To upload the predictions data to the database.
    This is used to upload the predictions data for the research outputs.
    """

    require_api_key(x_api_key)

    predictions = await file.read()
    response = await upload_predictions_data(predictions)
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")
    

@router.post("/api/upload_ref_embedding_pcas/", status_code=status.HTTP_201_CREATED)
async def upload_ref_embedding(
    file: UploadFile = File(...),
    x_api_key: str | None = Header(default=None, alias="X-API-Key")
):
    """
    To upload the predictions REF embedding data to the database.
    This uploads the REF embedding data of the research output from other Universities
    """

    require_api_key(x_api_key)

    ref_data = await file.read()
    response = await upload_ref_embedding_pcas(ref_data)
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")


@register_startup_task
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

    # the schools
    for school in schools["schools"]:
        school_uuid = school["school_uuid"]
        response = await research_outputs_uuids(school_uuid)
        if not response:
            raise HTTPException(400, detail=f"Something went wrong for school {school_uuid}")

@register_startup_task
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

    # the schools
    for school in schools["schools"]:
        school_uuid = school["school_uuid"]
        response = await research_outputs_details(school_uuid)
        if not response:
            raise HTTPException(400, detail=f"Something went wrong for school {school_uuid}")
    

@register_startup_task
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


@register_startup_task
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

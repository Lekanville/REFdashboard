from fastapi import APIRouter, HTTPException, status
#from schemas.pure_output import ResearchOutput
from db.repository.res_outputs import research_outputs


router = APIRouter()

@router.get("/api/research_outputs/{school_uuid}", status_code=status.HTTP_201_CREATED)
async def get_research_ouput(school_uuid: str):
    """
    To get the research output from the pure API
    :param uuid: The uuid of the research output
    """
    # Get the all research for a school uuid from 2021
    response = await research_outputs(school_uuid)
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")

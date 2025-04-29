from fastapi import APIRouter, HTTPException, status
#from schemas.pure_output import ResearchOutput
from db.repository.res_outputs import research_outputs


router = APIRouter()

@router.get("/api/research_outputs/{uuid}", status_code=status.HTTP_201_CREATED)
def get_research_ouput(uuid: str):
    """
    To get the research output from the pure API
    :param uuid: The uuid of the research output
    """
    # Get the pure_id from the uuid
    response = research_outputs(uuid)
    if response:
        return 1
    else:
        raise HTTPException(400, detail="Something went wrong")

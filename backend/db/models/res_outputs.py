from pydantic import BaseModel

# Properties required for the research outputs
class ResearchOutput(BaseModel):
    Research_uuid: str
    School_uuid: str
    Pure_id: str | None = None
    Article_type: str
    Title: str
    Year: int
    Abstract: str | None = None
    DOI: str | None = None
    ISSN:  str | None = None
    Authors:  str | None = None

class ResearchJournalDetails(BaseModel):
    research_uuid: str
    sjr: str | None = None
    altmetric_score: str | None = None
    date: str

class ResearchOutputAuthors(BaseModel):
    author_uuid:str | None = None
    author_name: str 
    uoa: str | None = None
    date: str
    
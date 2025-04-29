from fastapi import APIRouter
from apis.v1 import (route_res_outputs)

api_router = APIRouter()
api_router.include_router(route_res_outputs.router, prefix="/v1", tags=["The research outputs"])

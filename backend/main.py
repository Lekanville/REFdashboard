from apis.api_base import api_router
from core.config import settings
from fastapi import FastAPI

# from fastapi.middleware.cors import CORSMiddleware

# from db.base import get_db_handle

# origins = [

#     "http://localhost:8501"
# ]


def include_router(app):
    app.include_router(api_router)


def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app)
    return app


app = start_application()

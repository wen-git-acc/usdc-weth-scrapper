import toml
from fastapi import FastAPI

from app.routes.api import router


def get_app() -> FastAPI:
    project_metadata = toml.load("pyproject.toml")["tool"]["poetry"]
    app = FastAPI(
        title=project_metadata["name"],
        version=project_metadata["version"],
        description=project_metadata["description"],
    )
    app.include_router(router)


    return app


app = get_app()

from pydantic import BaseModel, Field


class JobInput(BaseModel):
    user: str = Field(..., title="User")
    playlist_id: str = Field(..., title="spotify playlist id")
    project_name: str = Field(..., title="user set project/model name")
    num_threads: int = Field(..., title="number of threads")
    threshold: int = Field(..., title="letter distance warning threshold")
    debug: bool = Field(..., title="Debug verbose")






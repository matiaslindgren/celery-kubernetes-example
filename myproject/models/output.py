from pydantic import BaseModel, Field


class DataOutPut(BaseModel):
    out: dict = Field(..., title="Out data dict")

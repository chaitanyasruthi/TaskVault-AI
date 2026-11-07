from pydantic import BaseModel, Field
from typing import Optional, Any


class RunCreate(BaseModel):
    task: str = Field(min_length=5, max_length=2000)
    sandbox_name: str = Field(
        pattern=r"^sbx-[a-z0-9]{8,}$"
    )


class RunResponse(BaseModel):
    id: int
    sandbox_name: str
    task: str
    status: str
    execution_target: str
    result: Optional[Any] = None

    model_config = {"from_attributes": True}
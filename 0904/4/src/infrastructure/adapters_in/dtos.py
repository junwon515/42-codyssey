from datetime import date

from pydantic import BaseModel, ConfigDict


class TodoCreateRequest(BaseModel):
    task: str | None = None
    due_date: date | None = None


class TodoViewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task: str
    due_date: date | None = None
    is_completed: bool


class TodoItem(BaseModel):
    task: str
    due_date: date | None = None

from datetime import date, datetime

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


class QuestionCreateRequest(BaseModel):
    subject: str
    content: str


class QuestionUpdateRequest(BaseModel):
    subject: str
    content: str


class QuestionViewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    subject: str
    content: str
    create_date: datetime
    answers: list['AnswerViewResponse'] = []


class AnswerCreateRequest(BaseModel):
    content: str
    question_id: str


class AnswerUpdateRequest(BaseModel):
    content: str


class AnswerViewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    content: str
    create_date: datetime
    question_id: str

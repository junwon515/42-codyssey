from datetime import date, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, field_serializer

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(from_attributes=True)

    total_items: int
    items: list[T]
    page: int
    page_size: int


def mask_ip(ip: str) -> str:
    if not ip:
        return 'unknown'
    if ip in ('127.0.0.1', 'localhost'):
        return 'localhost'

    parts = ip.split('.')
    if len(parts) == 4:
        return f'{parts[0]}.{parts[1]}'
    return 'unknown'


class TodoViewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task: str
    due_date: date | None = None
    is_completed: bool
    creator_ip: str
    created_at: datetime
    updated_at: datetime | None = None

    @field_serializer('creator_ip')
    def serialize_ip(self, ip: str) -> str:
        return mask_ip(ip)

    @field_serializer('updated_at')
    def serialize_updated_at(self, updated_at: datetime | None) -> datetime | None:
        if updated_at == self.created_at:
            return None
        return updated_at


class TodoCreateRequest(BaseModel):
    task: str | None = None
    due_date: date | None = None
    password: str


class TodoUpdateRequest(BaseModel):
    task: str
    due_date: date | None = None
    password: str


class AnswerViewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    content: str
    question_id: str
    creator_ip: str
    parent_id: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    replies: list['AnswerViewResponse'] = []
    reply_count: int

    @field_serializer('creator_ip')
    def serialize_ip(self, ip: str) -> str:
        if self.deleted_at is not None:
            return 'deleted'
        return mask_ip(ip)

    @field_serializer('updated_at')
    def serialize_updated_at(self, updated_at: datetime | None) -> datetime | None:
        if updated_at == self.created_at:
            return None
        return updated_at

    @field_serializer('content')
    def serialize_content(self, content: str) -> str:
        if self.deleted_at is not None:
            return 'This answer has been deleted.'
        return content


class AnswerCreateRequest(BaseModel):
    content: str
    question_id: str
    parent_id: str | None = None
    password: str


class AnswerUpdateRequest(BaseModel):
    content: str
    password: str


class QuestionViewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    subject: str
    content: str
    creator_ip: str
    created_at: datetime
    updated_at: datetime | None = None
    answers: list[AnswerViewResponse] = []
    answer_count: int

    @field_serializer('creator_ip')
    def serialize_ip(self, ip: str) -> str:
        return mask_ip(ip)

    @field_serializer('updated_at')
    def serialize_updated_at(self, updated_at: datetime | None) -> datetime | None:
        if updated_at == self.created_at:
            return None
        return updated_at


class QuestionCreateRequest(BaseModel):
    subject: str
    content: str
    password: str


class QuestionUpdateRequest(BaseModel):
    subject: str
    content: str
    password: str


class AuthRequest(BaseModel):
    password: str


class AuthStatusResponse(BaseModel):
    is_admin: bool


class AdminDeletedItemsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    todos: PaginatedResponse[TodoViewResponse]
    questions: PaginatedResponse[QuestionViewResponse]
    answers: PaginatedResponse[AnswerViewResponse]

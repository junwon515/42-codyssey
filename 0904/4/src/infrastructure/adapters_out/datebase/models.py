from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    and_,
    func,
    select,
    text,
)
from sqlalchemy.orm import aliased, column_property, relationship
from src.infrastructure.core.database import Base


class TodoTable(Base):
    __tablename__ = 'todo'
    id = Column(String, primary_key=True, index=True)
    task = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    creator_ip = Column(String, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)


class AnswerTable(Base):
    __tablename__ = 'answer'
    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    creator_ip = Column(String, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    question_id = Column(
        String, ForeignKey('question.id', ondelete='CASCADE'), nullable=False
    )
    question = relationship('QuestionTable', back_populates='answers')

    parent_id = Column(
        String, ForeignKey('answer.id', ondelete='CASCADE'), nullable=True
    )

    replies = relationship(
        'AnswerTable',
        primaryjoin='foreign(AnswerTable.parent_id) == AnswerTable.id',
        back_populates='parent',
        cascade='all, delete-orphan',
        order_by='AnswerTable.created_at',
    )

    parent = relationship(
        'AnswerTable',
        remote_side=[id],
        back_populates='replies',
    )


class QuestionTable(Base):
    __tablename__ = 'question'
    id = Column(String, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    creator_ip = Column(String, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)

    answers = relationship(
        'AnswerTable',
        primaryjoin='and_(QuestionTable.id == AnswerTable.question_id, AnswerTable.parent_id == None)',
        back_populates='question',
        cascade='all, delete-orphan',
        order_by='AnswerTable.created_at',
    )

    answer_count = column_property(
        select(func.count(1))
        .where(and_(AnswerTable.question_id == id, AnswerTable.deleted_at.is_(None)))
        .correlate_except(text('QuestionTable'))
        .scalar_subquery()
    )


replies_alias = aliased(AnswerTable, name='replies_alias')

AnswerTable.reply_count = column_property(
    select(func.count(replies_alias.id))
    .where(
        and_(
            replies_alias.parent_id == AnswerTable.id,
            replies_alias.deleted_at.is_(None),
        )
    )
    .correlate_except(replies_alias)
    .scalar_subquery()
)

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import relationship
from src.infrastructure.core.database import Base


class TodoTable(Base):
    __tablename__ = 'todo'
    id = Column(String, primary_key=True, index=True)
    task = Column(String, nullable=False)
    due_date = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)


class QuestionTable(Base):
    __tablename__ = 'question'
    id = Column(String, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    create_date = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    answers = relationship(
        'AnswerTable', back_populates='question', cascade='all, delete-orphan'
    )


class AnswerTable(Base):
    __tablename__ = 'answer'
    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    create_date = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    question_id = Column(
        String, ForeignKey('question.id', ondelete='CASCADE'), nullable=False
    )
    question = relationship('QuestionTable', back_populates='answers')

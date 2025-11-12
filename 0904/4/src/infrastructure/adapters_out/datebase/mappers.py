from datetime import UTC

from sqlalchemy import inspect
from src.domain.models import Answer, Question, Todo
from src.infrastructure.adapters_out.datebase.daos import (
    AnswerTable,
    QuestionTable,
    TodoTable,
)


class TodoMapper:
    @staticmethod
    def to_domain(todo_table: TodoTable) -> Todo:
        return Todo(
            id=todo_table.id,
            task=todo_table.task,
            due_date=todo_table.due_date,
            is_completed=todo_table.is_completed,
            creator_ip=todo_table.creator_ip,
            created_at=todo_table.created_at.replace(tzinfo=UTC),
            updated_at=todo_table.updated_at.replace(tzinfo=UTC),
            password_hash=todo_table.password_hash,
        )

    @staticmethod
    def to_table(todo: Todo) -> TodoTable:
        return TodoTable(
            id=todo.id,
            task=todo.task,
            due_date=todo.due_date,
            is_completed=todo.is_completed,
            creator_ip=todo.creator_ip,
            password_hash=todo.password_hash,
        )

    @staticmethod
    def update_table_from_domain(todo: Todo, todo_table: TodoTable) -> None:
        todo_table.task = todo.task
        todo_table.due_date = todo.due_date
        todo_table.is_completed = todo.is_completed


class QuestionMapper:
    @staticmethod
    def to_domain(question_table: QuestionTable) -> Question:
        domain_answers = []
        sa_instance_state = inspect(question_table)

        if 'answers' not in sa_instance_state.unloaded:
            domain_answers = [
                AnswerMapper.to_domain(ans_table)
                for ans_table in question_table.answers
            ]

        return Question(
            id=question_table.id,
            subject=question_table.subject,
            content=question_table.content,
            creator_ip=question_table.creator_ip,
            created_at=question_table.created_at.replace(tzinfo=UTC),
            updated_at=question_table.updated_at.replace(tzinfo=UTC),
            answers=domain_answers,
            answer_count=question_table.answer_count,
            password_hash=question_table.password_hash,
        )

    @staticmethod
    def to_table(question: Question) -> QuestionTable:
        return QuestionTable(
            id=question.id,
            subject=question.subject,
            content=question.content,
            creator_ip=question.creator_ip,
            password_hash=question.password_hash,
        )

    @staticmethod
    def update_table_from_domain(
        question: Question, question_table: QuestionTable
    ) -> None:
        question_table.subject = question.subject
        question_table.content = question.content


class AnswerMapper:
    @staticmethod
    def to_domain(answer_table: AnswerTable) -> Answer:
        domain_replies = []
        sa_instance_state = inspect(answer_table)

        if 'replies' not in sa_instance_state.unloaded:
            domain_replies = [
                AnswerMapper.to_domain(reply_table)
                for reply_table in answer_table.replies
            ]

        return Answer(
            id=answer_table.id,
            content=answer_table.content,
            question_id=answer_table.question_id,
            creator_ip=answer_table.creator_ip,
            parent_id=answer_table.parent_id,
            created_at=answer_table.created_at.replace(tzinfo=UTC),
            updated_at=answer_table.updated_at.replace(tzinfo=UTC),
            deleted_at=answer_table.deleted_at.replace(tzinfo=UTC)
            if answer_table.deleted_at
            else None,
            replies=domain_replies,
            reply_count=answer_table.reply_count,
            password_hash=answer_table.password_hash,
        )

    @staticmethod
    def to_table(answer: Answer) -> AnswerTable:
        return AnswerTable(
            id=answer.id,
            content=answer.content,
            question_id=answer.question_id,
            creator_ip=answer.creator_ip,
            parent_id=answer.parent_id,
            password_hash=answer.password_hash,
        )

    @staticmethod
    def update_table_from_domain(answer: Answer, answer_table: AnswerTable) -> None:
        answer_table.content = answer.content

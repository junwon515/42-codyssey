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
        )

    @staticmethod
    def to_table(todo: Todo) -> TodoTable:
        return TodoTable(
            id=todo.id,
            task=todo.task,
            due_date=todo.due_date,
            is_completed=todo.is_completed,
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
            create_date=question_table.create_date,
            answers=domain_answers,
        )

    @staticmethod
    def to_table(question: Question) -> QuestionTable:
        return QuestionTable(
            id=question.id,
            subject=question.subject,
            content=question.content,
            create_date=question.create_date,
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
        return Answer(
            id=answer_table.id,
            content=answer_table.content,
            create_date=answer_table.create_date,
            question_id=answer_table.question_id,
        )

    @staticmethod
    def to_table(answer: Answer) -> AnswerTable:
        return AnswerTable(
            id=answer.id,
            content=answer.content,
            create_date=answer.create_date,
            question_id=answer.question_id,
        )

    @staticmethod
    def update_table_from_domain(answer: Answer, answer_table: AnswerTable) -> None:
        answer_table.content = answer.content

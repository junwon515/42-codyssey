import contextlib
import sys
from datetime import datetime

import requests

BASE_URL = 'http://127.0.0.1:8000/api/v1'


# --- [ Helper Functions ] ---


def print_todo(todo):
    print(f"  ID: {todo['id']}")
    print(f"  Task: {todo['task']}")
    print(f"  Due: {todo.get('due_date', 'N/A')}")
    print(f"  Completed: {todo['is_completed']}")
    print('-' * 20)


def print_question(question, show_answers=True):
    print(f"  ID: {question['id']}")
    print(f"  Subject: {question['subject']}")
    print(f"  Content: {question['content']}")
    print(f"  Created: {format_datetime(question['create_date'])}")

    if show_answers and 'answers' in question:
        print(f"  Answers ({len(question['answers'])}):")
        if not question['answers']:
            print('    (답변이 없습니다)')
        for answer in question['answers']:
            print_answer(answer, indent='    ')
    print('-' * 20)


def print_answer(answer, indent='  '):
    print(f"{indent}ID: {answer['id']}")
    print(f"{indent}Content: {answer['content']}")
    print(f"{indent}Created: {format_datetime(answer['create_date'])}")
    print(f"{indent}Q_ID: {answer['question_id']}")
    print(f"{indent}{'-' * 15}")


def format_datetime(dt_str):
    if not dt_str:
        return 'N/A'
    # '2025-11-09T23:43:38.525131+00:00' 또는 'Z' 처리
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return dt_str


def handle_connection_error(e):
    if isinstance(e, requests.exceptions.ConnectionError):
        print('\n' + '=' * 40)
        print('  [치명적 오류] FastAPI 서버에 연결할 수 없습니다.')
        print(f"  '{BASE_URL}' 주소에서 서버가 실행 중인지 확인하세요.")
        print('=' * 40 + '\n')
    else:
        print(f'\n  [알 수 없는 오류] {e}')


def handle_http_error(response, resource_name='Resource', resource_id=None):
    id_str = f' (ID: {resource_id})' if resource_id else ''

    if response.status_code == 404:
        print(f'  [오류] {resource_name}{id_str}을(를) 찾을 수 없습니다.')
    elif response.status_code == 422:
        print('  [오류] 입력 데이터 형식이 잘못되었습니다.')
        with contextlib.suppress(requests.JSONDecodeError):
            print(response.json())
    elif response.status_code == 400:
        print('  [오류] 잘못된 요청입니다 (400).')
        with contextlib.suppress(requests.JSONDecodeError):
            print(response.json())
    else:
        response.raise_for_status()


# --- [ Todo Functions ] ---


def view_all_todos():
    print('\n--- [ 1. 모든 Todo 조회 ] ---')
    try:
        response = requests.get(f'{BASE_URL}/todo/')
        response.raise_for_status()

        todos = response.json()
        if not todos:
            print('  등록된 Todo가 없습니다.')
            return

        for todo in todos:
            print_todo(todo)

    except requests.exceptions.HTTPError as e:
        print(f'  [오류] 데이터를 가져오는데 실패했습니다: {e.response.status_code}')
    except Exception as e:
        handle_connection_error(e)


def view_single_todo():
    print('\n--- [ 2. 개별 Todo 조회 ] ---')
    todo_id = input('  조회할 Todo의 ID를 입력하세요: ').strip()
    if not todo_id:
        print('  [오류] ID를 입력해야 합니다.')
        return

    try:
        response = requests.get(f'{BASE_URL}/todo/{todo_id}')
        handle_http_error(response, 'Todo', todo_id)

        print('  [조회 성공]')
        print_todo(response.json())

    except requests.exceptions.HTTPError:
        pass  # handle_http_error가 이미 처리
    except Exception as e:
        handle_connection_error(e)


def create_todo():
    print('\n--- [ 3. 새 Todo 생성 ] ---')
    task = input('  Task 내용을 입력하세요: ').strip()
    if not task:
        print('  [오류] Task 내용은 필수입니다.')
        return

    due_date = input('  Due Date (YYYY-MM-DD, 비워두면 None): ').strip()
    if not due_date:
        due_date = None

    payload = {'task': task, 'due_date': due_date}

    try:
        response = requests.post(f'{BASE_URL}/todo/', json=payload)
        handle_http_error(response)

        print('  [생성 성공]')
        print_todo(response.json())

    except requests.exceptions.HTTPError:
        pass
    except Exception as e:
        handle_connection_error(e)


def update_todo():
    print('\n--- [ 4. Todo 수정 ] ---')
    todo_id = input('  수정할 Todo의 ID를 입력하세요: ').strip()
    if not todo_id:
        print('  [오류] ID를 입력해야 합니다.')
        return

    print('  [수정할 새 내용을 입력하세요 (TodoItem 모델)]')
    task = input('  New Task (필수): ').strip()
    if not task:
        print('  [오류] Task 내용은 필수입니다.')
        return

    due_date = input('  New Due Date (YYYY-MM-DD, 비워두면 None): ').strip()
    if not due_date:
        due_date = None

    payload = {'task': task, 'due_date': due_date}

    try:
        response = requests.put(f'{BASE_URL}/todo/{todo_id}', json=payload)
        handle_http_error(response, 'Todo', todo_id)

        print('  [수정 성공]')
        print_todo(response.json())

    except requests.exceptions.HTTPError:
        pass
    except Exception as e:
        handle_connection_error(e)


def delete_todo():
    print('\n--- [ 5. Todo 삭제 ] ---')
    todo_id = input('  삭제할 Todo의 ID를 입력하세요: ').strip()
    if not todo_id:
        print('  [오류] ID를 입력해야 합니다.')
        return

    try:
        response = requests.delete(f'{BASE_URL}/todo/{todo_id}')

        if response.status_code == 204:
            print(f'  [삭제 성공] ID({todo_id}) Todo가 삭제되었습니다.')
        else:
            handle_http_error(response, 'Todo', todo_id)

    except requests.exceptions.HTTPError:
        pass
    except Exception as e:
        handle_connection_error(e)


# --- [ Question & Answer Functions ] ---


def view_all_questions():
    print('\n--- [ 6. 모든 Question 조회 ] ---')
    try:
        response = requests.get(f'{BASE_URL}/question/')
        response.raise_for_status()

        questions = response.json()
        if not questions:
            print('  등록된 질문이 없습니다.')
            return

        print(f'  [총 {len(questions)}개의 질문 조회]')
        for question in questions:
            # 전체 목록에서는 답변을 간략히 표시
            print_question(question, show_answers=False)
            print(f"    (Answers: {len(question.get('answers', []))})")
            print('-' * 20)

    except requests.exceptions.HTTPError as e:
        print(f'  [오류] 데이터를 가져오는데 실패했습니다: {e.response.status_code}')
    except Exception as e:
        handle_connection_error(e)


def view_single_question():
    print('\n--- [ 7. 개별 Question 조회 (답변 포함) ] ---')
    question_id = input('  조회할 Question의 ID를 입력하세요: ').strip()
    if not question_id:
        print('  [오류] ID를 입력해야 합니다.')
        return

    try:
        response = requests.get(f'{BASE_URL}/question/{question_id}')
        handle_http_error(response, 'Question', question_id)

        print('  [조회 성공]')
        print_question(response.json(), show_answers=True)

    except requests.exceptions.HTTPError:
        pass
    except Exception as e:
        handle_connection_error(e)


def create_question():
    print('\n--- [ 8. 새 Question 생성 ] ---')
    subject = input('  제목을 입력하세요: ').strip()
    content = input('  내용을 입력하세요: ').strip()

    if not subject or not content:
        print('  [오류] 제목과 내용은 필수입니다.')
        return

    payload = {'subject': subject, 'content': content}

    try:
        response = requests.post(f'{BASE_URL}/question/', json=payload)
        handle_http_error(response)

        print('  [생성 성공]')
        print_question(response.json())

    except requests.exceptions.HTTPError:
        pass
    except Exception as e:
        handle_connection_error(e)


def create_answer():
    print('\n--- [ 9. 새 Answer 생성 ] ---')
    question_id = input('  답변을 달 Question의 ID를 입력하세요: ').strip()
    if not question_id:
        print('  [오류] Question ID는 필수입니다.')
        return

    content = input('  답변 내용을 입력하세요: ').strip()
    if not content:
        print('  [오류] 답변 내용은 필수입니다.')
        return

    payload = {'content': content, 'question_id': question_id}

    try:
        response = requests.post(f'{BASE_URL}/answer/', json=payload)
        # 404 (Question not found) 또는 422 (Validation error)
        handle_http_error(response)

        print('  [생성 성공]')
        print_answer(response.json())

    except requests.exceptions.HTTPError:
        pass
    except Exception as e:
        handle_connection_error(e)


def delete_question():
    print('\n--- [ 10. Question 삭제 ] ---')
    question_id = input('  삭제할 Question의 ID를 입력하세요: ').strip()
    if not question_id:
        print('  [오류] ID를 입력해야 합니다.')
        return

    try:
        response = requests.delete(f'{BASE_URL}/question/{question_id}')

        if response.status_code == 204:
            print(f'  [삭제 성공] ID({question_id}) Question이 삭제되었습니다.')
        else:
            handle_http_error(response, 'Question', question_id)

    except requests.exceptions.HTTPError:
        pass
    except Exception as e:
        handle_connection_error(e)


def delete_answer():
    print('\n--- [ 11. Answer 삭제 ] ---')
    answer_id = input('  삭제할 Answer의 ID를 입력하세요: ').strip()
    if not answer_id:
        print('  [오류] ID를 입력해야 합니다.')
        return

    try:
        response = requests.delete(f'{BASE_URL}/answer/{answer_id}')

        if response.status_code == 204:
            print(f'  [삭제 성공] ID({answer_id}) Answer가 삭제되었습니다.')
        else:
            handle_http_error(response, 'Answer', answer_id)

    except requests.exceptions.HTTPError:
        pass
    except Exception as e:
        handle_connection_error(e)


# --- [ Main Menu ] ---


def print_menu():
    print('\n===== FastAPI Todo/Q&A Client =====')
    print(' [ Todo ]')
    print('  1. 모든 Todo 조회')
    print('  2. 개별 Todo 조회')
    print('  3. 새 Todo 생성')
    print('  4. Todo 수정')
    print('  5. Todo 삭제')
    print(' ---------------------------------')
    print(' [ Question & Answer ]')
    print('  6. 모든 Question 조회')
    print('  7. 개별 Question 조회 (답변 포함)')
    print('  8. 새 Question 생성')
    print('  9. 새 Answer 생성 (질문 ID 필요)')
    print(' 10. Question 삭제 (답변도 함께 삭제될 수 있음 - DB설정따라)')
    print(' 11. Answer 삭제')
    print(' ---------------------------------')
    print('  q. 종료')
    print('===================================')
    return input('  선택: ').strip()


def main():
    while True:
        choice = print_menu()

        if choice == '1':
            view_all_todos()
        elif choice == '2':
            view_single_todo()
        elif choice == '3':
            create_todo()
        elif choice == '4':
            update_todo()
        elif choice == '5':
            delete_todo()
        elif choice == '6':
            view_all_questions()
        elif choice == '7':
            view_single_question()
        elif choice == '8':
            create_question()
        elif choice == '9':
            create_answer()
        elif choice == '10':
            delete_question()
        elif choice == '11':
            delete_answer()
        elif choice.lower() == 'q':
            print('  클라이언트를 종료합니다.')
            sys.exit(0)
        else:
            print('  [오류] 메뉴에 있는 숫자나 "q"를 입력하세요.')


if __name__ == '__main__':
    main()

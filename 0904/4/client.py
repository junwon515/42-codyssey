import sys

import requests

BASE_URL = 'http://127.0.0.1:8000/api/v1'


def print_todo(todo):
    print(f"  ID: {todo['id']}")
    print(f"  Task: {todo['task']}")
    print(f"  Due: {todo.get('due_date', 'N/A')}")
    print(f"  Completed: {todo['is_completed']}")
    print('-' * 20)


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

        if response.status_code == 404:
            print(f'  [오류] ID({todo_id})를 가진 Todo를 찾을 수 없습니다.')
        else:
            response.raise_for_status()
            print('  [조회 성공]')
            print_todo(response.json())

    except requests.exceptions.HTTPError as e:
        print(f'  [오류] 조회 실패: {e.response.status_code}')
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

        if response.status_code == 422:
            print(f'  [오류] 입력 데이터 형식이 잘못되었습니다 (날짜: {due_date})')
            print(response.json())
        else:
            response.raise_for_status()
            print('  [생성 성공]')
            print_todo(response.json())

    except requests.exceptions.HTTPError as e:
        print(f'  [오류] 생성 실패: {e.response.status_code}')
    except Exception as e:
        handle_connection_error(e)


def update_todo():
    print('\n--- [ 4. Todo 수정 ] ---')
    todo_id = input('  수정할 Todo의 ID를 입력하세요: ').strip()
    if not todo_id:
        print('  [오류] ID를 입력해야 합니다.')
        return

    print('  [수정할 새 내용을 입력하세요 (TodoItem 모델)]')
    task = input('  New Task (기존값 유지 시 비워두지 마세요): ').strip()
    if not task:
        print('  [오류] Task 내용은 필수입니다.')
        return

    due_date = input('  New Due Date (YYYY-MM-DD, 비워두면 None): ').strip()
    if not due_date:
        due_date = None

    payload = {'task': task, 'due_date': due_date}

    try:
        response = requests.put(f'{BASE_URL}/todo/{todo_id}', json=payload)

        if response.status_code == 404:
            print(f'  [오류] ID({todo_id})를 가진 Todo를 찾을 수 없습니다.')
        elif response.status_code == 422:
            print(f'  [오류] 입력 데이터 형식이 잘못되었습니다 (날짜: {due_date})')
        else:
            response.raise_for_status()
            print('  [수정 성공]')
            print_todo(response.json())

    except requests.exceptions.HTTPError as e:
        print(f'  [오류] 수정 실패: {e.response.status_code}')
    except Exception as e:
        handle_connection_error(e)


def delete_todo():
    """(DELETE /{id}) Todo 항목을 삭제합니다."""
    print('\n--- [ 5. Todo 삭제 ] ---')
    todo_id = input('  삭제할 Todo의 ID를 입력하세요: ').strip()
    if not todo_id:
        print('  [오류] ID를 입력해야 합니다.')
        return

    try:
        response = requests.delete(f'{BASE_URL}/todo/{todo_id}')

        if response.status_code == 404:
            print(f'  [오류] ID({todo_id})를 가진 Todo를 찾을 수 없습니다.')
        elif response.status_code == 204:
            print(f'  [삭제 성공] ID({todo_id}) Todo가 삭제되었습니다.')
        else:
            response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        print(f'  [오류] 삭제 실패: {e.response.status_code}')
    except Exception as e:
        handle_connection_error(e)


def handle_connection_error(e):
    if isinstance(e, requests.exceptions.ConnectionError):
        print('\n' + '=' * 40)
        print('  [치명적 오류] FastAPI 서버에 연결할 수 없습니다.')
        print(f"  '{BASE_URL}' 주소에서 서버가 실행 중인지 확인하세요.")
        print('=' * 40 + '\n')
    else:
        print(f'\n  [알 수 없는 오류] {e}')


def print_menu():
    print('\n===== FastAPI Todo Client =====')
    print(' 1. 모든 Todo 조회')
    print(' 2. 개별 Todo 조회')
    print(' 3. 새 Todo 생성')
    print(' 4. Todo 수정')
    print(' 5. Todo 삭제')
    print(' 6. 종료')
    print('===============================')
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
        elif choice == '6' or choice.lower() == 'q':
            print('  클라이언트를 종료합니다.')
            sys.exit(0)
        else:
            print('  [오류] 1-6 사이의 숫자를 입력하세요.')


if __name__ == '__main__':
    main()

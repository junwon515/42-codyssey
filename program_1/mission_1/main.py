print('\nHello Mars')

# 파일 경로 설정
PARENT_PATH = 'program_1/mission_1/'
MAIN_LOG_PATH = PARENT_PATH + 'mission_computer_main.log'
ISSUE_LOG_PATH = PARENT_PATH + 'mission_computer_issue.log'
JSON_LOG_PATH = PARENT_PATH + 'mission_computer_main.json'


def process_logs(log_file):
    """로그 파일을 처리하는 함수"""
    try:
        with open(log_file, encoding='utf-8') as f:
            logs = (line.strip() for line in f if line.strip())
            logs = list(logs)

        if not logs:
            print('❌ No logs found.')
            return

        # 로그 출력
        print('\n=== Log Output ===')
        print('\n'.join(logs))

        print('\n=== Log Output (Reversed) ===')
        print('\n'.join(reversed(logs)))

        # 문제 로그 저장 (마지막 3개)
        save_issue_logs(logs[-3:])

        # CSV 파싱 및 JSON 변환
        convert_logs_to_json(logs)

        print('\n✅ Processing completed successfully!')

    except FileNotFoundError:
        print(f'❌ Error: Log file "{log_file}" not found.')
    except PermissionError:
        print(f'❌ Error: No permission to access "{log_file}".')
    except Exception as e:
        print(f'❌ An unexpected error occurred: {e}')


def save_issue_logs(issue_logs):
    """문제가 된 로그를 별도 저장하는 함수"""
    try:
        with open(ISSUE_LOG_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(issue_logs) + '\n')
        print('\n✅ Issue log saved successfully!')
    except Exception as e:
        print(f'❌ Failed to save issue logs: {e}')


def convert_logs_to_json(logs):
    """로그를 CSV 파싱하여 JSON으로 변환 후 저장하는 함수"""
    try:
        # CSV 파싱
        csv_logs = [log.split(',') for log in logs]

        if not csv_logs or len(csv_logs) < 2:
            print('❌ Not enough data to convert to JSON.')
            return

        # CSV 로그 출력
        print('\n=== CSV Logs ===')
        print('\n'.join([str(log) for log in csv_logs]))

        # 시간 내림차순 정렬
        csv_logs.sort(key=lambda x: x[0], reverse=True)

        # DICT 변환
        headers, *data_rows = csv_logs
        json_logs = [dict(zip(headers, row, strict=False)) for row in data_rows]

        # JSON 포맷팅
        json_content = (
            '[\n'
            + ',\n'.join(
                [
                    '  {\n'
                    + ',\n'.join(
                        [f'    "{key}": "{value}"' for key, value in log.items()]
                    )
                    + '\n  }'
                    for log in json_logs
                ]
            )
            + '\n]'
        )

        # 로그 JSON 파일 저장
        with open(JSON_LOG_PATH, 'w', encoding='utf-8') as f:
            f.write(json_content)

        print('\n✅ JSON file created successfully!')

    except Exception as e:
        print(f'❌ Failed to convert logs to JSON: {e}')


if __name__ == '__main__':
    process_logs(MAIN_LOG_PATH)

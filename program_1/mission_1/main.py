print('\nHello Mars')

# 파일 경로 설정
parent_path = 'program_1/mission_1/'
main_log_path = parent_path + 'mission_computer_main.log'
issue_log_path = parent_path + 'mission_computer_issue.log'

def read_log(main_log_path) :
    try:
        # 로그 파일 읽기
        with open(main_log_path, 'r', encoding='utf-8') as f:
            log_lines = f.readlines()

        # 로그 전체 출력
        print('\n=== Log Output ===')
        print(''.join(log_lines))

        # 로그 역순 출력
        print('\n=== Log Output (Reversed) ===')
        print(''.join(reversed(log_lines)))

        # 문제가 되는 로그 저장
        with open(issue_log_path, 'w', encoding='utf-8') as f:
            f.writelines(log_lines[-3:])

        print('\n✅ Processing completed successfully!')

    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f'❌ Error: {e}')
    except Exception as e:
        print(f'❌ An unexpected error occurred: {e}')

if __name__ == '__main__' :
    read_log(main_log_path)
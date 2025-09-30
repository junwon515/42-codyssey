# 파일 경로 설정
PARENT_PATH = '0304/1-3/'
INVENTORY_LIST_PATH = PARENT_PATH + 'Mars_Base_Inventory_List.csv'
INVENTORY_DANGER_PATH = PARENT_PATH + 'Mars_Base_Inventory_danger.csv'
BIN_INVENTORY_LIST_PATH = PARENT_PATH + 'Mars_Base_Inventory_List.bin'


def read_csv(file_path):
    """CSV 파일을 읽어 리스트로 변환"""
    try:
        with open(file_path, encoding='utf-8') as f:
            return [line.strip().split(',') for line in f if line.strip()]
    except FileNotFoundError:
        print(f'❌ Error: CSV file "{file_path}" not found.')
    except PermissionError:
        print(f'❌ Error: No permission to access "{file_path}".')
    except Exception as e:
        print(f'❌ An unexpected error occurred: {e}')
    return []


def write_csv(file_path, data):
    """데이터를 CSV 파일로 저장"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for row in data:
                f.write(','.join(row) + '\n')
    except Exception as e:
        print(f'❌ Failed to write CSV file: {e}')


def convert_csv_to_bin(file_path, data):
    """데이터를 이진 파일로 저장하고 출력"""
    try:
        with open(file_path, 'wb') as f:
            for row in data:
                f.write((','.join(row) + '\n').encode('utf-8'))

        with open(file_path, 'rb') as f:
            print('\n📦 Binary Mars Base Inventory List')
            print(f.read())

        print('\n✅ Binary file created successfully!')
    except Exception as e:
        print(f'❌ Failed to convert CSV to BIN: {e}')


def main():
    """메인 함수"""
    csv_data = read_csv(INVENTORY_LIST_PATH)

    if not csv_data:
        print('❌ No data found.')
        return

    print('\n📦 Mars Base Inventory List')
    for row in csv_data:
        print(', '.join(row))

    # 위험 목록 생성
    headers, *data_rows = csv_data
    try:
        data_rows.sort(key=lambda x: float(x[4]), reverse=True)
        danger_data = [headers] + [row for row in data_rows if float(row[4]) >= 0.7]
    except ValueError:
        print('❌ Error: The value in the "Current Stock" column is not a number.')

    print('\n🔥 Mars Base Inventory Danger List')
    for row in danger_data:
        print(', '.join(row))

    # 위험 목록을 CSV 파일로 저장
    write_csv(INVENTORY_DANGER_PATH, danger_data)

    # 정렬된 데이터를 이진 파일로 저장
    convert_csv_to_bin(BIN_INVENTORY_LIST_PATH, [headers] + data_rows)

    print('\n✅ Processing completed successfully!')


if __name__ == '__main__':
    main()

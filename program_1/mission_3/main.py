# 파일 경로 설정
PARENT_PATH = 'program_1/mission_3/'
INVENTORY_LIST_PATH = PARENT_PATH + 'Mars_Base_Inventory_List.csv'
INVENTORY_DANGER_PATH = PARENT_PATH + 'Mars_Base_Inventory_danger.csv'
BIN_INVENTORY_LIST_PATH = PARENT_PATH + 'Mars_Base_Inventory_List.bin'

def main(file_path):
    """ 메인 함수 """
    try:
        # CSV 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_data = (line.strip().split(',') for line in f if line.strip())
            csv_data = list(csv_data)
        
        if not csv_data:
            print('❌ No data found.')
            return
        
        # CSV 데이터 출력
        print('\n📦 Mars Base Inventory List')
        for row in csv_data:
            print(', '.join(row))

        # 인화성 내림차순 정렬
        csv_data.sort(key=lambda x: x[4], reverse=True)

        # CSV 데이터를 바이너리 파일로 변환
        convert_csv_to_bin(csv_data)

        # 인화성 0.7 이상인 데이터만 추출 및 출력
        headers, *data_rows = csv_data
        danger_data = [headers] + [row for row in data_rows if float(row[4]) >= 0.7]

        print('\n🔥 Mars Base Inventory Danger List')
        for row in danger_data:
            print(', '.join(row))

        # CSV 파일 쓰기
        with open(INVENTORY_DANGER_PATH, 'w', encoding='utf-8') as f:
            for row in danger_data:
                f.write(','.join(row) + '\n')

        print('\n✅ Processing completed successfully!')

    except FileNotFoundError:
        print(f'❌ Error: CSV file "{file_path}" not found.')
    except PermissionError:
        print(f'❌ Error: No permission to access "{file_path}".')
    except Exception as e:
        print(f'❌ An unexpected error occurred: {e}')

def convert_csv_to_bin(csv_data):
    """ CSV 파일을 바이너리 파일로 변환, 저장, 출력 """
    try:
        with open(BIN_INVENTORY_LIST_PATH, 'wb') as f:
            for row in csv_data:
                f.write(','.join(row).encode('utf-8') + b'\n')
            
        with open(BIN_INVENTORY_LIST_PATH, 'rb') as f:
            binary_data = f.read()
        
        print('\n📦 Binary Mars Base Inventory List')
        print(binary_data)
        
        print('\n✅ Binary file created successfully!')

    except Exception as e:
        print(f'❌ Failed to convert CSV to BIN: {e}')

if __name__ == '__main__':
    main(INVENTORY_LIST_PATH)
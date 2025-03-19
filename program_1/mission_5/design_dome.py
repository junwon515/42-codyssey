import numpy as np

PARENT_PATH = 'program_1/mission_5/'
MAIN_PATH = PARENT_PATH + 'mars_base_main_parts-'
PARTS_PATH = PARENT_PATH + 'parts_to_work_on.csv'

def load_data(file_path):
    """ 데이터 불러오기 """
    try:
        return np.loadtxt(file_path, delimiter=',', dtype=str)
    except FileNotFoundError:
        print(f'❌ Error: file "{file_path}" not found.')
    except PermissionError:
        print(f'❌ Error: No permission to access "{file_path}".')
    except Exception as e:
        print(f'❌ An unexpected error occurred: {e}')
    return None

def save_data(file_path, data):
    """ 데이터 저장 """
    try:
        np.savetxt(file_path, data, fmt='%s', delimiter=',')
    except Exception as e:
        print(f'❌ Failed to save data: {e}')

def main():
    """ 메인 함수 """
    # 부품 데이터 불러오기
    data_list = [load_data(f'{MAIN_PATH}{i:03}.csv') for i in range(1, 4)]
    data_list = [data[1:, :] for data in data_list if data is not None]

    if not data_list:
        print('❌ No data found.')
        return

    parts = np.concatenate(data_list)

    # 부품별 평균 강도 계산
    parts_arrs, strength_arrs = parts[:, 0], parts[:, 1].astype(float)
    unique_parts = np.unique(parts_arrs)

    averages = np.array([
        [part, np.round(np.mean(strength_arrs[parts_arrs == part]), 3)]
        for part in unique_parts
    ], dtype=object)

    # 평균 강도가 50 미만인 부품 필터링
    work_parts = averages[averages[:, 1].astype(float) < 50]

    if work_parts.size > 0:
        save_data(PARTS_PATH, work_parts)
    else:
        print("ℹ️ No parts with average strength below 50.")

    # 저장된 부품 불러오고 전치행렬 변환 후 출력
    parts2 = load_data(PARTS_PATH)
    if parts2 is not None and parts2.size > 0:
        print(parts2.T)
    else:
        print("ℹ️ No data to transpose.")

if __name__ == '__main__':
    main()

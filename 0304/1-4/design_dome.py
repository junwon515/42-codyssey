import numpy as np

PARENT_PATH = 'program_1/mission_4/'
MAIN_PATH = PARENT_PATH + 'mars_base_main_parts-'
PARTS_PATH = PARENT_PATH + 'parts_to_work_on.csv'

# 전역 변수 선언
material = ''
diameter = 0
thickness = 0
area = 0.0
weight = 0.0


def sphere_area(diameter, material='유리', thickness=1):
    """반구의 표면적과 무게 계산"""

    global area, weight

    # 재질별 밀도 (g/cm³)
    densities = {'유리': 2.4, '알루미늄': 2.7, '탄소강': 7.85}

    # 반구 표면적 계산
    area = 3.14 * (diameter / 2) ** 2

    # 반구의 부피 계산 (겉면-속면)
    outer_volume = 2 / 3 * 3.14 * (diameter / 2) ** 3
    inner_volume = 2 / 3 * 3.14 * (diameter / 2 - thickness) ** 3
    material_volume = outer_volume - inner_volume

    # 무게 계산 (화성 중력 반영)
    weight = densities[material] * 0.38 * material_volume / 1000


def dome_calculator():
    """돔 계산기"""
    global material, diameter, thickness

    while True:
        try:
            user_input = input(
                '\n❇️  지름(cm), 재질(유리, 알루미늄, 탄소강), 두께(cm)를 입력하세요 (종료: exit)\n=> '
            ).split()

            if not user_input:
                continue
            if user_input[0].lower() == 'exit':
                print('\n🔅 프로그램을 종료합니다.')
                break

            # 입력값 처리
            diameter = int(user_input[0])
            if diameter <= 0:
                raise ValueError('지름은 0보다 커야 합니다.')

            material = user_input[1] if len(user_input) > 1 else '유리'
            if material not in ['유리', '알루미늄', '탄소강']:
                raise ValueError('재질은 유리, 알루미늄, 탄소강 중 하나여야 합니다.')

            thickness = int(user_input[2]) if len(user_input) > 2 else 1
            if thickness <= 0:
                raise ValueError('두께는 0보다 커야 합니다.')

            # 계산 수행
            sphere_area(diameter, material, thickness)

            # 결과 출력
            print(
                f'재질 ⇒ {material}, 지름 ⇒ {diameter} cm, 두께 ⇒ {thickness} cm, 면적 ⇒ {area:.3f} cm², 무게 ⇒ {weight:.3f} kg'
            )

        except ValueError as e:
            print(f'❌ {e} 다시 입력하세요.')


def load_data(file_path):
    """데이터 불러오기"""
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
    """데이터 저장"""
    try:
        np.savetxt(file_path, data, fmt='%s', delimiter=',')
    except Exception as e:
        print(f'❌ Failed to save data: {e}')


def process_parts_data():
    """부품 데이터 처리"""
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

    averages = np.array(
        [
            [part, np.round(np.mean(strength_arrs[parts_arrs == part]), 3)]
            for part in unique_parts
        ],
        dtype=object,
    )

    # 평균 강도가 50 미만인 부품 필터링
    work_parts = averages[averages[:, 1].astype(float) < 50]

    if work_parts.size > 0:
        save_data(PARTS_PATH, work_parts)
    else:
        print('ℹ️ No parts with average strength below 50.')

    # 저장된 부품 불러오고 전치행렬 변환 후 출력
    parts2 = load_data(PARTS_PATH)
    if parts2 is not None and parts2.size > 0:
        print(parts2.T)
    else:
        print('ℹ️ No data to transpose.')


def main():
    """메인 함수"""
    if input('부품 데이터 처리? (y/n) ').lower() == 'y':
        process_parts_data()
    elif input('돔 계산기? (y/n) ').lower() == 'y':
        dome_calculator()


if __name__ == '__main__':
    main()

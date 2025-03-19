# 전역 변수 선언
material = ''
diameter = 0
thickness = 0
area = 0.0
weight = 0.0

def sphere_area(diameter, material="유리", thickness=1):
    """ 반구의 표면적과 무게 계산 """
    
    global area, weight

    # 재질별 밀도 (g/cm³)
    densities = {'유리': 2.4, '알루미늄': 2.7, '탄소강': 7.85}

    # 반구 표면적 계산
    area = 3.14 * (diameter/2)**2

    # 반구의 부피 계산 (겉면-속면)
    outer_volume = 2/3 * 3.14 * (diameter/2)**3
    inner_volume = 2/3 * 3.14 * (diameter/2 - thickness)**3
    material_volume = outer_volume - inner_volume

    # 무게 계산 (화성 중력 반영)
    weight = densities[material] * 0.38 * material_volume / 1000

def main():
    """ 메인 함수 """
    global material, diameter, thickness

    while True:
        try:
            user_input = input('\n❇️  지름(cm), 재질(유리, 알루미늄, 탄소강), 두께(cm)를 입력하세요 (종료: exit)\n=> ').split()
            
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
            print(f'재질 ⇒ {material}, 지름 ⇒ {diameter} cm, 두께 ⇒ {thickness} cm, 면적 ⇒ {area:.3f} cm², 무게 ⇒ {weight:.3f} kg')

        except ValueError as e:
            print(f'❌ {e} 다시 입력하세요.')

if __name__ == '__main__':
    main()

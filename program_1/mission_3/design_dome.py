material = str()
diameter = int()
thickness = int()
area = float()
weight = float()

def sphere_volume(diameter, material='유리', thickness=1):
    """ 구의 부피를 계산하는 함수 """
    globals()['material'] = material
    globals()['diameter'] = diameter
    globals()['thickness'] = thickness
    globals()['area'] = 3.14 * (diameter/2)**2

    material_volume = 2/3 * 3.14 * ((diameter/2)**3 - (diameter/2 - thickness)**3)
    
    # 매칭되는 재료에 따라 무게 계산
    match material:
        case '유리':
            globals()['weight'] = 2.4 * 0.38 * material_volume
        case '알루미늄':
            globals()['weight'] =  2.7 * 0.38 * material_volume
        case '탄소강':
            globals()['weight'] = 7.85 * 0.38 * material_volume
        case _:
            globals()['weight'] = 0

def main():
    """ 메인 함수 """
    while True:
        try:
            user_input = input('\n❇️  돔의 지름(cm), 재질(유리, 알루미늄, 탄소강), 두께(cm)를 입력하세요'
                               + '\nex) 10 유리 1'
                               + '\n=> ').split()
            
            if not user_input:
                continue
            if user_input[0] == 'exit':
                print('\n🔅 프로그램을 종료합니다.')
                break

            for i in range(1, len(user_input)+1):
                match i:
                    case 1:
                        user_input[0] = int(user_input[0])
                        if user_input[0] <= 0:
                            raise ValueError
                    case 2:
                        if user_input[1] not in ['유리', '알루미늄', '탄소강']:
                            print('❌ 재질은 유리, 알루미늄, 탄소강 중 하나여야 합니다.')
                            raise ValueError
                    case 3:
                        user_input[2] = int(user_input[2])
                        if user_input[2] <= 0:
                            raise ValueError

            sphere_volume(*user_input)

            print('재질 ⇒ %s, 지름 ⇒ %d cm, 두께 ⇒ %d cm, 면적 ⇒ %.3f cm², 무게 ⇒ %.3f kg' % (material, diameter, thickness, area, weight))

        except ValueError:
            print('❌ 잘못된 입력입니다. 다시 입력하세요.')

if __name__ == '__main__':
    main()
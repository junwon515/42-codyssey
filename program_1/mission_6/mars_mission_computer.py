import random
from datetime import datetime

PARENT_PATH = 'program_1/mission_6/'
LOG_PATH = PARENT_PATH + 'mars_mission_computer.log'

class DummySensor:
    """ 더미 센서 클래스 """
    def __init__(self):
        self.env_values = {
            'timestamp': None,
            'mars_base_internal_temperature': None,
            'mars_base_external_temperature': None,
            'mars_base_internal_humidity': None,
            'mars_base_external_illuminance': None,
            'mars_base_internal_co2': None,
            'mars_base_internal_oxygen': None,
        }

    def get_env(self):
        """ 환경 센서 값을 반환한다. """
        self.__write_log()
        return self.env_values
    
    def set_env(self):
        """ 환경 센서 값을 설정한다. """
        # if not self.__input_timestamp():
        #     return None
        self.env_values.update({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # 현재 시간
            'mars_base_internal_temperature': random.randint(18, 30),
            'mars_base_external_temperature': random.randint(0, 21),
            'mars_base_internal_humidity': round(random.uniform(50.0, 60.0), 1),
            'mars_base_external_illuminance': random.randint(500, 715),
            'mars_base_internal_co2': round(random.uniform(0.02, 0.1), 2),
            'mars_base_internal_oxygen': round(random.uniform(4.0, 7.0), 1),
        })
        print('\n🌡️  Sensor values successfully set')

    def __input_timestamp(self):
        """ 타임스탬프를 설정한다. """
        for i in range(3):
            timestamp = input('\n❇️  Enter the timestamp (YYYY-MM-DD HH:MM:SS): ')
            parts = timestamp.split(' ')
            if len(parts) == 2 and len(parts[0]) == 10 and len(parts[1]) == 8:
                date_parts = parts[0].split('-')
                time_parts = parts[1].split(':')
                if all(p.isdigit() for p in date_parts + time_parts):
                    self.env_values['timestamp'] = timestamp
                    return True
            print(f'❌ 잘못된 입력입니다. 다시 입력해주세요. {2-i}회 남음')
        print('❌ 3회 잘못된 입력으로 종료합니다.')
        return False

    def __write_log(self):
        """ 로그를 기록한다. """
        try:
            with open(LOG_PATH, 'a', encoding='utf-8') as f:
                if f.tell() == 0:
                    f.write(','.join([
                        header.replace('mars_base_', '') for header in self.env_values.keys()
                    ]) + '\n')
                f.write(','.join(map(str, self.env_values.values())) + '\n')
                print('\n📝 Log file written successfully')
        except Exception as e:
            print(f'❌ Failed to write Log file: {e}')

def main():
    """ 메인 함수 """
    ds = DummySensor()
    ds.set_env()
    env_dict = ds.get_env()

    print('\n=== Sensor values ===')
    for key, value in env_dict.items():
        print(f'{key}: {value}')
    
if __name__ == '__main__':
    main()
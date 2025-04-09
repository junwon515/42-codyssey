import random
from datetime import datetime,timedelta
from threading import Timer
import platform
import psutil

PARENT_PATH = 'program_1/mission_6/'
LOG_PATH = PARENT_PATH + 'mars_mission_computer.log'
SETTING_PATH = PARENT_PATH + 'setting.txt'

env_values = {
    'timestamp': None,
    'mars_base_internal_temperature': None,
    'mars_base_external_temperature': None,
    'mars_base_internal_humidity': None,
    'mars_base_external_illuminance': None,
    'mars_base_internal_co2': None,
    'mars_base_internal_oxygen': None,
}

class DummySensor:
    """ 더미 센서 클래스 """
    def __init__(self, env_values):
        self.env_values = env_values

    def get_env(self):
        """ 환경 센서 값을 반환한다. """
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
        self.__write_log()

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

class MissionComputer:
    """ 화성 미션 컴퓨터 클래스 """
    def __init__(self, env_values):
        self.env_values = env_values
        self.ds = DummySensor(env_values)
        self.timer = [None] * 2

    def get_sensor_data(self):
        """ 센서 데이터를 가져온다. """
        try:
            self._update_sensors()
            self._print_avg()
            
            while True:
                if input().strip().lower() == 'exit':
                    break
        except KeyboardInterrupt:
            print('\n❇️  System interrupted by user.')
        except Exception as e:
            print(f'❌ An unexpected error occurred: {e}')
        finally:
            print('\n❇️  Sytem stoped...')
            for t in self.timer: 
                if t:
                    t.cancel()

    def get_mission_computer_info(self):
        """미션 컴퓨터 정보를 반환한다."""
        computer_info = {}
        try:
            settings = self.__read_setting()
            if not settings:
                print('\n❇️  No settings found.')
                return computer_info

            info_map = {
                "os": lambda: platform.system(),
                "os_version": lambda: platform.version(),
                "cpu_type": lambda: platform.processor(),
                "cpu_physical_cores": lambda: psutil.cpu_count(logical=False),
                "memory_total_gb": lambda: psutil.virtual_memory().total / (1024 ** 3)
            }

            computer_info = {key: info_map[key]() for key in settings if key in info_map}

            print('\n=== Mission Computer Info ===')
            print(self.__dict_to_json(computer_info))
        except Exception as e:
            print(f"\n❌ Failed to get mission computer info: {e}")

        return computer_info

    def get_mission_computer_load(self):
        """ 미션 컴퓨터의 부하를 반환한다. """
        computer_load = {}
        try:
            computer_load = {
                "cpu_usage_percent": psutil.cpu_percent(interval=1),
                "memory_usage_percent": psutil.virtual_memory().percent
            }
            print('\n=== Mission Computer Load ===')
            print(self.__dict_to_json(computer_load))
        except Exception as e:
            print(f"\n❌ Failed to get mission computer load: {e}")

        return computer_load

    def _update_sensors(self):
        """ 센서 값을 업데이트한다. """
        try:
            self.ds.set_env()
            
            print('\n=== Mars Base Environment ===')
            print(self.__dict_to_json(self.env_values))
            
            self.timer[0] = Timer(5, self._update_sensors)
            self.timer[0].start()
        except Exception as e:
            print(f'❌ Sensor update error: {e}')

    def _print_avg(self):
        """ 최근 5분간의 평균 센서 값을 출력한다. """
        try:
            data = self.__read_recent_data()
            if not data:
                print('\n❇️  No data available in the last 5 minutes.')
                return
            
            averages = {list(self.env_values.keys())[i]: sum(values) / len(values)
                         for i, values in enumerate(zip(*data))}
            print('\n=== Average Sensor Values (last 5 minutes) ===')
            print(self.__dict_to_json(averages))
            
            self.timer[1] = Timer(300, self._print_avg)
            self.timer[1].start()
        except Exception as e:
            print(f'❌ Error calculating average: {e}')

    def __read_recent_data(self):
        """ 최근 5분간의 센서 데이터를 읽어온다. """     
        five_minutes_ago = datetime.now() - timedelta(minutes=5)
        data = []
        
        try:
            with open(LOG_PATH, 'rb') as f:
                f.seek(0, 2)
                position = f.tell()
                line = b""
                
                while position >= 0:
                    f.seek(position)
                    char = f.read(1)
                    
                    if char == b'\n' and line:
                        decoded_line = line.decode('utf-8').strip()
                        values = decoded_line.split(',')
                        try:
                            timestamp = datetime.strptime(values[0], '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            print(f'❌ Invalid timestamp in log: {values[0]}')
                            position -= 1
                            line = b''
                            continue
                        
                        if timestamp < five_minutes_ago:
                            break
                        
                        try:
                            data.append(list(map(float, values[1:])))
                        except ValueError:
                            print(f'❌ Invalid sensor data in log: {values[1:]}')
                        
                        line = b''
                    else:
                        line = char + line
                    
                    position -= 1
        except Exception as e:
            print(f'❌ Error reading log file: {e}')
        
        return data
    
    def __read_setting(self):
        """ 설정 파일을 읽어온다. """
        lines = []
        try:
            with open(SETTING_PATH, 'r', encoding='utf-8') as f:
                lines = [line.strip().lower() for line in f if line.strip()]
        except Exception as e:
            print(f'❌ Error reading setting file: {e}')

        return lines
    
    def __dict_to_json(self, obj, indent=0):
        spacing = '  ' * indent
        if isinstance(obj, dict):
            items = []
            for key, value in obj.items():
                json_key = f'"{str(key)}"'
                json_value = self.__dict_to_json(value, indent + 1)
                items.append(f'{spacing}  {json_key}: {json_value}')
            return '{\n' + ',\n'.join(items) + f'\n{spacing}' + '}'
        elif isinstance(obj, list):
            items = [self.__dict_to_json(item, indent + 1) for item in obj]
            return '[\n' + ',\n'.join(f'{spacing}  {item}' for item in items) + f'\n{spacing}' + ']'
        elif isinstance(obj, str):
            return f'"{obj}"'
        elif isinstance(obj, bool):
            return 'true' if obj else 'false'
        elif obj is None:
            return 'null'
        elif isinstance(obj, float):
            return f'{round(obj, 2):.2f}'
        else:  # int 등
            return str(obj)
    
def main():
    """ 메인 함수 """
    runComputer = MissionComputer(env_values)
    runComputer.get_mission_computer_info()
    runComputer.get_mission_computer_load()
    
if __name__ == '__main__':
    main()
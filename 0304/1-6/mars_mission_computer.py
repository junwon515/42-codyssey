import multiprocessing
import platform
import random
import threading
import time
from datetime import datetime, timedelta

import psutil

PARENT_PATH = '0304/1-6/'
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
    """더미 센서 클래스"""

    def __init__(self, env_values):
        self.env_values = env_values

    def get_env(self):
        """환경 센서 값을 반환한다."""
        return self.env_values

    def set_env(self):
        """환경 센서 값을 설정한다."""
        # if not self.__input_timestamp():
        #     return None
        self.env_values.update(
            {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # 현재 시간
                'mars_base_internal_temperature': random.randint(18, 30),
                'mars_base_external_temperature': random.randint(0, 21),
                'mars_base_internal_humidity': round(random.uniform(50.0, 60.0), 1),
                'mars_base_external_illuminance': random.randint(500, 715),
                'mars_base_internal_co2': round(random.uniform(0.02, 0.1), 2),
                'mars_base_internal_oxygen': round(random.uniform(4.0, 7.0), 1),
            }
        )
        self.__write_log()

    def __input_timestamp(self):
        """타임스탬프를 설정한다."""
        for i in range(3):
            timestamp = input('\n❇️  Enter the timestamp (YYYY-MM-DD HH:MM:SS): ')
            parts = timestamp.split(' ')
            if len(parts) == 2 and len(parts[0]) == 10 and len(parts[1]) == 8:
                date_parts = parts[0].split('-')
                time_parts = parts[1].split(':')
                if all(p.isdigit() for p in date_parts + time_parts):
                    self.env_values['timestamp'] = timestamp
                    return True
            print(f'❌ 잘못된 입력입니다. 다시 입력해주세요. {2 - i}회 남음')
        print('❌ 3회 잘못된 입력으로 종료합니다.')
        return False

    def __write_log(self):
        """로그를 기록한다."""
        try:
            with open(LOG_PATH, 'a', encoding='utf-8') as f:
                if f.tell() == 0:
                    f.write(
                        ','.join(
                            [
                                header.replace('mars_base_', '')
                                for header in self.env_values
                            ]
                        )
                        + '\n'
                    )
                f.write(','.join(map(str, self.env_values.values())) + '\n')
        except Exception as e:
            print(f'❌ Failed to write Log file: {e}', flush=True)


class MissionComputer:
    """화성 미션 컴퓨터 클래스"""

    def __init__(self, env_values):
        self.env_values = env_values
        self.ds = DummySensor(env_values)

    def start(self):
        self.get_sensor_data()
        threading.Thread(
            target=self._schedule_task,
            args=(20, self.get_mission_computer_info),
            daemon=True,
        ).start()
        threading.Thread(
            target=self._schedule_task,
            args=(20, self.get_mission_computer_load),
            daemon=True,
        ).start()

    def get_sensor_data(self):
        """센서 데이터를 가져온다."""
        threading.Thread(
            target=self._schedule_task, args=(5, self._update_sensors), daemon=True
        ).start()
        threading.Thread(
            target=self._schedule_task, args=(300, self._print_avg), daemon=True
        ).start()

    def get_mission_computer_info(self):
        """화성 미션 컴퓨터 정보를 가져온다."""
        try:
            settings = self.__read_setting()
            if not settings:
                raise ValueError('No settings found.')
            info_map = {
                'os': platform.system,
                'os_version': platform.version,
                'cpu_type': platform.processor,
                'cpu_physical_cores': lambda: psutil.cpu_count(logical=False),
                'memory_total_gb': lambda: psutil.virtual_memory().total / (1024**3),
            }
            return {key: info_map[key]() for key in settings if key in info_map}
        except Exception as e:
            print(f'\n❌ Failed to get mission computer info: {e}', flush=True)

    def get_mission_computer_load(self):
        """화성 미션 컴퓨터의 부하를 가져온다."""
        try:
            return {
                'cpu_usage_percent': psutil.cpu_percent(interval=1),
                'memory_usage_percent': psutil.virtual_memory().percent,
            }
        except Exception as e:
            print(f'\n❌ Failed to get mission computer load: {e}', flush=True)

    def _update_sensors(self):
        """센서 값을 업데이트한다."""
        try:
            self.ds.set_env()
            return self.ds.get_env()
        except Exception as e:
            print(f'❌ Error updating sensors: {e}', flush=True)

    def _print_avg(self):
        """최근 5분 평균 센서 값을 출력한다."""
        try:
            data = self.__read_recent_data()
            if not data:
                raise ValueError('No data available for averaging.')
            return {
                list(self.env_values.keys())[i]: sum(values) / len(values)
                for i, values in enumerate(zip(*data, strict=False))
            }
        except Exception as e:
            print(f'❌ Error calculating averages: {e}', flush=True)

    def _schedule_task(self, interval, func):
        """주기적으로 함수를 실행한다."""
        while True:
            try:
                start_time = time.time()
                result = func()
                if isinstance(result, dict):
                    print(
                        f'\n📌 Output from: {func.__name__}  {self.__dict_to_json(result)}\n',
                        flush=True,
                    )
                time.sleep(max(0, interval - (time.time() - start_time)))
            except Exception as e:
                print(f'\n❌ Error in scheduled task: {e}', flush=True)
                time.sleep(interval)

    def __read_recent_data(self):
        """최근 5분간의 센서 데이터를 읽는다."""
        try:
            five_minutes_ago = datetime.now() - timedelta(minutes=5)
            data = []

            with open(LOG_PATH, 'rb') as f:
                f.seek(0, 2)
                position = f.tell()
                line = b''

                while position >= 0:
                    f.seek(position)
                    char = f.read(1)
                    if char == b'\n' and line:
                        try:
                            values = line.decode('utf-8').strip().split(',')
                            timestamp = datetime.strptime(
                                values[0], '%Y-%m-%d %H:%M:%S'
                            )
                            if timestamp < five_minutes_ago:
                                break
                            data.append(list(map(float, values[1:])))
                        except Exception:
                            pass
                        line = b''
                    else:
                        line = char + line
                    position -= 1

            return data
        except Exception as e:
            print(f'❌ Error reading log file: {e}', flush=True)

    def __read_setting(self):
        """설정 파일을 읽는다."""
        try:
            with open(SETTING_PATH, encoding='utf-8') as f:
                return [line.strip().lower() for line in f if line.strip()]
        except Exception as e:
            print(f'❌ Error reading setting file: {e}', flush=True)

    def __dict_to_json(self, obj, indent=0):
        """딕셔너리를 JSON 형식으로 변환한다."""
        spacing = '  ' * indent
        if isinstance(obj, dict):
            items = [
                f'{spacing}  "{k}": {self.__dict_to_json(v, indent + 1)}'
                for k, v in obj.items()
            ]
            return '{\n' + ',\n'.join(items) + f'\n{spacing}' + '}'
        elif isinstance(obj, list):
            items = [self.__dict_to_json(item, indent + 1) for item in obj]
            return (
                '[\n'
                + ',\n'.join(f'{spacing}  {item}' for item in items)
                + f'\n{spacing}'
                + ']'
            )
        elif isinstance(obj, str):
            return f'"{obj}"'
        elif isinstance(obj, bool):
            return 'true' if obj else 'false'
        elif obj is None:
            return 'null'
        elif isinstance(obj, float):
            return f'{round(obj, 2):.2f}'
        return str(obj)


def run_instance(env, stop_event):
    """인스턴스를 실행한다."""
    run_computer = MissionComputer(env)
    run_computer.start()

    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print('\n❇️  Stopping instance...', flush=True)


def main():
    """메인 함수"""
    stop_event = multiprocessing.Event()
    processes = []
    for _ in range(3):
        process = multiprocessing.Process(
            target=run_instance, args=(env_values.copy(), stop_event)
        )
        processes.append(process)
        process.start()

    try:
        while True:
            user_input = input()
            if user_input.strip().lower() == 'exit':
                stop_event.set()
                break
    except KeyboardInterrupt:
        stop_event.set()
        print('\n❇️  Interrupted by user.', flush=True)
    finally:
        for process in processes:
            process.join()
        print('\n❇️  System stopped...', flush=True)


if __name__ == '__main__':
    main()

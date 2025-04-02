from program_1.mission_6.mars_mission_computer import DummySensor
from datetime import datetime, timedelta
from threading import Timer

LOG_PATH = 'program_1/mission_6/mars_mission_computer.log'

class MissionComputer:
    """ 화성 미션 컴퓨터 클래스 """
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
        self.ds = DummySensor()
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

    def _update_sensors(self):
        """ 센서 값을 업데이트한다. """
        try:
            self.ds.set_env()
            self.env_values.update(self.ds.get_env())
            
            print('\n=== Mars Base Environment ===')
            print({key.replace('mars_base_', ''): value for key, value in self.env_values.items()})
            
            self.timer[0] = Timer(5, self._update_sensors)
            self.timer[0].start()
        except Exception as e:
            print(f'❌ Sensor update error: {e}')

    def _print_avg(self):
        """ 최근 5분간의 평균 센서 값을 출력한다. """
        try:
            data = self._read_recent_data()
            if not data:
                print('\n❇️  No data available in the last 5 minutes.')
                return
            
            averages = {list(self.env_values.keys())[i]: sum(values) / len(values)
                         for i, values in enumerate(zip(*data))}
            print('\n=== Average Sensor Values (last 5 minutes) ===')
            print({key.replace('mars_base_', ''): round(value, 2) for key, value in averages.items()})
            
            self.timer[1] = Timer(300, self._print_avg)
            self.timer[1].start()
        except Exception as e:
            print(f'❌ Error calculating average: {e}')

    def _read_recent_data(self):
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

def main():
    """ 메인 함수 """
    RunComputer = MissionComputer()
    RunComputer.get_sensor_data()
    
if __name__ == '__main__':
    main()

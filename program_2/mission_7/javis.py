import os
import threading
import datetime
import time
import wave
import pyaudio

PARENT_PATH = os.path.dirname(os.path.abspath(__file__))
RECORD_FOLDER = os.path.join(PARENT_PATH, 'records/')

MAX_RECORD_SECONDS = 60
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

class Recorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.stop_recording = False
        self._ensure_record_folder()

    def _ensure_record_folder(self):
        os.makedirs(RECORD_FOLDER, exist_ok=True)

    def _wait_for_input(self):
        input()
        self.stop_recording = True

    def record(self):
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        print('🎙️  녹음을 시작합니다. 최대 60초 또는 엔터 입력 시 종료됩니다.')
        input_thread = threading.Thread(target=self._wait_for_input)
        input_thread.start()

        self.frames.clear()
        start_time = time.time()
        elapsed_time = 0

        while not self.stop_recording and elapsed_time < MAX_RECORD_SECONDS:
            elapsed_time = time.time() - start_time
            print(f'🔴 녹음 중... {elapsed_time:.1f}초', end='\r')
            self.frames.append(stream.read(CHUNK))

        stream.stop_stream()
        stream.close()
        self.audio.terminate()

        self._save_recording()

    def _save_recording(self):
        filename = f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.wav'
        filepath = os.path.join(RECORD_FOLDER, filename)

        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self.frames))

        print(f'\n✅ 녹음 완료! 파일이 저장되었습니다: {filepath}')

def list_recordings(start_date, end_date):
    if not os.path.exists(RECORD_FOLDER):
        print('❗ 녹음 폴더가 존재하지 않습니다.')
        return

    recordings = []
    for filename in os.listdir(RECORD_FOLDER):
        if filename.endswith('.wav'):
            try:
                date_str = filename.split('-')[0]
                file_date = datetime.datetime.strptime(date_str, '%Y%m%d')
                if start_date <= file_date <= end_date:
                    recordings.append(filename)
            except ValueError:
                continue

    if recordings:
        print(f'\n📜 {start_date.strftime("%Y-%m-%d")} ~ {end_date.strftime("%Y-%m-%d")} 녹음 목록:')
        for idx, rec in enumerate(sorted(recordings), 1):
            print(f'{idx}. {rec}')
    else:
        print('❗ 해당 기간에 녹음된 파일이 없습니다.')

def parse_date_range(date_range_str):
    try:
        if '~' not in date_range_str:
            raise ValueError
        start_str, end_str = date_range_str.split('~')
        start_date = datetime.datetime.strptime(start_str, '%Y%m%d') if start_str else datetime.datetime.min
        end_date = datetime.datetime.strptime(end_str, '%Y%m%d') if end_str else datetime.datetime.max
        return start_date, end_date
    except ValueError:
        print('❗ 날짜 형식이 잘못되었습니다. YYYYMMDD~YYYYMMDD 형식으로 입력해주세요.')
        return None, None

def main():
    recorder = Recorder()

    while True:
        print('\n❇️  JARVIS 음성 녹음 프로그램')
        print('1. 녹음하기')
        print('2. 녹음 파일 목록 보기')
        print('3. 종료')

        choice = input('➡️  원하는 작업을 선택하세요 (1/2/3): ').strip()

        if choice == '1':
            recorder.record()
        elif choice == '2':
            date_input = input('날짜 범위 (YYYYMMDD~YYYYMMDD): ')
            start_date, end_date = parse_date_range(date_input)
            if start_date and end_date:
                list_recordings(start_date, end_date)
        elif choice == '3':
            print('❇️  프로그램을 종료합니다.')
            break
        else:
            print('❗ 잘못된 선택입니다. 다시 시도해주세요.')

if __name__ == '__main__':
    main()
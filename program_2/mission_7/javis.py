import os
import threading
import datetime
import wave
import pyaudio
import speech_recognition as sr
from pydub import AudioSegment, silence

PARENT_PATH = os.path.dirname(os.path.abspath(__file__))
RECORD_FOLDER = os.path.join(PARENT_PATH, 'records/')

MAX_RECORD_SECONDS = 60
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

class Recorder:
    def __init__(self):
        self.frames = []
        self.stop_recording = False
        self._ensure_record_folder()
        self.audio = pyaudio.PyAudio()

    def _ensure_record_folder(self):
        os.makedirs(RECORD_FOLDER, exist_ok=True)

    def _wait_for_input(self):
        input()
        self.stop_recording = True

    def record(self):
        try:
            stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
        except Exception as e:
            print(f'❗ 마이크를 열 수 없습니다: {e}')
            return

        print('🎙️  녹음을 시작합니다. 최대 60초 또는 엔터 입력 시 종료됩니다.')
        input_thread = threading.Thread(target=self._wait_for_input)
        input_thread.start()

        self.frames.clear()
        self.stop_recording = False

        for i in range(0, int(RATE / CHUNK * MAX_RECORD_SECONDS) + 1):
            if self.stop_recording: break
            print(f'🔴 녹음 중... {i * CHUNK / RATE:.1f}초', end='\r')
            self.frames.append(stream.read(CHUNK))

        stream.stop_stream()
        stream.close()

        filename = f'{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.wav'
        filepath = os.path.join(RECORD_FOLDER, filename)

        self._save_recording(filepath)
        self.transcribe_audio_to_csv(filepath)

    def _save_recording(self, filepath):
        try:
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(self.frames))
            print(f'\n✅ 녹음 완료! 파일이 저장되었습니다: {filepath}')
        except Exception as e:
            print(f'❗ 파일 저장 실패: {e}')

    def transcribe_audio_to_csv(self, filepath):
        recognizer = sr.Recognizer()
        try:
            audio = AudioSegment.from_wav(filepath)
        except Exception as e:
            print(f'❗ 오디오 파일 로딩 실패: {e}')
            return

        min_silence_len = 700
        silence_thresh = audio.dBFS - 16

        nonsilent_ranges = silence.detect_nonsilent(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh
        )

        base_filename = os.path.splitext(os.path.basename(filepath))[0]
        csv_filename = os.path.splitext(filepath)[0] + '.csv'

        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            f.write('시작 시간 (초),인식된 텍스트\n')

            for i, (start_ms, end_ms) in enumerate(nonsilent_ranges):
                chunk = audio[start_ms:end_ms]
                chunk_filename = os.path.join(RECORD_FOLDER, f'{base_filename}_chunk_{i}.wav')
                chunk.export(chunk_filename, format='wav')

                try:
                    with sr.AudioFile(chunk_filename) as source:
                        audio_data = recognizer.record(source)
                        text = recognizer.recognize_google(audio_data, language='ko-KR')
                        f.write(f'{start_ms/1000:.2f},{text}\n')
                except sr.UnknownValueError:
                    print(f'🔇 인식 실패 (청크 {i})')
                except sr.RequestError as e:
                    print(f'❗ STT 서버 오류 (청크 {i}): {e}')
                finally:
                    if os.path.exists(chunk_filename):
                        os.remove(chunk_filename)

        print(f'📝 텍스트 추출 완료. CSV 저장됨: {csv_filename}')

def parse_partial_date(date_str, is_start=True):
    try:
        if len(date_str) == 4:
            return datetime.datetime.strptime(date_str, '%Y') if is_start else \
                   datetime.datetime.strptime(date_str, '%Y').replace(month=12, day=31)
        elif len(date_str) == 6:
            return datetime.datetime.strptime(date_str, '%Y%m') if is_start else \
                   (datetime.datetime.strptime(date_str, '%Y%m') + datetime.timedelta(days=31)).replace(day=1) - datetime.timedelta(days=1)
        elif len(date_str) == 8:
            return datetime.datetime.strptime(date_str, '%Y%m%d')
        else:
            raise ValueError
    except ValueError:
        raise ValueError('날짜 형식이 잘못되었습니다. YYYY, YYYYMM, YYYYMMDD 형식으로 입력하세요.')

def parse_date_range(date_range_str):
    date_range_str = date_range_str.strip()
    if not date_range_str:
        return datetime.datetime.min, datetime.datetime.max
    if '~' in date_range_str:
        start_str, end_str = map(str.strip, date_range_str.split('~'))
    else:
        start_str, end_str = date_range_str, date_range_str
    try:
        start_date = parse_partial_date(start_str, True) if start_str else datetime.datetime.min
        end_date = parse_partial_date(end_str, False) if end_str else datetime.datetime.max
        return start_date, end_date
    except ValueError as e:
        print(f'❗ 날짜 형식 오류: {e}')
        return None, None

def list_recordings(start_date, end_date, print_info=True):
    if not os.path.exists(RECORD_FOLDER):
        print('❗ 녹음 폴더가 존재하지 않습니다.')
        return []

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

    if not recordings:
        print('❗ 해당 날짜 범위에 녹음된 파일이 없습니다.')
        return []
    if print_info:
        print(f'📂 {len(recordings)}개의 녹음 파일이 발견되었습니다:')
        for recording in recordings:
            print(f'  - {recording}')
    return recordings

def search_in_csv_files(keyword):
    keyword = keyword.strip()
    if not keyword:
        print('❗ 검색 키워드를 입력하세요.')
        return

    found = False
    for filename in os.listdir(RECORD_FOLDER):
        if not filename.endswith('.csv'):
            continue
        filepath = os.path.join(RECORD_FOLDER, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                next(f)
                for line in f:
                    row = line.split(',')
                    if len(row) < 2:
                        continue
                    if keyword in row[1]:
                        if not found:
                            print(f'\n🔍 키워드 "{keyword}" 검색 결과:')
                            found = True
                        print(f'📂 파일: {filename} | 시간: {row[0]} | 텍스트: {row[1]}')
        except Exception as e:
            print(f'❗ CSV 파일을 읽는 중 오류 발생: {filename} ({e})')

    if not found:
        print('❗ 해당 키워드가 포함된 내용이 없습니다.')

def main():
    recorder = Recorder()
    try:
        while True:
            print('\n❇️  JARVIS 음성 녹음 프로그램')
            print('1. 녹음하기')
            print('2. 녹음 파일 목록 보기')
            print('3. 음성 텍스트로 변환 및 CSV 저장')
            print('4. 키워드로 텍스트 검색')
            print('5. 종료')

            choice = input('➡️  원하는 작업을 선택하세요 (1/2/3/4/5): ').strip()

            if choice == '1':
                recorder.record()
            elif choice == '2':
                date_input = input('녹음 파일의 날짜 범위를 입력하세요 (YYYYMMDD ~ YYYYMMDD): ')
                start_date, end_date = parse_date_range(date_input)
                if start_date and end_date:
                    list_recordings(start_date, end_date)
            elif choice == '3':
                date_input = input('녹음 파일의 날짜 범위를 입력하세요 (YYYYMMDD ~ YYYYMMDD): ')
                start_date, end_date = parse_date_range(date_input)
                if start_date and end_date:
                    recordings = list_recordings(start_date, end_date, print_info=False)
                    for recording in recordings:
                        filepath = os.path.join(RECORD_FOLDER, recording)
                        recorder.transcribe_audio_to_csv(filepath)
            elif choice == '4':
                keyword = input('🔍 검색할 키워드를 입력하세요: ')
                search_in_csv_files(keyword)
            elif choice == '5':
                print('❇️  프로그램을 종료합니다.')
                break
            else:
                print('❗ 잘못된 선택입니다. 다시 시도해주세요.')
    except KeyboardInterrupt:
        print('\n❇️  사용자 요청으로 프로그램을 종료합니다.')
    finally:
        recorder.audio.terminate()

if __name__ == '__main__':
    main()
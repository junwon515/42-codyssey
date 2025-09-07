import time
import zipfile

PARENT_PATH = 'program_2/mission_1/'
ZIP_PATH = PARENT_PATH + 'emergency_storage_key.zip'
PASSWORD_PATH = PARENT_PATH + 'password.txt'

CHAR_GROUP = 'etaoinshrdlucmfwypvbgkqjxz'
NUMERIC = '0123456789'
MAX_LENGTH = 6
MIN_LENGTH = 4


def unlock_zip():
    try:
        zip_file = zipfile.ZipFile(ZIP_PATH)
    except FileNotFoundError:
        print('❌ ZIP file not found.')
        return
    except zipfile.BadZipFile:
        print('❌ Bad ZIP file.')
        return

    print('🔑 Attempting to unlock the ZIP file...')
    start_time = time.time()
    attempts = 0

    def try_password(pwd):
        nonlocal attempts
        attempts += 1
        try:
            zip_file.read(zip_file.namelist()[0], pwd=bytes(pwd, 'utf-8'))
            duration = time.time() - start_time
            print(
                f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] '
                f'Trying: {pwd} | Attempts: {attempts // 1000}K | Time: {duration:.2f}s',
                end='\r',
            )
            print(f'\n✅ Password found: {pwd}')
            print(f'🔁 Total attempts: {attempts}')
            print(f'⏱ Time taken: {duration:.2f} seconds')
            write_password(pwd)
            return True
        except Exception:
            if attempts % 1000 == 0:
                elapsed = time.time() - start_time
                print(
                    f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] '
                    f'Trying: {pwd} | Attempts: {attempts // 1000}K | Time: {elapsed:.2f}s',
                    end='\r',
                )
            return False

    for length in range(MIN_LENGTH, MAX_LENGTH + 1):
        # A. 숫자만 조합해서 시도 (예: 1234, 567890)
        for num in generate_combinations(NUMERIC, length):
            if try_password(num):
                return

        # B. 문자 기반 패턴 시도
        for i in range(1, len(CHAR_GROUP) + 1):
            current_charset = CHAR_GROUP[:i]  # 자주 쓰이는 문자 빈도 순으로 확장
            new_char = CHAR_GROUP[i - 1]  # 현재 확장된 문자 중 마지막 문자

            for j in range(0, length):
                is_alphabet_pattern = j == 0  # 알파벳 패턴 체크
                is_cross_pattern = (
                    True if j > 1 and (j * 2 == length) else False
                )  # 교차형 패턴 체크
                # pwd_base는 현재 문자셋으로 만든 (length - j - 1) 길이의 문자열
                for pwd_base in generate_combinations(current_charset, length - j - 1):
                    for k in range(0, length - j):
                        # pwd_base에 new_char를 삽입 (이전 패턴과 중복 방지)
                        pwd = pwd_base[:k] + new_char + pwd_base[k:]

                        # B1. 문자 패턴 (문자열만)
                        if is_alphabet_pattern:
                            if try_password(pwd):
                                return
                            continue

                        for num in generate_combinations(NUMERIC, j):
                            # B2. 문자 + 숫자 패턴 (문자열 뒤에 숫자)
                            if try_password(pwd + num):
                                return
                            # B3. 숫자 + 문자 패턴 (숫자 뒤에 문자열)
                            if try_password(num + pwd):
                                return

                            # B4. 교차형 패턴 (문자+숫자+문자+숫자 ...)
                            if is_cross_pattern:
                                if try_password(
                                    ''.join(
                                        x + y for x, y in zip(pwd, num, strict=False)
                                    )
                                ):
                                    return
                                if try_password(
                                    ''.join(
                                        x + y for x, y in zip(num, pwd, strict=False)
                                    )
                                ):
                                    return

    for length in range(MIN_LENGTH, MAX_LENGTH + 1):
        # C. A, B 패턴 외 모든 가능한 문자+숫자 조합 시도
        for i in range(1, len(CHAR_GROUP) + 1):
            current_charset = CHAR_GROUP[:i] + NUMERIC
            new_char = CHAR_GROUP[i - 1]

            for pwd_base in generate_combinations(current_charset, length - 1):
                for j in range(0, length):
                    # pwd_base에 new_char를 삽입 (이전 패턴과 중복 방지)
                    pwd = pwd_base[:j] + new_char + pwd_base[j:]

                    # check_pattern을 통해 이미 시도된 A/B 패턴이면 스킵
                    if check_pattern(pwd):
                        continue

                    # 새로운 패턴이므로 시도
                    if try_password(pwd):
                        return

    print('\n❇️  Password not found.')


def generate_combinations(charset, length):
    if length == 0:
        yield ''
    else:
        for char in charset:
            for pwd in generate_combinations(charset, length - 1):
                yield char + pwd


def check_pattern(pwd):
    if pwd.isdigit() or pwd.isalpha():
        return True

    # 문자+숫자 체크 (연속 문자 뒤에 연속 숫자)
    i = 0
    while i < len(pwd) and pwd[i].isalpha():
        i += 1
    if 0 < i < len(pwd) and pwd[i:].isdigit():
        return True

    # 숫자+문자 체크 (연속 숫자 뒤에 연속 문자)
    i = 0
    while i < len(pwd) and pwd[i].isdigit():
        i += 1
    if 0 < i < len(pwd) and pwd[i:].isalpha():
        return True

    # 교차 패턴 체크 (문자+숫자+문자+숫자)
    def check_alternate(start_digit):
        if len(pwd) % 2 != 0:
            return False
        expect_digit = start_digit
        for c in pwd:
            if expect_digit and not c.isdigit():
                return False
            if not expect_digit and not c.isalpha():
                return False
            expect_digit = not expect_digit
        return True

    return check_alternate(True) or check_alternate(False)


def read_password():
    pass


def write_password(password):
    try:
        with open(PASSWORD_PATH, 'w') as f:
            f.write(password)
    except Exception as e:
        print(f'❌ Failed to write password: {e}')


if __name__ == '__main__':
    unlock_zip()

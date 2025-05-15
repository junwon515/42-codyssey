import zipfile
import time
import itertools

PARENT_PATH = 'program_2/mission_1/'
ZIP_PATH = PARENT_PATH + 'emergency_storage_key.zip'
PASSWORD_PATH = PARENT_PATH + 'password.txt'

CHAR_GROUP = 'etaoinshrdlucmfwypvbgkqjxz'
NUMERIC = '0123456789'
MAX_LENGTH = 6

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
            print(f'\n✅ Password found: {pwd}')
            print(f'🔁 Total attempts: {attempts}')
            print(f'⏱ Time taken: {duration:.2f} seconds')
            write_password(pwd)
            return True
        except:
            if attempts % 1000 == 0:
                elapsed = time.time() - start_time
                print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] '
                      f'Trying: {pwd} | Attempts: {attempts//1000}K | Time: {elapsed:.2f}s', end='\r')
            return False

    for i in range(0, len(CHAR_GROUP) + 1):
        if i == 0:
            current_charset = NUMERIC
            new_char = None
        else:
            current_charset = CHAR_GROUP[:i] + NUMERIC
            new_char = CHAR_GROUP[i - 1]

        for length in range(1, MAX_LENGTH + 1):
            for pwd_tuple in itertools.product(current_charset, repeat=length):
                pwd = ''.join(pwd_tuple)

                if new_char and new_char not in pwd:
                    continue
                if try_password(pwd):
                    return
                
    print("\n❇️ Password not found.")

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
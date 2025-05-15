import zipfile
import time

PARENT_PATH = 'program_2/mission_1/'
ZIP_PATH = PARENT_PATH + 'emergency_storage_key.zip'
PASSWORD_PATH = PARENT_PATH + 'password.txt'

CHARSET = 'etaoinshrdlucmfwypvbgkqjxz0123456789'
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

    def brute_force(pwd, depth):
        nonlocal attempts
        if depth == 0:
            attempts += 1
            try:
                zip_file.read(zip_file.namelist()[0], pwd=bytes(pwd, 'utf-8'))
                
                duration = time.time() - start_time
                print(f'\nPassword found: {pwd}')
                print(f'Total attempts: {attempts}')
                print(f'Time taken: {duration:.2f} seconds')

                write_password(pwd)

                return True
            except:
                if attempts % 1000 == 0:
                    elapsed = time.time() - start_time
                    print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] Password : {pwd} | Attempts: {attempts//1000} K | Elapsed Time: {elapsed:.2f} seconds', end='\r')
                return False
        else:
            for c in CHARSET:
                if brute_force(pwd + c, depth - 1):
                    return True
        return False

    if brute_force('', MAX_LENGTH):
        return
    print("\n❇️  Password not found.")

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
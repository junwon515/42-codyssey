PARENT_PATH = '0304/2-2/'
PASSWORD_PATH = PARENT_PATH + 'password.txt'
RESULT_PATH = PARENT_PATH + 'result.txt'
DICTIONARY_PATH = PARENT_PATH + 'dictionary.txt'


def caesar_cipher_decode(target_text, shift):
    decoded_text = ''
    for char in target_text:
        if char.isalpha():
            ascii_offset = ord('A') if char.isupper() else ord('a')
            decoded_char = chr((ord(char) - ascii_offset - shift) % 26 + ascii_offset)
            decoded_text += decoded_char
        else:
            decoded_text += char
    return decoded_text


def read_password():
    try:
        with open(PASSWORD_PATH) as f:
            password = f.read().strip()
        return password
    except FileNotFoundError:
        print(f'❌ Error: The file {PASSWORD_PATH} was not found.')
    except Exception as e:
        print(f'❌ An error occurred while reading the password file: {e}')
    return None


def read_dictionary():
    try:
        with open(DICTIONARY_PATH) as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        print(f'❌ Error: The file {DICTIONARY_PATH} was not found.')
    except Exception as e:
        print(f'❌ An error occurred while reading the dictionary file: {e}')
    return None


def write_result(result):
    try:
        with open(RESULT_PATH, 'w') as f:
            f.write(result)
        print(f'✅ The decoded password has been saved to {RESULT_PATH}.')
    except Exception as e:
        print(f'❌ An error occurred while writing to the result file: {e}')


def auto_decode_password(password):
    dictionary = read_dictionary()
    if dictionary is None:
        return False

    print('\n🔍 Trying to decode the password using dictionary match...')
    for shift in range(1, 27):
        decoded_text = caesar_cipher_decode(password, shift)
        decoded_words = decoded_text.split()
        found_words = [word for word in decoded_words if word.lower() in dictionary]
        if found_words:
            print(f'\n🔑 Found potential match (Shift {shift}): {decoded_text}')
            print(f'📚 Matched words: {", ".join(found_words)}')
            choice = (
                input('💾 Do you want to save this decoded password? (y/n): ')
                .strip()
                .lower()
            )
            if choice in ('y', 'yes'):
                write_result(decoded_text)
                return True

    return False


def manual_decode_password(password):
    print('\n🔍 Listing all possible Caesar cipher shifts (1-26):')
    for shift in range(1, 27):
        decoded_text = caesar_cipher_decode(password, shift)
        print(f'{shift:2d}. {decoded_text}')

    print('\n🔢 Enter the shift value you believe is correct')
    try:
        shift = int(input('➡️  Shift value (1-26): '))
        if 1 <= shift <= 26:
            decoded_password = caesar_cipher_decode(password, shift)
            print(f'\n🔓 Decoded password: {decoded_password}')
            write_result(decoded_password)
        else:
            print('❌ Error: The shift value must be between 1 and 26.')
    except ValueError:
        print('❌ Error: Please enter a valid integer for the shift value.')


def main():
    password = read_password()
    if password is None:
        return

    print(f'\n🔐 Encrypted password: {password}')
    choice = (
        input(
            '\n🤖 Would you like the program to try decoding it automatically? (y/n): '
        )
        .strip()
        .lower()
    )

    if choice in ('y', 'yes'):
        if auto_decode_password(password):
            return
        print('\n🤖 No matches found. You can try decoding it manually.')

    manual_decode_password(password)


if __name__ == '__main__':
    main()

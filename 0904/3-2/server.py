import socket
import threading
from contextlib import suppress

HOST = '127.0.0.1'
PORT = 9999
RECV_BUF = 1024

# 공유 상태
clients: dict[socket.socket, str] = {}
last_whisper_partner: dict[socket.socket, str] = {}
usernames: set[str] = set()
lock = threading.Lock()


def send_to(socket: socket.socket, text: str):
    try:
        socket.send(text.encode('utf-8'))
    except (ConnectionResetError, OSError):
        remove_client(socket, announce=False)


def broadcast(text: str, exclude: socket.socket | None = None):
    with lock:
        targets = [s for s in clients if s is not exclude]
    if not targets:
        return
    dead: list[socket.socket] = []
    encoded = text.encode('utf-8')
    for s in targets:
        try:
            s.send(encoded)
        except (ConnectionResetError, OSError):
            dead.append(s)
    if dead:
        for s in dead:
            remove_client(s, announce=False)


def remove_client(client_socket: socket.socket, announce: bool = True):
    with lock:
        username = clients.pop(client_socket, None)
        if username:
            usernames.discard(username)
        last_whisper_partner.pop(client_socket, None)

    if username:
        print(f"[알림] '{username}'님이 퇴장하셨습니다.")
        if announce:
            broadcast(f"[알림] '{username}'님이 퇴장하셨습니다.")

    with suppress(OSError):
        client_socket.close()


def prompt_username(client_socket: socket.socket) -> str | None:
    send_to(client_socket, '닉네임을 입력하세요 (/종료 입력 시 연결 종료): ')
    while True:
        try:
            data = client_socket.recv(RECV_BUF)
        except (ConnectionResetError, OSError):
            return None
        if not data:
            return None
        proposed = data.decode('utf-8').strip()
        if proposed == '/종료':
            send_to(client_socket, '연결을 종료합니다.')
            return None
        if not proposed:
            send_to(client_socket, '빈 닉네임은 사용할 수 없습니다. 다시 입력: ')
            continue
        with lock:
            if proposed in usernames:
                send_to(
                    client_socket, f"'{proposed}' 는 이미 사용 중입니다. 다른 닉네임: "
                )
                continue
            usernames.add(proposed)
            clients[client_socket] = proposed
            return proposed


def process_command(socket: socket.socket, username: str, message: str) -> bool:
    # 반환: True 계속, False 종료
    if message == '/종료':
        return False

    if message.startswith('/w '):
        parts = message.split(' ', 2)
        if len(parts) != 3:
            send_to(socket, '귓속말 형식이 올바르지 않습니다. (/w 이름 메시지)')
            return True
        target_username, whisper_msg = parts[1], parts[2]
        if target_username == username:
            send_to(socket, '자기 자신에게 귓속말을 보낼 수 없습니다.')
            return True
        with lock:
            target_sock = next(
                (s for s, u in clients.items() if u == target_username), None
            )
        if not target_sock:
            send_to(socket, f"'{target_username}'님을 찾을 수 없습니다.")
            return True
        send_to(target_sock, f'[귓속말] {username}>> {whisper_msg}')
        send_to(socket, f'[귓속말] {target_username}<< {whisper_msg}')
        with lock:
            last_whisper_partner[socket] = target_username
            last_whisper_partner[target_sock] = username
        return True

    if message.startswith('/r '):
        parts = message.split(' ', 1)
        if len(parts) != 2 or not parts[1].strip():
            send_to(socket, '답장 형식이 올바르지 않습니다. (/r 메시지)')
            return True
        reply_msg = parts[1].strip()
        with lock:
            partner_username = last_whisper_partner.get(socket)
        if not partner_username:
            send_to(socket, '최근 귓속말 대상이 없습니다.')
            return True
        with lock:
            partner_sock = next(
                (s for s, u in clients.items() if u == partner_username), None
            )
        if not partner_sock:
            send_to(socket, '이전 귓속말 대상이 현재 접속 중이 아닙니다.')
            return True
        if partner_username == username:
            send_to(socket, '자기 자신에게 답장을 보낼 수 없습니다.')
            return True
        send_to(partner_sock, f'[귓속말] {username}>> {reply_msg}')
        send_to(socket, f'[귓속말] {partner_username}<< {reply_msg}')
        with lock:
            last_whisper_partner[socket] = partner_username
            last_whisper_partner[partner_sock] = username
        return True

    # 일반 메시지
    formatted = f'[일반] {username}: {message}'
    print(formatted)
    broadcast(formatted, exclude=socket)
    return True


def handle_client(client_socket: socket.socket, addr: tuple[str, int]):
    print(f'[알림] 새로운 클라이언트 접속: {addr}')
    try:
        username = prompt_username(client_socket)
        if not username:
            remove_client(client_socket, announce=False)
            return

        print(f"[알림] '{username}'님이 입장하셨습니다. (주소: {addr})")
        broadcast(f"[알림] '{username}'님이 입장하셨습니다.", exclude=client_socket)
        send_to(
            client_socket,
            '채팅방에 입장했습니다. (/종료 퇴장, /w 이름 메시지 귓속말, /r 메시지 최근 대상 답장)',
        )

        while True:
            try:
                data = client_socket.recv(RECV_BUF)
            except (ConnectionResetError, OSError):
                break
            if not data:
                break
            message = data.decode('utf-8').strip()
            if not message:
                continue
            if not process_command(client_socket, username, message):
                break

    except ConnectionResetError:
        print(
            f"[오류] '{clients.get(client_socket, '알 수 없는 사용자')}' 연결 비정상 종료"
        )
    finally:
        remove_client(client_socket)


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.settimeout(1)
    print(f'[알림] 채팅 서버 시작: {HOST}:{PORT}')
    try:
        while True:
            try:
                client_socket, addr = server_socket.accept()
            except TimeoutError:
                continue
            threading.Thread(
                target=handle_client, args=(client_socket, addr), daemon=True
            ).start()
    except KeyboardInterrupt:
        print('[알림] 서버를 종료합니다.')
    finally:
        server_socket.close()


if __name__ == '__main__':
    start_server()

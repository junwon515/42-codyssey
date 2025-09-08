import socket
import threading

HOST = '127.0.0.1'
PORT = 9999
RECV_BUF = 1024


def safe_send(sock: socket.socket, text: str):
    try:
        sock.send(text.encode('utf-8'))
    except OSError:
        pass


def receiver(sock: socket.socket, stop_event: threading.Event):
    while not stop_event.is_set():
        try:
            data = sock.recv(RECV_BUF)
        except (ConnectionResetError, OSError):
            print('[알림] 서버와의 연결이 끊어졌습니다.')
            break
        if not data:
            print('[알림] 서버가 연결을 종료했습니다.')
            break
        print(data.decode('utf-8'))
    stop_event.set()


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print('[오류] 서버에 연결할 수 없습니다.')
        return

    stop_event = threading.Event()

    receive_thread = threading.Thread(
        target=receiver, args=(client_socket, stop_event), daemon=True
    )
    receive_thread.start()

    try:
        while not stop_event.is_set():
            try:
                line = input()
            except EOFError:
                line = '/종료'
            if not line.strip():
                continue
            if line == '/종료':
                safe_send(client_socket, line)
                break
            safe_send(client_socket, line)
    except KeyboardInterrupt:
        print('\n[알림] 사용자 종료')
    finally:
        stop_event.set()

    try:
        client_socket.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    client_socket.close()
    receive_thread.join(timeout=0.5)


if __name__ == '__main__':
    start_client()

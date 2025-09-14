import datetime
import http.server
import json
import socket
import threading

HOST = '127.0.0.1'
PORT = 8080

IPINFO_HOST = 'ipinfo.io'
IPINFO_PORT = 80
SOCKET_TIMEOUT = 3.0
CACHE_TTL_SECONDS = 600

_ip_cache = {}
_cache_lock = threading.RLock()
_inflight = {}
_inflight_lock = threading.Lock()

try:
    with open('index.html', 'rb') as f:
        INDEX_HTML_CONTENT = f.read()
except FileNotFoundError:
    print('index.html 파일을 찾을 수 없습니다. 서버를 시작할 수 없습니다.')
    exit(1)


def _now_ts():
    return int(datetime.datetime.now().timestamp())


def _get_cached(ip):
    with _cache_lock:
        item = _ip_cache.get(ip)
        if not item:
            return None
        ts, value = item
        if _now_ts() - ts > CACHE_TTL_SECONDS:
            _ip_cache.pop(ip, None)
            return None
        return value


def _set_cached(ip, value):
    with _cache_lock:
        _ip_cache[ip] = (_now_ts(), value)


def get_location_info(ip_address):
    cached = _get_cached(ip_address)
    if cached is not None:
        return cached

    with _inflight_lock:
        evt = _inflight.get(ip_address)
        if evt is None:
            evt = threading.Event()
            _inflight[ip_address] = evt
            is_creator = True
        else:
            is_creator = False

    if not is_creator:
        evt.wait(SOCKET_TIMEOUT + 2)
        post = _get_cached(ip_address)
        return post if post is not None else 'Location info not available'

    try:
        request_path = f'/{ip_address}/json'
        server_ip = socket.gethostbyname(IPINFO_HOST)
        with socket.create_connection(
            (server_ip, IPINFO_PORT), timeout=SOCKET_TIMEOUT
        ) as s:
            s.settimeout(SOCKET_TIMEOUT)
            request_message = (
                f'GET {request_path} HTTP/1.1\r\n'
                f'Host: {IPINFO_HOST}\r\n'
                f'User-Agent: Python-socket-client\r\n'
                f'Accept: application/json\r\n'
                f'Accept-Encoding: identity\r\n'
                'Connection: close\r\n\r\n'
            )
            s.sendall(request_message.encode('utf-8'))

            response_data = b''
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response_data += chunk

        header_part, body = response_data.split(b'\r\n\r\n', 1)
        header_lines = header_part.decode('utf-8', errors='ignore').split('\r\n')
        status_line = header_lines[0]

        version, status_code, reason = status_line.split(' ', 2)
        if status_code != '200':
            print(
                f'Error: Received status code {status_code} {reason} for IP {ip_address}'
            )
            return 'Location info not available'

        location_info = json.loads(body.decode('utf-8'))
        where = '/'.join(
            location_info.get(k, '')
            for k in ('city', 'region', 'country')
            if location_info.get(k)
        )
        parts = [where] + [
            location_info.get(k, '')
            for k in ('org', 'loc', 'timezone')
            if location_info.get(k)
        ]
        result = ' | '.join(filter(None, parts))

        if result:
            _set_cached(ip_address, result)
        return result or 'Location info not available'

    except Exception as e:
        print(f'Error fetching location info for {ip_address}: {e}')
        return 'Location info not available'

    finally:
        with _inflight_lock:
            _inflight.pop(ip_address, None)
        evt.set()


class HttpRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = self.client_address[0]
        location_info = get_location_info(client_ip)
        print(f'[{log_time}] {client_ip} - {location_info}')

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(INDEX_HTML_CONTENT)))
            self.end_headers()
            self.wfile.write(INDEX_HTML_CONTENT)
        except Exception as e:
            print(f'Error handling request from {self.client_address[0]}: {e}')


def start_server():
    httpd = http.server.ThreadingHTTPServer((HOST, PORT), HttpRequestHandler)

    server_host = (
        'localhost'
        if HOST == '127.0.0.1'
        else socket.gethostbyname(socket.gethostname())
    )
    print(f'서버가 시작되었습니다. http://{server_host}:{PORT} 에서 접속하세요.')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('서버를 종료합니다.')
    finally:
        httpd.server_close()


if __name__ == '__main__':
    start_server()

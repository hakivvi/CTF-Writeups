from pydoc import cli
import socket
import time
import threading
import re

class HTTPTunnel:
    def __init__(self, client_socket, backend_host='feed', backend_port=9292):
        self.client_socket = client_socket
        self.backend_host = backend_host
        self.backend_port = backend_port
        self.backend = None
        self.requests_count = 0
        self.client_id = []

    def connect_to_backend(self):
        self.backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.backend.connect((self.backend_host, self.backend_port))
        self.backend.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def handle_connection(self):
        self.connect_to_backend()

        while True:
            try:
                request_headers = self.read_request()
                if not request_headers:
                    break
                if self.requests_count > 0:
                    client_id = self.get_client_id(request_headers)
                    if client_id != self.client_id:
                        self.client_socket.sendall(b"HTTP/1.1 401 Unauthorized\r\nContent-Length: 20\r\nConnection: close\r\n\r\nNot Your HTTPTunnel.")
                        continue
                content_length = self.get_content_length(request_headers)
                body = self.read_request_body(content_length) if content_length > 0 else ''
                response = self.forward_request(request_headers, body)
                self.client_socket.sendall(response)
                self.requests_count += 1
            except Exception as e:
                print(e)
                break

        self.client_socket.close()
        self.backend.close()

    def read_request(self):
        request_headers = []
        while True:
            line = self.read_line(self.client_socket)
            if not line or line == '':
                break
            request_headers.append(line)
        return request_headers

    def get_content_length(self, request_headers):
        for header in request_headers:
            if header.lower().startswith('content-length'):
                return int(header.split(': ')[1])
        return 0
    
    def get_client_id(self, request_headers):
        md5_regex = re.compile(r'^[a-f0-9]{32}$')

        for header in request_headers:
            if header.lower().startswith('cookie'):
                cookie_string = header.split(':', 1)[1].strip()

                cookies = {k.strip(): v.strip() for k, v in 
                           (cookie.split('=') for cookie in cookie_string.split(';'))}
                
                client_id = cookies.get('client_id')
                
                if client_id and md5_regex.match(client_id):
                    return client_id
                
        return ''

    def read_request_body(self, content_length):
        if content_length > 0:      
            body = self.client_socket.recv(content_length)
            if body == b'':
                raise Exception("Client disconnected.")
            return body
        return ''

    def forward_request(self, request_headers, body):
        self.start_time = time.time()
        for header in request_headers:
            self.backend.sendall(f'{header}\r\n'.encode())
        self.backend.sendall(b'\r\n')
        if body:
            self.backend.sendall(body)


        response_line = self.read_line(self.backend).strip()
        response_headers = []

        while True:
            line = self.read_line(self.backend)
            if not line or line == '':
                break
            if line.startswith('X-Client-Id'):
                self.client_id = line.split(': ')[1].strip()
            response_headers.append(line)
        
        response_time = (time.time() - self.start_time) * 1000
        response_headers.append(f'X-Response-Time: {response_time:.2f}ms')
        response_headers.append("Content-Security-Policy: default-src 'none'; script-src 'none'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; font-src 'none'; object-src 'none'; frame-src https://en.wikipedia.org/wiki/Special:Random; media-src 'none'; worker-src 'none'")
        response_body = self.read_response_body(response_headers)

        return (response_line + '\r\n' + '\r\n'.join(response_headers) + '\r\n' + '\r\n').encode() + response_body

    def read_response_body(self, response_headers):
        for header in response_headers:
            if header.lower().startswith('content-length'):
                content_length = int(header.split(': ')[1])
                if content_length > 0:      
                    body = self.backend.recv(content_length)
                    if body == b'':
                        raise Exception("Backend disconnected.")
                    return body
        return ''

    def read_line(self, sock):
        line = bytearray()
        while True:
            char = sock.recv(1)
            if char == b'':
                raise Exception(f"Peer disconnected.")
            if char == b'\n':
                return line.decode().rstrip('\r\n')
            elif char:
                line.extend(char)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('127.0.0.1', 8888))
server_socket.listen(50)

print("Listening on 127.0.0.1:8888")

while True:
    client_socket, addr = server_socket.accept()
    client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    print(f"Accepted connection from {addr}")
    tunnel = HTTPTunnel(client_socket)
    threading.Thread(target=tunnel.handle_connection).start()

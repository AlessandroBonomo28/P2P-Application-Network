import socket
import time

buf_size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

"""s.bind(('127.0.0.1',10101))
(buf,address)=s.recvfrom(buf_size)
if not len(buf):
    print("wtf")
print ("received",address, buf.decode())"""

msg = "Hello everyone!"
dest = ('192.168.1.255',10100)

try:
    while True:
        s.sendto(msg.encode(), dest)
        time.sleep(2)
except:
    print ("exit")



s.close()
"""print ("Sent broadcast. Looking for replies")
while 1:
    (buf,address)=s.recvfrom(buf_size)
    if not len(buf):
        break
    print ("received",address, buf.decode())
"""

import socket

msg = "Hello everyone!"
dest = ('192.168.1.255',10100)
buf_size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.sendto(msg.encode(), dest)

print ("Sent broadcast. Looking for replies")
while 1:
    (buf,address)=s.recvfrom(buf_size)
    if not len(buf):
        break
    print ("received",address, buf.decode())
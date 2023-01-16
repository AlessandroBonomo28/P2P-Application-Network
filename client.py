import socket

host = ''
port = 10100
buf_size = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # ?
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((host,port))

print("Waiting for server broadcast...")
while 1:
    try:
        message, address = s.recvfrom(buf_size)
        print ("Got data from", address)
        print ("Data:", message.decode())
        s.sendto("Hello server!".encode(), address)
    except KeyboardInterrupt:
        print("bye")
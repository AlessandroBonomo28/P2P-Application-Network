import socket
import time
import select
from protocol import DatagramP2P,HeaderP2P,PayloadP2P,HostP2P,ProtocolP2P
buf_size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

s.bind(('0.0.0.0',10101))

print ("Looking for broadcast...")
(buf,address)=s.recvfrom(buf_size)
print ("received",address, buf.decode())

print("Trying to connect: ",address)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((address[0],5000))
my_p2p_host = HostP2P()

datagram = DatagramP2P(
    header=HeaderP2P(host=my_p2p_host),
    payload=PayloadP2P(message="PING")
)

#client_socket.send(datagram_json.encode())
ProtocolP2P.send_datagram(client_socket,datagram)
try:
    
    
    client_socket.setblocking(0)
    

    ready = select.select([client_socket], [], [], 5)
    if ready[0]:
        msg = client_socket.recv(buf_size)
    else:
        raise Exception('timed out')

    #msg = client_socket.recv(buf_size)
    print("received ",msg.decode())

    datagram = DatagramP2P(
    header=HeaderP2P(HostP2P(),"123"),
    payload=PayloadP2P(message="END")
    )

    #client_socket.send("END".encode())
    ProtocolP2P.send_datagram(client_socket,datagram)
except Exception as e:
    print("err while communicating",e)
client_socket.close()

"""
msg = "Hello everyone!"
dest = ('192.168.1.255',10100)

try:
    while True:
        s.sendto(msg.encode(), dest)
        time.sleep(2)
except:
    print ("exit")

"""

s.close()

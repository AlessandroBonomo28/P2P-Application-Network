import socket
from protocol import Host
import threading, time

class ServerP2P():

    def broadcast_receiver(self):
        try:
            while True:
                print ("Looking for broadcast replies...")
                (buf,address)=self.sock_broad_listen.recvfrom(self.buffer_size)
                if not len(buf):
                    raise Exception('Buffer empty read')
                print ("received",address, buf.decode())
        except Exception as e:
            print("Exception in thread broadcast receiver",e)

    def __init__(self, my_p2p_host : Host, broad_listen_port : int, broad_send_port, buffer_size: int = 1024, broad_addr='192.168.1.255' ) -> None:
        self.broad_listen_port = broad_listen_port
        self.broad_send_port = broad_send_port
        self.buffer_size = buffer_size
        self.broad_addr = broad_addr
        self.host = '0.0.0.0' 
        self.my_p2p_host = my_p2p_host
        self.sock_broad_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_broad_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_broad_listen.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock_broad_listen.bind((self.host,broad_listen_port))

        self.sock_broad_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_broad_send.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        thread = threading.Thread(target=self.broadcast_receiver).start()

    def send_discovery_broadcast(self) -> None:
        message = self.my_p2p_host.to_json().encode()
        dest = (self.broad_addr,self.broad_send_port)
        self.sock_broad_send.sendto(message, dest)
    
    def close_broadcast(self):
        self.sock_broad_listen.shutdown(socket.SHUT_RDWR)
        self.sock_broad_listen.close()

        self.sock_broad_send.close()
    


broad_listen_port = 10100
broad_send_port = 10101
my_p2p_host = Host()
p2p_server = ServerP2P(my_p2p_host,broad_listen_port=broad_listen_port,
                        broad_send_port=broad_send_port)


p2p_server2 = ServerP2P(my_p2p_host,broad_listen_port=10101,
                        broad_send_port=10100)

#p2p_server.send_discovery_broadcast()
try:
    while(True):
        p2p_server.send_discovery_broadcast()
        print("sleep")
        time.sleep(1)
except:
    print("exit")
    p2p_server.close_broadcast()
    p2p_server2.close_broadcast()








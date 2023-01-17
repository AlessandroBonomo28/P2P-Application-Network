import socket
from protocol import Host,DatagramP2P,HeaderP2P,PayloadP2P, ProtocolP2P
import threading, time

class HostList():
     

    def update(self, host : Host):
        self.host_list[host.id] = host

    def remove(self, host: Host):
        del self.host_list[host.id]


    def __init__(self) -> None:
        self.host_list = {}

class ServerP2P():
    BACKLOG_TCP_ACCEPTED_CONNECTIONS = 5
    def handle_client(self,conn : socket.socket, addr):
        try:
            print("Authenticated")
        except:
            return

        while True:
            try:
                datagram = ProtocolP2P.recv_datagram(conn)
                msg = datagram.payload.message
                if msg == "END":
                    print("datagram=",datagram.header,datagram.payload)
                    print("Ending connection ",addr)
                    break
                elif msg == "PING":
                    #pass
                    conn.send("PONG".encode())
                elif msg == "HOSTS":
                    #pass
                    conn.send("PONG".encode())
                else:
                    conn.send("INVALID COMMAND".encode())
            except Exception as e:
                print("Exception while communicating",e)
                break
        conn.close()

    def accept_clients(self):
        try:
            while True:
                conn , addr = self.tcp_accept_socket.accept()
                print ("New client accepted: ",addr)
                threading.Thread(target=self.handle_client,args=(conn,addr),daemon=True).start()
        except Exception as e:
            print("Exception in thread accept clients",e)

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

    def __init__(self, my_p2p_host : Host, tcp_accept_port: int, broad_listen_port : int, broad_send_port, buffer_size: int = 1024, broad_addr='192.168.1.255' ) -> None:
        self.ingoing_hosts = HostList()
        self.outgoing_hosts = HostList()

        self.tcp_accept_port = tcp_accept_port
        self.broad_listen_port = broad_listen_port
        self.broad_send_port = broad_send_port
        self.buffer_size = buffer_size
        self.broad_addr = broad_addr
        self.host = '0.0.0.0' 
        self.my_p2p_host = my_p2p_host

        self.tcp_accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_accept_socket.bind((self.host, tcp_accept_port))
        self.tcp_accept_socket.listen(self.BACKLOG_TCP_ACCEPTED_CONNECTIONS)

        self.sock_broad_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_broad_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_broad_listen.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock_broad_listen.bind((self.host,broad_listen_port))

        self.sock_broad_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_broad_send.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.send_discovery_broadcast()

        threading.Thread(target=self.broadcast_receiver, daemon=True).start()
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def send_discovery_broadcast(self) -> None:
        message = self.my_p2p_host.to_json().encode()
        dest = (self.broad_addr,self.broad_send_port)
        self.sock_broad_send.sendto(message, dest)
    
    def close_broadcast(self):
        self.sock_broad_listen.shutdown(socket.SHUT_RDWR)
        self.sock_broad_listen.close()

        self.sock_broad_send.close()
    
    def close_tcp_accept(self):
        self.tcp_accept_socket.close()

    def close(self):
        self.close_broadcast()
        self.close_tcp_accept()
    


broad_listen_port = 10100
broad_send_port = 10101
my_p2p_host = Host()
p2p_server = ServerP2P(my_p2p_host, tcp_accept_port=5000, broad_listen_port=broad_listen_port,
                        broad_send_port=broad_send_port)


#p2p_server2 = ServerP2P(my_p2p_host,tcp_accept_port=5001, broad_listen_port=10101,
#                        broad_send_port=10100)

#p2p_server.send_discovery_broadcast()
try:
    while(True):
        p2p_server.send_discovery_broadcast()
        print("sleep")
        time.sleep(1)
except:
    print("exit")
    p2p_server.close()
    #p2p_server2.close_broadcast()








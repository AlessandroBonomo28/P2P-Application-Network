import socket
from protocol import HostP2P, ProtocolP2P,DatagramP2P
import threading, time, json
import p2p_exceptions

class HostList():
    def __iter__(self):
        self.i = 0
        self.__keys = list(self.host_list.keys())
        return self
    
    def __next__(self):
        if self.i < len(self.host_list):
            self.i +=1
            k = self.__keys[self.i-1]
            return self.host_list[k]
        else:
            raise StopIteration


    def exists_host_id(self, host_id : str):
        try:
            self.get_host_by_id(host_id)
            return True
        except:
            return False
    
    def get_conn(self,host_id: str):
        try:
            return self.host_list[host_id]["conn"]
        except:
            raise p2p_exceptions.ConnectionNotFound('Connection was not found')
    
    def get_host_by_id(self,host_id: str):
        try:
            return self.host_list[host_id]["host"]
        except:
            raise p2p_exceptions.HostNotFound('Host was not found')

    def print_hosts(self):
        for i in self.host_list:
            print(self.host_list[i]["host"].id, self.host_list[i]["conn"].getpeername())
    
    def update(self, host : HostP2P, conn : socket.socket = None):
        self.host_list[host.id] = {"host": host, "conn":conn}

    def remove(self, host_id: str):
        del self.host_list[host_id]


    def __init__(self) -> None:
        self.host_list = {}

class ServerP2P():
    BACKLOG_TCP_ACCEPTED_CONNECTIONS = 200

    def __check_broken_host(self, host: HostP2P):
        try:
            conn = self.outgoing_hosts.get_conn(host.id)
            ProtocolP2P.send_TCP_datagram(DatagramP2P(message="PING"))
            ProtocolP2P.recv_TCP_datagram(conn,5)
        except:
            raise p2p_exceptions.BrokenHost('Host did not respond to ping')

    def establish_outgoing_conn(self,host : HostP2P, ip_address : str):
        if host.id == self.my_p2p_host.id:
            raise p2p_exceptions.SelfConnectNotAllowed('Cannot connect to self')
        if self.outgoing_hosts.exists_host_id(host.id):
                try:
                    self.__check_broken_host(host)
                    raise p2p_exceptions.OutgoingConnectionException("Outgoing connection already exists")
                except:
                    print("Removed broken host")
                    self.outgoing_hosts.remove(host.id)
              
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            conn.connect((ip_address,self.tcp_accept_port))
            datagram = DatagramP2P(host=self.my_p2p_host)
            ProtocolP2P.send_TCP_datagram(conn,datagram)
        except:
            conn.close()
            raise p2p_exceptions.FailToConnectToP2PServer('Could not connect to P2P server')
        self.outgoing_hosts.update(host,conn)
        return conn

    def handle_ingoing_conn(self,conn : socket.socket, addr):
        try:
            datagram = ProtocolP2P.recv_TCP_datagram(conn,timeout=5)
            host_id = datagram.host.id
            if self.ingoing_hosts.exists_host_id(host_id):
                raise p2p_exceptions.IngoingConnectionException("Host already connected")
        except Exception as e:
            print("Rejected host",addr, "\nReason of reject:",e)
            conn.close()
            return
        ProtocolP2P.send_TCP_datagram(conn,DatagramP2P(message="authenticated"))
        self.ingoing_hosts.update(datagram.host, conn)
        current_host : HostP2P = datagram.host
        print("Authenticated",addr)
        
        while True:
            try:
                datagram = ProtocolP2P.recv_TCP_datagram(conn)
                msg = datagram.message

                if msg == "END":
                    print("Ending connection ",addr)
                    break
                elif msg == "PING":
                    ProtocolP2P.send_TCP_datagram(conn,DatagramP2P(message="PONG"))
                elif msg == "HOSTS":
                    hosts = []
                    for i in self.ingoing_hosts:
                        hosts.append(i["host"].to_json())
                    ProtocolP2P.send_TCP_datagram(conn,DatagramP2P(
                        message="HOSTS",
                        data=hosts
                        ))
                else:
                    ProtocolP2P.send_TCP_datagram(conn,DatagramP2P(status_code=-1, message="INVALID"))
            except Exception as e:
                print("Exception while communicating",e)
                break
        conn.close()
        self.ingoing_hosts.remove(host_id)
        print("Closed ingoing connection with",addr)
    
    def accept_ingoing_connections(self):
        try:
            while True:
                conn , addr = self.tcp_accept_socket.accept()
                print ("New client accepted: ",addr)
                threading.Thread(target=self.handle_ingoing_conn,args=(conn,addr),daemon=True).start()
        except Exception as e:
            print("Exception in thread accept clients",e)

    def broadcast_receiver(self):
        try:
            while True:
                print ("Looking for broadcast...")
                datagram ,address = ProtocolP2P.recv_UDP_datagram(self.sock_broad_listen)

                print ("received broadcast from ",address)
                try:
                    host = datagram.host
                    self.establish_outgoing_conn(host,address[0])
                    if datagram.message == "DISCOVERY":
                        datagram = DatagramP2P(message="DISCOVERY-RESPONSE",host=self.my_p2p_host)
                        dest = (address[0],self.broad_send_port)
                        ProtocolP2P.send_UDP_datagram(self.sock_broad_send,datagram,dest)
                    elif datagram.message == "DISCOVERY-RESPONSE":
                        print("Received discovery response from ",address)
                except Exception as e:
                    if isinstance(e,p2p_exceptions.SelfConnectNotAllowed):
                        print("ignored self broadcast")
                        continue
                    else:
                        print("Could not decode broadcast message from ",address, "Exception",e,"\n")

                
        except Exception as e:
            self.sock_broad_listen.close()
            print("Exception in thread broadcast receiver",e)

    def __init__(self, my_p2p_host : HostP2P, tcp_accept_port: int, broad_listen_port : int, broad_send_port, buffer_size: int = 1024, broad_addr='255.255.255.255' ) -> None:
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
        self.tcp_accept_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        threading.Thread(target=self.accept_ingoing_connections, daemon=True).start()

    def send_discovery_broadcast(self) -> None:
        datagram = DatagramP2P(message="DISCOVERY",host=self.my_p2p_host)
        dest = (self.broad_addr,self.broad_send_port)
        ProtocolP2P.send_UDP_datagram(self.sock_broad_send,datagram,dest)
        print("Broadcast sent...")

    def close_broadcast(self):
        self.sock_broad_listen.close()
        self.sock_broad_send.close()
    
    def close_all_ingoing_connections(self):
        for i in self.ingoing_hosts:
            i["conn"].close()

    def close_all_outgoing_connections(self):
        for i in self.outgoing_hosts:
            i["conn"].close()

    def close_tcp_accept(self):
        self.tcp_accept_socket.close()

    def close(self):
        self.close_broadcast()
        self.close_tcp_accept()
        self.close_all_ingoing_connections()
        self.close_all_outgoing_connections()
    


broad_listen_port = 10100
broad_send_port = 10100
my_p2p_host = HostP2P()
p2p_server = ServerP2P(my_p2p_host, tcp_accept_port=6969, broad_listen_port=broad_listen_port,
                        broad_send_port=broad_send_port)


#p2p_server2 = ServerP2P(my_p2p_host,tcp_accept_port=5001, broad_listen_port=10101,
#                        broad_send_port=10100)
SLEEP_TIME = 5
#p2p_server.send_discovery_broadcast()
try:
    while(True):
        #p2p_server.send_discovery_broadcast()
        print("-"*40)
        print("Status ingoing: ",len(p2p_server.ingoing_hosts.host_list))
        p2p_server.ingoing_hosts.print_hosts()
        print("Status outgoing: ",len(p2p_server.outgoing_hosts.host_list))
        p2p_server.outgoing_hosts.print_hosts()
        print("go to sleep for",SLEEP_TIME)
        time.sleep(SLEEP_TIME)
except:
    print("exit")
    p2p_server.close()
    #p2p_server2.close_broadcast()








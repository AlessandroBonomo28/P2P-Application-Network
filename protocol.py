import uuid, json, socket
import netifaces, select
import p2p_exceptions
class Host():
    @staticmethod
    def from_json(json_dict : dict):
        id = str(json_dict["id"])
        name = str(json_dict["name"])
        group = int(json_dict["group"])
        ip_addr = str(json_dict["ip_addr"])
        host = Host(id=id,name=name,group=group,ip_addr=ip_addr)
        return host
    

    def __get_my_ip(self):
        iface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        ip_addr = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
        return ip_addr
    
    def __init__(self, ip_addr = None, id : str = str(uuid.uuid4()), name : str ="Host",
                 group : int=0) -> None:
        self.id = id
        self.name = name
        self. group = group
        if not ip_addr:
            ip_addr = self.__get_my_ip()
        self.ip_addr = ip_addr
        
    def to_json(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
    
    def __str__(self)-> str:
        return "Host "+str(vars(self))

class HeaderP2P():

    @staticmethod
    def from_json(json_dict : dict):
        if not json_dict["host"]:
            return HeaderP2P(token=json_dict["token"])
        auth_header = HeaderP2P(
            Host.from_json(json_dict["host"]),
            json_dict["token"]
        )
        return auth_header


    def __init__(self, host : Host=None, token : str = None) -> None:
        self.host = host
        self.token = token
    
    def to_json(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
    
    def __str__(self)-> str:
        return "HeaderP2P "+str(vars(self))



class PayloadP2P():
    @staticmethod
    def from_json(json_dict : dict):
        payload = PayloadP2P(json_dict["message"])
        return payload

    def __init__(self, message : str) -> None:
        self.message = message
    
    def to_json(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
    
    def __str__(self)-> str:
        return "PayloadP2P "+str(vars(self))

class DatagramP2P():
    @staticmethod
    def from_json(json_str : str):
        json_dict = json.loads(json_str)
        datagram_p2p = DatagramP2P(
            HeaderP2P.from_json(json_dict["header"]),
            PayloadP2P.from_json(json_dict["payload"])
        )
        return datagram_p2p

    def __init__(self, header : HeaderP2P, payload : PayloadP2P) -> None:
        self.header = header
        self.payload = payload
    
    def to_json(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
    
    def __str__(self)-> str:
        return "DatagramP2P "+str(vars(self))


class ProtocolP2P():
    buffer_size = 1024
    @staticmethod
    def send_datagram(conn : socket.socket, datagram : DatagramP2P) -> None:
        conn.send(datagram.to_json().encode())
    @staticmethod
    def recv_datagram(conn : socket.socket, timeout : float = None) -> DatagramP2P:
        if not timeout:
            conn.setblocking(1)
            datagram_json = conn.recv(ProtocolP2P.buffer_size).decode()
        else:
            conn.setblocking(0)
            ready = select.select([conn], [], [], timeout)
            if ready[0]:
                datagram_json = conn.recv(ProtocolP2P.buffer_size).decode()
            else:
                raise p2p_exceptions.TimedOut('Timed out')
        return DatagramP2P.from_json(datagram_json)
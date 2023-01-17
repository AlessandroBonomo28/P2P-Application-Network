import uuid, json, socket
import netifaces, select
import p2p_exceptions
class HostP2P():
    @staticmethod
    def from_json(json_dict : dict):
        id = str(json_dict["id"])
        name = str(json_dict["name"])
        group = int(json_dict["group"])
        host = HostP2P(id=id,name=name,group=group)
        return host
    
    def __init__(self,id : str = str(uuid.uuid4()), name : str ="Host",
                 group : int=0) -> None:
        self.id = id
        self.name = name
        self. group = group
        
    def to_json(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
    
    def __str__(self)-> str:
        return "Host "+str(vars(self))


class DatagramP2P():
    @staticmethod
    def from_json(json_str : str):
        json_dict = json.loads(json_str)
        if json_dict["host"]!=None:
            host = HostP2P.from_json(json_dict["host"])
        else:
            host = None
        datagram_p2p = DatagramP2P(
            host=host,
            message=json_dict["message"],
            data=json_dict["data"],
            status_code=json_dict["status_code"]
        )
        return datagram_p2p

    def __init__(self, host : HostP2P = None, message : str = None, data : str = None,status_code : int = 0) -> None:
        self.status_code = status_code
        self.host = host
        self.message = message
        self.data = data
    
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
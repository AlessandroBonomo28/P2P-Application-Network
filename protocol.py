import uuid, json
import netifaces
class Host():
    def __get_my_ip(self):
        iface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        ip_addr = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
        return ip_addr
    
    def __init__(self, ip_addr = None, id : str = str(uuid.uuid4()), name : str ="Host",
                 group : int=0, dictionary : dict= None) -> None:
        if dictionary:
            self.id = str(dictionary["id"])
            self.name = str(dictionary["name"])
            self. group = int(dictionary["group"])
            self.ip_addr = str(dictionary["ip_addr"])
            return
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

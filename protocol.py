import uuid, json

class Host():
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
        self.ip_addr = ip_addr
        
    def to_json(self):
        return json.dumps(self, indent = 4, default=lambda o: o.__dict__)
    
    def __str__(self)-> str:
        return "Host "+str(vars(self))

"""for i in range(1,50):
    print(f"{i} users = {(i*(i-1))/2} connections")

exit()"""
from protocol import HostP2P
from p2p_server import HostList
import json

l = HostList()
l.update(HostP2P(id = "1"))
l.update(HostP2P(id ="12"))
l.update(HostP2P(id ="123"))
print("len",len(l.host_list))
for i in l:
    print(i)
    

exit()


host = HostP2P()
json_str= host.to_json()
print("json str ",json_str)


json_dict = json.loads(json_str)
host2 = HostP2P.from_json(json_dict)
print(host2)


auth = HeaderP2P(host2)

json_str = auth.to_json()
print(json_str)
json_dict = json.loads(json_str)
auth2 = HeaderP2P.from_json(json_dict)
print(auth2.host.id)
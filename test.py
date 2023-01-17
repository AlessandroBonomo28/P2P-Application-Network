from protocol import HostP2P, HeaderP2P
import json
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
from protocol import Host
import json
host = Host(ip_addr="192.168.1.1")
json_str= host.to_json()
print("json str ",json_str)

dictionary  = json.loads(json_str)
print("dict",dictionary)

host2 = Host(dictionary=dictionary)
print(host2)
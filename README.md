# python-dubbo-protocol

可耻的dubbo协议

**Tested in Python3.4/3.5**

```
from dubborpc import DubboClient
client = DubboClient(IP, PORT, encoding='gb18030’)
print(client.com.company.api.dubbo.interfaces.db.querySBInfoById(1))
```

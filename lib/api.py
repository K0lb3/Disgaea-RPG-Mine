import re
import requests


class API(requests.Session):
    def __init__(self, host):
        super().__init__()
        self.host = host

    def get(self, path, **kwargs):
        return super().get(f"{self.host}/{path.lstrip('/')}", **kwargs)

    def post(self, path, **kwargs):
        return super().get(f"{self.host}/{path.lstrip('/')}", **kwargs)


base_api = API("https://disgaea-static.boltrend.com/en/live")

server_list = base_api.get("/Server/List.ini").text.split(",")
# default,debug79,debugQA,Build_20201211180117,Build_20201215132158,Build_20201215152655,Build_20201218,ios_20201229132520,ios_20201231141409,1.0.251_ios,2.5.0_ios

default = {
    m[0] : m[1]
    for m in re.findall(r"(.+?)=(.+)",base_api.get("/Server/default.ini").text)
}

asset_api = API(default["asset"])


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


api_url = "https://disgaea-static.boltrend.com/en/live"
base_api = API(api_url)

build_list = [x.split("=") for x in base_api.get("/Server/List.ini").text.split("\n")]
# default,debug79,debugQA,Build_20201211180117,Build_20201215132158,Build_20201215152655,Build_20201218,ios_20201229132520,ios_20201231141409,1.0.251_ios,2.5.0_ios
build_selection = sorted([entry[1] for entry in build_list if len(entry) == 2 and entry[1][:5] == "live_"])[-1]

build_settings = {
    m[0] : m[1]
    for m in re.findall(r"(.+?)=(.+)",base_api.get(f"/Server/{build_selection}.ini").text)
}

asset_api = API(build_settings["asset"].format(cdn = api_url))


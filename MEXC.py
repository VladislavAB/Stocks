import requests
import json


class MEXC:
    def __init__(self):
        self.symbols = []

    def get_symbols(self) -> list:
        url = 'https://api.mexc.com/api/v3/defaultSymbols'
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            self.symbols = load_form_json["data"]
        return self.symbols


pairs = MEXC()
print(pairs.get_symbols())

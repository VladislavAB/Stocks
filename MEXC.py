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

    def get_asks(self):
        self.asks = {}
        prices = []
        url = 'https://api.mexc.com/api/v3/depth?symbol=WOFO1USDT'
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            self.asks = load_form_json["asks"]
            for i in self.asks:
                prices.append(i[0])
        return sorted(prices)

    def get_bids(self):
        self.bids = {}
        prices = []
        url = 'https://api.mexc.com/api/v3/depth?symbol=WOFO1USDT'
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            self.bids = load_form_json["bids"]
            for i in self.bids:
                prices.append(i[0])
        return sorted(prices, reverse=True)

    def get_spread(self):
        self.spread = {}
        asks = self.get_asks()[0]
        bids = self.get_bids()[0]
        self.spread = {'ask': asks, 'bid': bids}
        return self.spread


pairs = MEXC()
print(pairs.get_asks())
print(pairs.get_bids())
print(pairs.get_spread())

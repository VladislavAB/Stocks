import requests
import json


class HTX:
    def __init__(self):
        self.base_url = 'https://api.huobi.pro/market/'
        self.symbols = self.get_symbols()

    def get_symbols(self) -> list:
        symbols = []
        method = 'tickers'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            data = load_form_json["data"]
            for symbol in data:
                symbols.append(symbol['symbol'])
        return symbols

    def check_exist(self, pair: str) -> bool:
        if pair in self.symbols:
            return True
        else:
            print(f'Символа {pair} не сущеуствует!')
            return False

    def get_asks(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            asks = []
            method = "depth"
            url = self.base_url + method + "?symbol=" + pair + "&depth=&type=step0"
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                asks = load_form_json['tick']['asks']
            return asks
        return False

    def get_bids(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            bids = []
            method = "depth"
            url = self.base_url + method + "?symbol=" + pair + "&depth=&type=step0"
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                bids = load_form_json['tick']['bids']
            return bids
        return False

    #
    def get_spread(self, pair: str) -> dict:
        asks = self.get_asks(pair)
        bids = self.get_bids(pair)
        spread = {'ask': asks[0], 'bid': bids[0]}
        return spread


#     def get_commission(self, pair: str) -> dict:
#         commission = {}
#         method = "exchangeInfo"
#         url = self.base_url + method + "?symbol=" + pair
#         mexc_api_respond = requests.get(url)
#         if mexc_api_respond:
#             load_form_json = json.loads(mexc_api_respond.text)
#             maker_commission = load_form_json["symbols"][0]["makerCommission"]
#             taker_commission = load_form_json["symbols"][0]["takerCommission"]
#             commission = {'maker': maker_commission, 'taker': taker_commission}
#         return commission
#
#
stock = HTX()
print(stock.get_symbols())
print(stock.check_exist('sylousdt'))
print(stock.get_asks("sylousdt"))
print(stock.get_bids("sylousdt"))
print(stock.get_spread("sylousdt"))
# print(stock.get_commission("sylousdt"))

import requests
import json


class OKX:
    def __init__(self):
        self.base_url = 'https://www.okx.com/api/v5/market/'
        self.symbols = self.get_symbols()

    def get_symbols(self) -> list:
        symbols = []
        method = 'tickers?instType=SPOT'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            data = load_form_json["data"]
            for symbol in data:
                symbols.append(symbol['instId'])
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
            method = "books"
            url = self.base_url + method + "?instId=" + pair + '&sz=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                asks = load_form_json["data"][0]['asks']
            return asks
        return False

    def get_bids(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            bids = []
            method = "books"
            url = self.base_url + method + "?instId=" + pair + '&sz=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                bids = load_form_json["data"][0]['bids']
            return bids
        return False

    def get_spread(self, pair: str) -> dict:
        asks = self.get_asks(pair)
        bids = self.get_bids(pair)
        spread = {'ask': asks[0][:2], 'bid': bids[0][:2]}
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
stock = OKX()
print(stock.get_symbols())
print(stock.check_exist("MDT-USDT"))
print(stock.get_asks("MDT-USDT"))
print(stock.get_bids("MDT-USDT"))
print(stock.get_spread("MDT-USDT"))
# print(stock.get_commission("MDT-USDT"))

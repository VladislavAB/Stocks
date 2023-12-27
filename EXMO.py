import requests
import json


class EXMO:
    def __init__(self):
        self.base_url = 'https://api.exmo.me/v1.1/'
        self.symbols = self.get_symbols()

    #
    def get_symbols(self) -> list:
        symbols = []
        method = 'ticker'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            symbols = list(load_form_json.keys())
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
            method = "order_book"
            url = self.base_url + method + "?pair=" + pair + '&limit=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                asks = load_form_json[pair]['ask']
            return asks
        return False

    def get_bids(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            bids = []
            method = "order_book"
            url = self.base_url + method + "?pair=" + pair + '&limit=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                bids = load_form_json[pair]['bid']
            return bids
        return False

    def get_spread(self, pair: str) -> dict:
        asks = self.get_asks(pair)
        bids = self.get_bids(pair)
        spread = {'ask': asks[0], 'bid': bids[0]}
        return spread

    def get_commission(self, pair: str) -> dict:
        commission = {}
        method = "pair_settings"
        url = self.base_url + method
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            maker_commission = load_form_json[pair]["commission_maker_percent"]
            taker_commission = load_form_json[pair]["commission_taker_percent"]
            commission = {'maker': maker_commission, 'taker': taker_commission}
        return commission


stock = EXMO()
print(stock.symbols)
print(stock.check_exist("ADA_BTC"))
print(stock.get_asks("ADA_BTC"))
print(stock.get_bids("ADA_BTC"))
print(stock.get_spread("ADA_BTC"))
print(stock.get_commission("ADA_BTC"))

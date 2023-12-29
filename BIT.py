import requests
import json


class BIT:
    def __init__(self):
        self.base_url = 'https://api.bit.com/spot/v1/'
        self.symbols = self.get_symbols()

    def get_symbols(self) -> list:
        symbols = []
        method = 'instruments'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            for symbol in load_form_json["data"]:
                symbols.append(symbol['pair'])
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
            method = "orderbooks"
            url = self.base_url + method + "?pair=" + pair + '&level=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                asks = load_form_json["data"]['asks']
            return asks
        return False

    def get_bids(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            bids = []
            method = "orderbooks"
            url = self.base_url + method + "?pair=" + pair + '&level=10'
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                bids = load_form_json["data"]["bids"]
            return bids
        return False

    def get_spread(self, pair: str) -> dict:
        asks = self.get_asks(pair)
        bids = self.get_bids(pair)
        spread = {'ask': asks[0], 'bid': bids[0]}
        return spread

    def get_commission(self, pair: str) -> dict:
        commission = {}
        method = "instruments"
        url = self.base_url + method
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            for i in load_form_json['data']:
                if i['pair'] == pair:
                    maker_commission = load_form_json['data'][0]["maker_fee_rate"]
                    taker_commission = load_form_json['data'][0]["taker_fee_rate"]
                    commission = {'maker': maker_commission, 'taker': taker_commission}
        return commission

    def get_spread_w_commission(self, pair):
        precision = 10
        spread = self.get_spread(pair)
        commission = self.get_commission(pair)
        commission_ask = round(float(spread['ask'][0]) * float(commission['taker']), precision)
        commission_bid = round(float(spread['bid'][0]) * float(commission['taker']), precision)
        spread_w_commission = {'ask': round(float(spread['ask'][0]) + commission_ask, precision),
                               'bid': round(float(spread['bid'][0]) - commission_bid, precision)}
        return spread_w_commission


stock = BIT()
print(stock.get_spread("AAVE-USDT"))
print(stock.get_commission("AAVE-USDT"))
print(stock.get_spread_w_commission("AAVE-USDT"))

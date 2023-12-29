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

    def get_precision(self, pair) -> dict:
        precision = None
        method = "pair_settings"
        url = self.base_url + method
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            precision = load_form_json[pair]["price_precision"]
        return {"precision_inst": precision,
                "precision_commission": precision}

    def get_spread_w_commission(self, pair):
        precision = self.get_precision(pair)
        spread = self.get_spread(pair)
        commission = self.get_commission(pair)
        commission_ask = round(float(spread['ask'][0]) * float(commission['taker']), precision['precision_commission'])
        commission_bid = round(float(spread['bid'][0]) * float(commission['taker']), precision['precision_commission'])
        spread_w_commission = {'ask': round(float(spread['ask'][0]) + commission_ask, precision['precision_inst']),
                               'bid': round(float(spread['bid'][0]) - commission_bid, precision['precision_inst'])}
        return spread_w_commission


stock = EXMO()
print(stock.get_spread("ADA_BTC"))
print(stock.get_commission("ADA_BTC"))
print(stock.get_spread_w_commission("ADA_BTC")["ask"])

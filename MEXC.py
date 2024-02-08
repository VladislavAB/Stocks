import requests
import json
import pandas as pd


class MEXC:
    def __init__(self):
        self.base_url = 'https://api.mexc.com/api/v3/'
        self.symbols = self.get_symbols()
        self.exchange_info = self.get_exchange_info()

    def get_symbols(self) -> list:
        symbols = []
        method = 'defaultSymbols'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        if mexc_api_respond:
            load_form_json = json.loads(mexc_api_respond.text)
            symbols = load_form_json["data"]
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
            url = self.base_url + method + "?symbol=" + pair
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                asks = load_form_json["asks"]
            return asks
        return False

    def get_bids(self, pair: str) -> list or bool:
        if self.check_exist(pair):
            bids = []
            method = "depth"
            url = self.base_url + method + "?symbol=" + pair
            mexc_api_respond = requests.get(url)
            if mexc_api_respond:
                load_form_json = json.loads(mexc_api_respond.text)
                bids = load_form_json["bids"]
            return bids
        return False

    def get_spread(self, pair: str) -> dict:
        asks = self.get_asks(pair)
        bids = self.get_bids(pair)
        spread = {'ask': asks[0], 'bid': bids[0]}
        return spread

    def get_commission(self, pair: str) -> dict:
        commission = {}
        method = "exchangeInfo"
        url = self.base_url + method + "?symbol=" + pair
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            maker_commission = load_form_json["symbols"][0]["makerCommission"]
            taker_commission = load_form_json["symbols"][0]["takerCommission"]
            commission = {'maker': maker_commission, 'taker': taker_commission}
        return commission

    def get_precision(self, pair):
        precision = None
        method = "exchangeInfo"
        url = self.base_url + method + "?symbol=" + pair
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            precision = {"quotePrecision": load_form_json["symbols"][0]["quotePrecision"],
                         "quoteCommissionPrecision": load_form_json["symbols"][0]["quoteCommissionPrecision"]}
        return precision

    def get_spread_w_commission(self, pair):
        precision = self.get_precision(pair)
        spread = self.get_spread(pair)
        commission = self.get_commission(pair)
        if commission:
            commission_ask = round(float(spread['ask'][0]) * float(commission['taker']),
                                   precision["quoteCommissionPrecision"])
            commission_bid = round(float(spread['bid'][0]) * float(commission['taker']),
                                   precision["quoteCommissionPrecision"])
            spread_w_commission = {'ask': round(float(spread['ask'][0]) + commission_ask, precision["quotePrecision"]),
                                   'bid': round(float(spread['bid'][0]) - commission_bid, precision["quotePrecision"])}
            return spread_w_commission
        return spread

    def get_exchange_info(self) -> pd.DataFrame:
        method = 'exchangeInfo'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        exchange_info = ''
        df = None
        if mexc_api_respond:
            exchange_info = json.loads(mexc_api_respond.text)["symbols"]
            df = pd.DataFrame(exchange_info)
            df['gen_name'] = df['symbol']
            df = df.rename(columns={'symbol': 'original_name'})
            cols = df.columns
            cols = cols.delete(list(cols).index('gen_name'))
            cols = cols.insert(0, 'gen_name')
            df = df[cols]
        return df

stock = MEXC()
# print(f'SPREAD: {stock.get_spread("WOFO1USDT")}')
# print(f'COMMISSION: {stock.get_commission("WOFO1USDT")}')
# print(f'PRECISION: {stock.get_precision("WOFO1USDT")}')
# print(f'SPREAD W COMMISSION: {stock.get_spread_w_commission("WOFO1USDT")}')
print(stock.get_exchange_info())
stock.exchange_info.to_csv('out/list-MEXC.csv', sep='|', encoding='utf-8', index=False)



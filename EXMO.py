import pandas as pd
import requests
import json
from pprint import pprint


class EXMO:
    def __init__(self):
        self.base_url = 'https://api.exmo.me/v1.1/'
        self.symbols = self.get_symbols()
        self.exchange_info = self.get_exchange_info()  # return dataframe

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

    def get_pairs(self):
        pairs = None
        method = "pair_settings"
        url = self.base_url + method
        api_respond = requests.get(url)
        if api_respond:
            load_form_json = json.loads(api_respond.text)
            pairs = list(load_form_json.keys())
        return pairs

    def get_prices(self):
        prices = []
        pairs = self.get_pairs()
        for pair in pairs:
            print(pair)
            best_ask = self.get_asks(pair)[0]
            best_bid = self.get_bids(pair)[0]
            prices.append({'original_name': pair, 'best_ask': best_ask[0], 'quantity_ask': best_ask[1],
                           'best_bid': best_bid[0], 'quantity_bid': best_bid[1]})
        prices = pd.DataFrame(prices)
        return prices

    def get_exchange_info(self) -> pd.DataFrame:
        method = 'pair_settings'
        url = self.base_url + method
        mexc_api_respond = requests.get(url)
        exchange_info = ''
        if mexc_api_respond:
            exchange_info = json.loads(mexc_api_respond.text)
            for pair in exchange_info.keys():
                exchange_info[pair]['gen_name'] = pair.replace('_', '')
        df = pd.DataFrame(exchange_info)
        df = df.T
        df['original_name'] = df.index
        cols = df.columns
        cols = cols.delete(list(cols).index('gen_name'))
        cols = cols.delete(list(cols).index('original_name'))
        cols = cols.insert(0, 'original_name')
        cols = cols.insert(0, 'gen_name')
        df = df[cols]
        return df

    def get_currencies(self) -> pd.DataFrame:
        result = []
        url = 'https://api.exmo.me/v1.1/payments/providers/crypto/list'
        api_response = requests.get(url)
        if api_response:
            response = json.loads(api_response.text)
            for coin_info in response.values():
                for coin in coin_info:
                    currency_name = None
                    name = None
                    comment = None
                    if 'currency_name' in coin.keys():
                        currency_name = coin['currency_name']
                    if 'name' in coin.keys():
                        name = coin['name']
                    if 'comment' in coin.keys():
                        comment = coin['comment']
                    if 'withdraw' in coin.values():
                        withdraw = coin['enabled']
                    else:
                        if 'deposit' in coin.values():
                            deposit = coin['enabled']
                            result.append(
                                {'currency_name': currency_name, 'name': name, 'withdraw': withdraw,
                                 'deposit': deposit, 'comment': comment})
        df_result = pd.DataFrame(result)
        df_result["blockchain"] = df_result["comment"].apply(stock.display_blockchain)
        return df_result

    @staticmethod
    def remove_in_brackets(string):
        first_bracket_index, last_bracket_index = None, None
        result = string
        finished = False

        while not finished:
            for index, symbol in enumerate(result):
                if symbol == '(':
                    first_bracket_index = index
                if symbol == ')':
                    last_bracket_index = index
                # print(f"{index}, {symbol} {first_bracket_index} {last_bracket_index}")
                if first_bracket_index and last_bracket_index:
                    result = result[:first_bracket_index - 1] + result[last_bracket_index + 1:]
                    first_bracket_index, last_bracket_index = None, None
                    break
            if index == (len(result) - 1):
                finished = True
        return result

    @staticmethod
    def display_blockchain(string):
        result = []
        string = stock.remove_in_brackets(string)
        string = string.replace('.', '')
        string = string.replace(',', '')
        words = string.split()
        if 'network' in words:
            for index, word in enumerate(words):
                if word == 'network':
                    network_index = index
                    words = words[:network_index]
                    words = words[::-1]
                    break
        else:
            return None
        for word in words:
            if stock.have_capital(word):
                result.append(word)
            else:
                break
        result = ' '.join(result)
        return result

    @staticmethod
    def have_capital(word):
        for letter in word:
            if letter.isupper():
                return True


# string = 'We support only Ethereum (ERC-20) network for PRQ deposits, please consider this when transferring funds'

stock = EXMO()
# df_info = stock.get_exchange_info()
# df_prices = stock.get_prices()
# df_final = df_prices.merge(df_info, on='original_name', how='left')
# gen = df_final['gen_name']
# df_final = df_final.drop('gen_name', axis=1)
# df_final.insert(0, 'gen_name', gen)
# df_final.to_csv('out/EXMO-spread.csv', encoding='utf-8', na_rep='None', sep='|', index=False)
stock.get_currencies().to_csv('out/EXMO-currency.csv', encoding='utf-8', na_rep='None', sep='|', index=False)
pprint(stock.get_currencies())

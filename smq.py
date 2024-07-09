import sys
from pathlib import Path
sys.path.append(str(Path('').resolve()))

from SETTINGS.settings__ import info_smq
from pybit.unified_trading import HTTP
import time
from decimal import Decimal as D
from datetime import datetime
import glob
from os.path import basename
from pprint import pprint

session = HTTP()

def fetch_data():
    data = session.get_tickers(category='linear')['result']['list']
    print(f'{datetime.now()}: Получил новые данные')
    return data

def validate(data_new, prices_old):
    for price_new in data_new:
        symbol = price_new['symbol'] if 'USDT' in price_new['symbol'] else None
        if symbol in prices_old:
            percent_change = round(((D(price_new['lastPrice']) - prices_old[symbol]) / prices_old[symbol]) * 100, 2)
            if abs(percent_change) >= D(info_smq['PROCENT']) and abs(percent_change) < D(info_smq['PROCENT_LIMIT']):
                with open(str(Path('').resolve().parent) + '\\SMQ_N\\signal.txt', 'w', encoding='utf-8') as f:
                    if percent_change < 0:
                        side = 'Buy'
                        f.write(f'🔴Ticker: {symbol}\n'
                                f'Percent: {percent_change}%\n'
                                f'Datetime: {datetime.now()}')
                    if percent_change > 0:
                        side = 'Sell'
                        f.write(f'🟢Ticker: {symbol}\n'
                                f'Percent: {percent_change}%\n'
                                f'Datetime: {datetime.now()}')
                return symbol, side, percent_change
            else:
                None

def smq(prices_old):
    time.sleep(0.5)
    print(f'Check data. Time: {datetime.now()}')
    data_new = session.get_tickers(category='linear')['result']['list']
    signal = validate(data_new=data_new, prices_old=prices_old)
    if signal != None:
        return signal

if __name__ == '__main__':
    data_old = fetch_data()
    prices_old = {price['symbol']: D(price['lastPrice']) for price in data_old}
    start_time = time.time()
    while True:
        if time.time() - start_time >= 60:
            data_old = fetch_data()
            prices_old = {price['symbol']: D(price['lastPrice']) for price in data_old}
            start_time = time.time()
        signal = smq(prices_old=prices_old)
        if signal != None:
            pprint(signal)

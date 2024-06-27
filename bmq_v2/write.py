import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bmq_v2.keys import session
from bmq_v2.read import get_roundQty
from datetime import datetime
from decimal import Decimal as D
import traceback

'''ORDERS ↓
'''
def cancel_position():
    position = session.get_positions(category='linear', settleCoin='USDT')['result']['list'][-1]
    side = 'Buy' if position['side'] == 'Sell' else 'Sell'
    session.place_order(category='linear',
                        symbol=position['symbol'],
                        side=side,
                        orderType='Market',
                        qty=position['size'],
                        reduceOnly=True)

def orders_clear(orders_tp):
    if not orders_tp:
        session.cancel_all_orders(category="linear", settleCoin='USDT')

def place_order_limit(symbol, side, qty, price, i=None):
    try:
        session.place_order(
            category='linear', symbol=symbol,
            qty=qty, marketUnit='baseCoin',
            side=side,
            orderType='Limit', price=price,
            isLeverage=10,
            tpTriggerBy='LastPrice', slTriggerBy='LastPrice'
        )
    except:
        cancel_position()
        er = traceback.format_exc()
        with open('/CODE_PROJECTS/SMQ-N & Python/signal.txt', 'w', encoding='utf-8') as f:
            f.write(f'Ошибка в выставлении {i} лимитного ордера: \n{er}\n Время: {datetime.now()}')

def place_orders_limit(symbol, side, qty, round_qty, percent_price):
    avg_position_price = D(session.get_positions(category='linear', settleCoin='USDT')['result']['list'][-1]['avgPrice'])
    radius_price = avg_position_price * percent_price
    for i in range(1, 5):
        price = round(avg_position_price + (radius_price * (i if side == 'Sell' else -i)), round_qty[0])
        place_order_limit(symbol=symbol, side=side, qty=qty, price=price, i=i+1)

'''POSITION ↓
'''
def place_order(symbol, side, qty):
    try:
        session.place_order(
            category='linear',
            symbol=symbol,
            qty=qty, marketUnit='baseCoin',
            side=side,
            orderType='Market',
            isLeverage=10,
            tpTriggerBy='LastPrice', slTriggerBy='LastPrice'
        )
    except:
        er = traceback.format_exc()
        with open('/CODE_PROJECTS/SMQ-N & Python/signal.txt', 'w', encoding='utf-8') as f:
            f.write(f'Ошибка в Place Order: \nВремя: {datetime.now()}\n{er}')

def TP(position, orders_limit_num, tp):
    symbol = position['symbol']        
    side = position['side']
    avg_price = D(position['avgPrice'])
    round_qty = get_roundQty(symbol)
    tp_position = position['takeProfit'].rstrip('0')
    tp_price = str(round(avg_price + ((avg_price * tp[-(orders_limit_num + 1)] * (-1 if side == 'Sell' else 1))), round_qty[0])).rstrip('0')
    print(tp_price, tp_position, tp_position == tp_price)
    if tp_position != tp_price:
        if tp_position != tp_price:
            try:
                session.set_trading_stop(category='linear', symbol=symbol, tpslMode='Full', takeProfit=tp_price, positionIdx=0)
            except:
                with open('/CODE_PROJECTS/SMQ-N & Python/signal.txt', 'w', encoding='utf-8') as f:
                    f.write(f'Ошибка в TP: \nВремя: {datetime.now()}\nДанные: TPPOS: {tp_position}, TPPR: {tp_price}\n{traceback.format_exc()}')
                cancel_position()

def SL(position, orders_limit, sl):
    symbol = position['symbol']
    side = position['side']
    avg_price = D(session.get_positions(category='linear', settleCoin='USDT')['result']['list'][-1]['avgPrice'])
    round_qty = get_roundQty(symbol)
    sl_position_price = position['stopLoss'].rstrip('0')
    sl_price = str(round(avg_price + ((avg_price * sl * (1 if side == 'Sell' else -1))), round_qty[0])).rstrip('0')
    if sl_position_price != sl_price and not orders_limit:
        try:
            session.set_trading_stop(category='linear', symbol=symbol, tpslMode='Full', stopLoss=sl_price, positionIdx=0)
        except:
            with open('/CODE_PROJECTS/SMQ-N & Python/signal.txt', 'w', encoding='utf-8') as f:
                f.write(f'Ошибка в TP: \nВремя: {datetime.now()}\nДанные: SLPOS: {sl_position_price}, SLPR: {sl_price}\n{traceback.format_exc()}')
            cancel_position()

'''MORE ↓
'''
def switch_margin_mode(symbol):
    try:
        session.switch_margin_mode(
            category="linear", symbol=symbol,
            tradeMode=1,
            buyLeverage="10", sellLeverage="10",
        )
    except:
        pass
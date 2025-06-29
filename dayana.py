import time
import random
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from binance.client import Client
from binance.enums import (
    ORDER_TYPE_MARKET,
    SIDE_BUY,
    SIDE_SELL
)
from config import (
    API_KEY, API_SECRET, TRADE_AMOUNT, TP_PCT, SL_PCT, LEVERAGE,
    SYMBOLS, DEFAULT_INTERVAL, CHECK_INTERVAL_SECONDS,
    ENABLE_LONG, ENABLE_SHORT, MAX_OPEN_TRADES, BOT_NAME
)
from strategies import check_all_strategies
from data_fetch import get_klines
from logger import log_trade
from decimal import Decimal, ROUND_DOWN
import json
from zoneinfo import ZoneInfo

last_trade_time = None
TRADE_COOLDOWN_SECONDS = 1267  # минут

client = Client(API_KEY, API_SECRET)
active_trades = {}

def get_quantity(symbol, price):
    try:
        info = client.futures_exchange_info()
    except Exception as e:
        print(f"❌ Ошибка получения информации биржи: {e}")
        return None, None
    
    for s in info['symbols']:
        if s['symbol'] == symbol:
            filters = {f['filterType']: f for f in s['filters']}
            min_qty = float(filters['LOT_SIZE']['minQty'])
            step_size = float(filters['LOT_SIZE']['stepSize'])

            raw_qty = TRADE_AMOUNT / price
            step = Decimal(str(step_size))
            qty = Decimal(str(raw_qty)).quantize(step, rounding=ROUND_DOWN)

            if qty < Decimal(str(min_qty)):
                print(f"⚠️ {symbol}: qty {qty} < minQty {min_qty}")
                return None, None

            return float(qty), step
    return None, None

def get_open_symbols():
    return set(get_open_positions().keys())

def get_open_positions():
    try:
        positions = client.futures_position_information()
        result = {}
        for p in positions:
            amt = float(p.get('positionAmt', 0))
            if amt != 0.0:
                result[p['symbol']] = {
                    'side': 'BUY' if amt > 0 else 'SELL',
                    'qty': abs(amt),
                    'entry_price': float(p.get('entryPrice', 0))
                }
        return result
    except Exception as e:
        print(f"❌ Ошибка получения открытых позиций: {e}")
        return {}

def place_order(symbol, side, entry_price, strategy, indicators):
    try:
        info = client.futures_exchange_info()
        sym = next(s for s in info['symbols'] if s['symbol'] == symbol)
        filters = {f['filterType']: f for f in sym['filters']}

        min_qty   = Decimal(filters['LOT_SIZE']['minQty'])
        step_qty  = Decimal(filters['LOT_SIZE']['stepSize'])
        raw_qty   = Decimal(str(TRADE_AMOUNT)) / Decimal(str(entry_price))
        qty       = raw_qty.quantize(step_qty, rounding=ROUND_DOWN)
        if qty < min_qty:
            print(f"⚠️ {symbol}: qty {qty} < minQty {min_qty}")
            return
        quantity_str = str(qty)

        tick = Decimal(filters['PRICE_FILTER']['tickSize'])
        ep = Decimal(str(entry_price))

        tp_pct = Decimal(str(indicators.get('tp_pct', TP_PCT)))
        sl_pct = Decimal(str(indicators.get('sl_pct', SL_PCT)))

        if side == 'BUY':
            tp_price = ep * (Decimal('1') + tp_pct)
            sl_price = ep * (Decimal('1') - sl_pct)
        else:
            tp_price = ep * (Decimal('1') - tp_pct)
            sl_price = ep * (Decimal('1') + sl_pct)

        tp_str = str(tp_price.quantize(tick, rounding=ROUND_DOWN))
        sl_str = str(sl_price.quantize(tick, rounding=ROUND_DOWN))

        print(f"📊 DEBUG: {symbol}")
        print(f"  quantity    = {quantity_str}")
        print(f"  tp_str      = {tp_str}")
        print(f"  sl_str      = {sl_str}")

        client.futures_change_leverage(symbol=symbol, leverage=LEVERAGE)
        client.futures_cancel_all_open_orders(symbol=symbol)

        client.futures_create_order(
            symbol=symbol,
            side=SIDE_BUY if side=='BUY' else SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=quantity_str
        )

        # 🕒 Подождать немного, чтобы позиция успела открыться
        time.sleep(1.5)

        client.futures_create_order(
            symbol=symbol,
            side=SIDE_SELL if side=='BUY' else SIDE_BUY,
            type='STOP_MARKET',
            stopPrice=sl_str,
            closePosition=True,
            timeInForce='GTE_GTC'
        )
        client.futures_create_order(
            symbol=symbol,
            side=SIDE_SELL if side=='BUY' else SIDE_BUY,
            type='TAKE_PROFIT_MARKET',
            stopPrice=tp_str,
            closePosition=True,
            timeInForce='GTE_GTC'
        )

        active_trades[symbol] = {
            "side":        side,
            "entry_price": float(ep),
            "qty":         float(qty),
            "tp":          float(tp_price),
            "sl":          float(sl_price),
            "strategy":    strategy,
            "indicators":  indicators,
            "time":        datetime.now(timezone.utc).isoformat()
        }
        log_trade(symbol, side, float(ep), float(qty), float(tp_price), float(sl_price), strategy, indicators, is_exit=False)
        print(f"✅ Opened {side} {symbol} @ {entry_price} (TP: {tp_price}, SL: {sl_price})")

    except Exception as e:
        import traceback
        print(f"❌ Ошибка при открытии позиции по {symbol}: {e}")
        traceback.print_exc()
        try:
            client.futures_cancel_all_open_orders(symbol=symbol)
        except:
            pass

def check_exit():
    open_positions = get_open_positions()
    for symbol in list(active_trades):
        if symbol not in open_positions:
            trade = active_trades[symbol]
            try:
                mark_price = float(client.futures_mark_price(symbol=symbol)['markPrice'])
            except Exception as e:
                print(f"❌ Ошибка получения цены {symbol}: {e}")
                continue
            trade['exit_price'] = mark_price
            trade['exit_reason'] = "manual_or_tp_sl"
            entry = Decimal(str(trade['entry_price']))
            exit_ = Decimal(str(trade['exit_price']))
            qty = Decimal(str(trade['qty']))

            side_mult = Decimal('1') if trade['side'] == 'BUY' else Decimal('-1')
            pnl_dec = (exit_ - entry) * qty * side_mult
            pnl = float(pnl_dec.quantize(Decimal('0.01')))
            trade['pnl'] = pnl

            log_trade(
                symbol,
                trade['side'],
                trade['entry_price'],
                trade['qty'],
                trade['tp'],
                trade['sl'],
                trade['strategy'],
                {
                    **trade['indicators'],
                    "exit_price": trade['exit_price'],
                    "exit_reason": trade['exit_reason'],
                    "pnl": pnl,
                    "timestamp_exit": datetime.now(timezone.utc).isoformat()
                },
                is_exit=True
            )

            try:
                client.futures_cancel_all_open_orders(symbol=symbol)
            except:
                pass

            print(f"✅ {symbol} закрыта вручную или TP/SL. Прибыль: {pnl:.2f} USDT")
            del active_trades[symbol]

def main():
    global last_trade_time
    print(f"\n🚀 Привет! Я — {BOT_NAME}")
    print("🔍 Анализирую рынок...\n")

    # инициализация активных сделок из Binance
    active_trades.clear()
    existing = get_open_positions()
    for sym, data in existing.items():
        active_trades[sym] = {
            "side": data['side'],
            "entry_price": data['entry_price'],
            "qty": data['qty'],
            "tp": None,
            "sl": None,
            "strategy": "from_api",
            "indicators": {},
            "time": datetime.now(timezone.utc).isoformat()
        }
    if active_trades:
        print(f"🔄 Найдено открытых позиций: {len(active_trades)}")

    while True:
        open_symbols = set(get_open_positions().keys())
        for symbol in list(active_trades):
            if symbol not in open_symbols:
                print(f"⚠️ Позиция {symbol} закрыта вручную — очищаем")
                try:
                    client.futures_cancel_all_open_orders(symbol=symbol)
                except:
                    pass
                del active_trades[symbol]

        if len(active_trades) >= MAX_OPEN_TRADES:
            print(f"⚠️ Достигнут лимит сделок ({MAX_OPEN_TRADES})")

        open_positions = get_open_positions()
        for symbol in random.sample(SYMBOLS, len(SYMBOLS)):
            if symbol in active_trades:
                continue

            if len(open_positions) >= MAX_OPEN_TRADES:
                break

            if len(active_trades) >= MAX_OPEN_TRADES:
                break

            try:

                now = datetime.now(timezone.utc)
                if last_trade_time and (now - last_trade_time).total_seconds() < TRADE_COOLDOWN_SECONDS:
                    print(f"⏳ Кулдаун: прошло меньше {TRADE_COOLDOWN_SECONDS} секунд после последней сделки")
                    continue

                df = get_klines(symbol, interval=DEFAULT_INTERVAL, limit=350)
                print(f"\n📈 Монета: {symbol}")
                print("─" * 25)

                

                entry = check_all_strategies(symbol, df)
                if entry:
                    side = entry['side']
                    if (side == 'BUY' and not ENABLE_LONG) or (side == 'SELL' and not ENABLE_SHORT):
                        print(f"🚫 {side} сигналы отключены — пропускаем {symbol}")
                        continue
                    strategy = entry['strategy']
                    price = float(client.futures_mark_price(symbol=symbol)['markPrice'])
                    indicators = df.iloc[-1].to_dict()
                    place_order(symbol, side, price, strategy, indicators)
                    last_trade_time = datetime.now(timezone.utc)
            except Exception as e:
                print(f"❌ Ошибка по {symbol}: {e}")

        check_exit()
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()

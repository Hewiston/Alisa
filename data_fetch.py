# data_fetch.py — загрузка свечей + индикаторы

import pandas as pd
from binance.client import Client
from config import API_KEY, API_SECRET
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from datetime import timezone

client = Client(API_KEY, API_SECRET)

def get_klines(symbol, interval='5m', limit=350):
    raw = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(raw, columns=[
        'timestamp','open','high','low','close','volume','close_time',
        'quote_asset_volume','num_trades','taker_buy_base_volume',
        'taker_buy_quote_volume','ignore'])
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    df = compute_indicators(df)

    # Удаляем строки с NaN — особенно важно для ema_200, boll_width_ma и т.п.
    df = df[df['ema_200'].notna()].reset_index(drop=True)

     # Возвращаем None, если данных недостаточно
    if len(df) < 3:
        return None
    
    return df

def compute_indicators(df):
    df['ema_9'] = EMAIndicator(df['close'], 9).ema_indicator()
    df['ema_14'] = EMAIndicator(df['close'], 14).ema_indicator()
    df['ema_21'] = EMAIndicator(df['close'], 21).ema_indicator()
    df['ema_50'] = EMAIndicator(df['close'], 50).ema_indicator()
    df['ema_200'] = EMAIndicator(df['close'], 200).ema_indicator()

    df['rsi'] = RSIIndicator(df['close'], 14).rsi()
    macd = MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macdsignal'] = macd.macd_signal()  # уже есть как 'macd_signal', значит rename
    df['macd_hist'] = macd.macd_diff()
 

    adx = ADXIndicator(df['high'], df['low'], df['close'], 14)
    df['adx'] = adx.adx()
    df['adx_pos'] = adx.adx_pos()
    df['adx_neg'] = adx.adx_neg()

    stoch = StochasticOscillator(df['high'], df['low'], df['close'], 14, 3)
    df['stoch_k'] = stoch.stoch()
    df['stoch_d'] = stoch.stoch_signal()

    df['obv'] = OnBalanceVolumeIndicator(df['close'], df['volume']).on_balance_volume()

    df['vwap'] = (df['high'] + df['low'] + df['close']) / 3

    bb = BollingerBands(df['close'], 20, 2)
    df['boll_upper'] = bb.bollinger_hband()
    df['boll_lower'] = bb.bollinger_lband()
    df['boll_width'] = df['boll_upper'] - df['boll_lower']
    df['boll_width_ma'] = df['boll_width'].rolling(window=20).mean()

    df['atr'] = AverageTrueRange(df['high'], df['low'], df['close'], 14).average_true_range()

    df['volume_ma'] = df['volume'].rolling(window=10, min_periods=5).mean()
    return df

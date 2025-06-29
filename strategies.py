# strategies.py — 14 независимых стратегий LONG и SHORT
from config import ENABLED_STRATEGIES
from datetime import datetime, timedelta
from datetime import timezone
import random


strategy_cooldowns = {}
STRATEGY_COOLDOWN_MINUTES = 120 


def format_strategy(name, side, passed, total, conditions, tp_pct=None, sl_pct=None):
    return {
        "strategy": name,
        "side": side,
        "passed": passed,
        "total": total,
        "conditions": conditions,
        "success": passed == total,
        "tp_pct": tp_pct,
        "sl_pct": sl_pct
    }

# Все стратегии


def strategy_panic_wick_reversal(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("Нижняя тень > 1%", (latest['close'] - latest['low']) / latest['close'] > 0.01),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("RSI < 35", latest['rsi'] < 35),
        ("Объём > MA * 1.5", latest['volume'] > latest['volume_ma'] * 1.5),
        ("Предыдущая свеча красная", prev['close'] < prev['open']),
        ("Закрытие выше нижней BB", latest['close'] > latest['boll_lower']),
        ("Цена > EMA50", latest['close'] > latest['ema_50'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("panic_wick_reversal", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_volume_cliff_bounce(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("Предыдущая свеча красная + объёмная", prev['close'] < prev['open'] and prev['volume'] > df['volume_ma'].iloc[-2] * 1.5),
        ("Текущая свеча зелёная", latest['close'] > latest['open']),
        ("RSI растёт и > 35", latest['rsi'] > prev['rsi'] and latest['rsi'] > 35),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist']),
        ("Закрытие выше нижней BB", latest['close'] > latest['boll_lower']),
        ("Цена > EMA50", latest['close'] > latest['ema_50']),
        ("Объём > предыдущего", latest['volume'] > prev['volume'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("volume_cliff_bounce", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_flash_crash_recover(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    body = abs(latest['close'] - latest['open'])
    wick = latest['high'] - latest['low']

    conditions = [
        ("Нижняя тень > 2%", (latest['close'] - latest['low']) / latest['close'] > 0.02),
        ("Свеча молот (тело < 30% от всей свечи)", body < wick * 0.3),
        ("RSI < 35", latest['rsi'] < 35),
        ("Объём > MA * 2", latest['volume'] > latest['volume_ma'] * 2),
        ("Закрытие выше нижней BB", latest['close'] > latest['boll_lower']),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist']),
        ("Цена > EMA200", latest['close'] > latest['ema_200'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("flash_crash_recover", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_oversold_rsi_explosion(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("RSI < 25 на предыдущей свече", prev['rsi'] < 25),
        ("RSI резко вырос > 5 пунктов и > 30", latest['rsi'] > prev['rsi'] + 5 and latest['rsi'] > 30),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("Объём > MA * 1.8", latest['volume'] > latest['volume_ma'] * 1.8),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist']),
        ("Закрытие выше нижней BB", latest['close'] > latest['boll_lower']),
        ("Цена > EMA50", latest['close'] > latest['ema_50'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("oversold_rsi_explosion", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_bb_lower_squeeze_pop(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("Предыдущая свеча закрылась ниже BB lower", prev['close'] < prev['boll_lower']),
        ("Текущая свеча закрылась выше BB lower", latest['close'] > latest['boll_lower']),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("RSI растёт и > 35", latest['rsi'] > prev['rsi'] and latest['rsi'] > 35),
        ("Bollinger ширина < MA", latest['boll_width'] < latest['boll_width_ma']),
        ("Объём > MA * 1.5", latest['volume'] > latest['volume_ma'] * 1.5),
        ("Цена > EMA50", latest['close'] > latest['ema_50'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("bb_lower_squeeze_pop", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_trend_pullback_ema50(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("EMA50 > EMA200", latest['ema_50'] > latest['ema_200']),
        ("Цена у EMA50", abs(latest['close'] - latest['ema_50']) / latest['close'] < 0.005),
        ("RSI > 45", latest['rsi'] > 45),
        ("RSI растёт", latest['rsi'] > prev['rsi']),
        ("MACD > сигнала", latest['macd'] > latest['macd_signal']),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("Объём > MA * 1.2", latest['volume'] > latest['volume_ma'] * 1.2)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("trend_pullback_ema50", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_trend_breakout_rsi_macd(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("EMA50 > EMA200", latest['ema_50'] > latest['ema_200']),
        ("RSI > 60", latest['rsi'] > 60),
        ("RSI растёт", latest['rsi'] > prev['rsi']),
        ("MACD > сигнала", latest['macd'] > latest['macd_signal']),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist']),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("Объём > MA * 1.3", latest['volume'] > latest['volume_ma'] * 1.3)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("trend_breakout_rsi_macd", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_ma_stack_squeeze_entry(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("EMA9 > EMA21 > EMA50", latest['ema_9'] > latest['ema_21'] > latest['ema_50']),
        ("EMA50 > EMA200", latest['ema_50'] > latest['ema_200']),
        ("Bollinger ширина < MA ширины", latest['boll_width'] < latest['boll_width_ma']),
        ("RSI > 50", latest['rsi'] > 50),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("Объём > MA * 1.5", latest['volume'] > latest['volume_ma'] * 1.5),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("ma_stack_squeeze_entry", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_rsi_ema_confluence(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("EMA50 > EMA200", latest['ema_50'] > latest['ema_200']),
        ("EMA9 > EMA21 > EMA50", latest['ema_9'] > latest['ema_21'] > latest['ema_50']),
        ("RSI > 55", latest['rsi'] > 55),
        ("RSI растёт", latest['rsi'] > prev['rsi']),
        ("MACD > сигнала", latest['macd'] > latest['macd_signal']),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("Объём > MA * 1.3", latest['volume'] > latest['volume_ma'] * 1.3)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("rsi_ema_confluence", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_adx_trend_follow(symbol, df):
    latest = df.iloc[-1]
    passed, total = 0, 7

    conditions = [
        ("ADX > 25", latest['adx'] > 25),
        ("ADX+ > ADX-", latest['adx_pos'] > latest['adx_neg']),
        ("EMA50 > EMA200", latest['ema_50'] > latest['ema_200']),
        ("EMA9 > EMA21 > EMA50", latest['ema_9'] > latest['ema_21'] > latest['ema_50']),
        ("RSI > 55", latest['rsi'] > 55),
        ("MACD > сигнала", latest['macd'] > latest['macd_signal']),
        ("Объём > MA * 1.2", latest['volume'] > latest['volume_ma'] * 1.2)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("adx_trend_follow", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_bull_trap_fakeout(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("Предыдущая свеча пробивала EMA200", prev['high'] > prev['ema_200'] * 1.01),
        ("Текущая свеча ниже EMA200", latest['close'] < latest['ema_200']),
        ("RSI падает", latest['rsi'] < prev['rsi']),
        ("RSI > 60 на предыдущей", prev['rsi'] > 60),
        ("MACD hist снижается", latest['macd_hist'] < prev['macd_hist']),
        ("Красная свеча", latest['close'] < latest['open']),
        ("Объём > MA * 1.4", latest['volume'] > latest['volume_ma'] * 1.4)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("bull_trap_fakeout", "SELL", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_reversed_rsi_macd_divergence_short(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("RSI < предыдущего", latest['rsi'] < prev['rsi']),
        ("RSI был > 70", prev['rsi'] > 70),
        ("MACD hist падает", latest['macd_hist'] < prev['macd_hist']),
        ("Цена > EMA50", latest['close'] > latest['ema_50']),
        ("Красная свеча", latest['close'] < latest['open']),
        ("Объём > MA * 1.3", latest['volume'] > latest['volume_ma'] * 1.3),
        ("Bollinger ширина растёт", latest['boll_width'] > prev['boll_width'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("rsi_macd_divergence_short", "BUY", passed, total, conditions, tp_pct=0.013, sl_pct=0.09)

def strategy_exhaustion_volume_top(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    body = abs(latest['close'] - latest['open'])
    wick = latest['high'] - latest['low']

    conditions = [
        ("RSI > 70", latest['rsi'] > 70),
        ("RSI падает", latest['rsi'] < prev['rsi']),
        ("MACD hist падает", latest['macd_hist'] < prev['macd_hist']),
        ("Объём > MA * 2", latest['volume'] > latest['volume_ma'] * 2),
        ("Свеча с малым телом", body < wick * 0.3),
        ("Красная свеча", latest['close'] < latest['open']),
        ("EMA9 > EMA21", latest['ema_9'] > latest['ema_21'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("exhaustion_volume_top", "SELL", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_macd_hist_decline_peak(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("MACD hist падает", latest['macd_hist'] < prev['macd_hist']),
        ("MACD hist был > 0", prev['macd_hist'] > 0),
        ("RSI > 60", latest['rsi'] > 60),
        ("RSI падает", latest['rsi'] < prev['rsi']),
        ("Красная свеча", latest['close'] < latest['open']),
        ("Объём > MA * 1.2", latest['volume'] > latest['volume_ma'] * 1.2),
        ("EMA9 < EMA21", latest['ema_9'] < latest['ema_21'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("macd_hist_decline_peak", "SELL", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_bollinger_pop_and_fade(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("Предыдущая свеча выше BB upper", prev['close'] > prev['boll_upper']),
        ("Текущая свеча ниже BB upper", latest['close'] < latest['boll_upper']),
        ("RSI > 65", latest['rsi'] > 65),
        ("RSI падает", latest['rsi'] < prev['rsi']),
        ("MACD hist падает", latest['macd_hist'] < prev['macd_hist']),
        ("Красная свеча", latest['close'] < latest['open']),
        ("Объём > MA * 1.4", latest['volume'] > latest['volume_ma'] * 1.4)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("bollinger_pop_and_fade", "SELL", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_rsi_divergence_reversal(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("Цена < предыдущей", latest['close'] < prev['close']),
        ("RSI > предыдущего", latest['rsi'] > prev['rsi']),
        ("RSI ранее < 30", prev['rsi'] < 30),
        ("RSI сейчас > 35", latest['rsi'] > 35),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist']),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("Объём > MA * 1.3", latest['volume'] > latest['volume_ma'] * 1.3)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("rsi_divergence_reversal", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_macd_divergence_reversal(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("Цена < предыдущей", latest['close'] < prev['close']),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist']),
        ("MACD hist ранее < 0", prev['macd_hist'] < 0),
        ("RSI > 30", latest['rsi'] > 30),
        ("RSI растёт", latest['rsi'] > prev['rsi']),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("Объём > MA * 1.3", latest['volume'] > latest['volume_ma'] * 1.3)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("macd_divergence_reversal", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_stoch_rsi_diver_entry(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("Цена < предыдущей", latest['close'] < prev['close']),
        ("Stoch K ранее < 20", prev['stoch_k'] < 20),
        ("Stoch K сейчас > 30", latest['stoch_k'] > 30),
        ("Stoch K > D", latest['stoch_k'] > latest['stoch_d']),
        ("RSI > 35", latest['rsi'] > 35),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("Объём > MA * 1.2", latest['volume'] > latest['volume_ma'] * 1.2)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("stoch_rsi_diver_entry", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_reversed_bollinger_squeeze_macd_pop(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("Bollinger ширина < MA", latest['boll_width'] < latest['boll_width_ma']),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist']),
        ("MACD hist < 0", latest['macd_hist'] < 0),
        ("RSI растёт", latest['rsi'] > prev['rsi']),
        ("RSI > 40", latest['rsi'] > 40),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("Объём > MA * 1.4", latest['volume'] > latest['volume_ma'] * 1.4)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("reversed_bollinger_squeeze_macd_pop", "BUY", passed, total, conditions, tp_pct=0.012, sl_pct=0.009)

def strategy_reversed_volume_dry_spike(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    volume_mean = df['volume'].iloc[-6:-1].mean()
    passed, total = 0, 7

    conditions = [
        ("Средний объём < MA * 0.8", volume_mean < latest['volume_ma'] * 0.8),
        ("Текущий объём > MA * 1.5", latest['volume'] > latest['volume_ma'] * 1.5),
        ("RSI растёт", latest['rsi'] > prev['rsi']),
        ("RSI > 40", latest['rsi'] > 40),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist']),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("EMA9 > EMA21", latest['ema_9'] > latest['ema_21'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("volume_dry_spike", "SELL", passed, total, conditions, tp_pct=0.01, sl_pct=0.007)

def strategy_flat_range_breakout(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    small_bodies = df.iloc[-6:-1].apply(
        lambda row: abs(row['close'] - row['open']) / max((row['high'] - row['low']), 1e-9) < 0.4,
        axis=1
    ).sum()

    conditions = [
        ("4+ свечей с малыми телами", small_bodies >= 4),
        ("Bollinger ширина < MA", latest['boll_width'] < latest['boll_width_ma']),
        ("RSI растёт", latest['rsi'] > prev['rsi']),
        ("RSI > 45", latest['rsi'] > 45),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist']),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("Объём > MA * 1.5", latest['volume'] > latest['volume_ma'] * 1.5)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("flat_range_breakout", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)


def strategy_reversed_engulfing_with_volume(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    body = abs(latest['close'] - latest['open'])
    prev_body = abs(prev['close'] - prev['open'])

    conditions = [
        ("Текущая свеча зелёная", latest['close'] > latest['open']),
        ("Предыдущая свеча красная", prev['close'] < prev['open']),
        ("Тело текущей > предыдущей", body > prev_body),
        ("RSI растёт", latest['rsi'] > prev['rsi']),
        ("RSI > 40", latest['rsi'] > 40),
        ("Объём > MA * 1.5", latest['volume'] > latest['volume_ma'] * 1.5),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("reversed_engulfing_with_volume", "BUY", passed, total, conditions, tp_pct=0.01, sl_pct=0.007)

def strategy_hammer_with_bb_support(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    body = abs(latest['close'] - latest['open'])
    wick = latest['high'] - latest['low']

    conditions = [
        ("Нижняя тень > 1.5%", (latest['close'] - latest['low']) / latest['close'] > 0.015),
        ("Тело < 35% от длины", body < wick * 0.35),
        ("Свеча зелёная", latest['close'] > latest['open']),
        ("Закрытие выше BB lower", latest['close'] > latest['boll_lower']),
        ("RSI > 35", latest['rsi'] > 35),
        ("MACD hist растёт", latest['macd_hist'] > prev['macd_hist']),
        ("Объём > MA * 1.5", latest['volume'] > latest['volume_ma'] * 1.5)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("hammer_with_bb_support", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_morning_star_combo(symbol, df):
    c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    passed, total = 0, 7

    body_1 = abs(c1['close'] - c1['open'])
    body_2 = abs(c2['close'] - c2['open'])
    body_3 = abs(c3['close'] - c3['open'])
    wick_2 = c2['high'] - c2['low']

    conditions = [
        ("1-я свеча красная", c1['close'] < c1['open']),
        ("2-я свеча маленькая", body_2 < wick_2 * 0.3),
        ("3-я свеча зелёная и > 1-й", c3['close'] > c3['open'] and body_3 > body_1),
        ("RSI растёт", c3['rsi'] > c2['rsi']),
        ("RSI > 35", c3['rsi'] > 35),
        ("MACD hist растёт", c3['macd_hist'] > c2['macd_hist']),
        ("Объём > MA * 1.4", c3['volume'] > c3['volume_ma'] * 1.4)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("morning_star_combo", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_three_soldiers_entry(symbol, df):
    c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    passed, total = 0, 7

    conditions = [
        ("3 свечи зелёные", all(c['close'] > c['open'] for c in [c1, c2, c3])),
        ("Каждая закрылась выше предыдущей", c3['close'] > c2['close'] > c1['close']),
        ("RSI растёт", c3['rsi'] > c2['rsi'] > c1['rsi']),
        ("RSI последней > 45", c3['rsi'] > 45),
        ("MACD hist растёт", c3['macd_hist'] > c2['macd_hist']),
        ("Объём > MA * 1.2", c3['volume'] > c3['volume_ma'] * 1.2),
        ("EMA9 > EMA21", c3['ema_9'] > c3['ema_21'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("three_soldiers_entry", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_multi_signal_confluence(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 8

    conditions = [
        ("EMA9 > EMA21 > EMA50 > EMA200", latest['ema_9'] > latest['ema_21'] > latest['ema_50'] > latest['ema_200']),
        ("RSI > 55 и растёт", latest['rsi'] > 55 and latest['rsi'] > prev['rsi']),
        ("MACD > сигнала и hist растёт", latest['macd'] > latest['macd_signal'] and latest['macd_hist'] > prev['macd_hist']),
        ("ADX > 25 и + > -", latest['adx'] > 25 and latest['adx_pos'] > latest['adx_neg']),
        ("Зелёная свеча", latest['close'] > latest['open']),
        ("Объём > MA * 1.5", latest['volume'] > latest['volume_ma'] * 1.5),
        ("Закрытие выше BB middle", latest['close'] > (latest['boll_upper'] + latest['boll_lower']) / 2),
        ("Bollinger ширина растёт", latest['boll_width'] > prev['boll_width'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("multi_signal_confluence", "BUY", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_parabolic_exhaustion_reversal(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("RSI > 75", latest['rsi'] > 75),
        ("RSI падает", latest['rsi'] < prev['rsi']),
        ("MACD hist падает", latest['macd_hist'] < prev['macd_hist']),
        ("Тело < 30%", abs(latest['close'] - latest['open']) / max((latest['high'] - latest['low']), 1e-9) < 0.3),
        ("Объём > MA * 2", latest['volume'] > latest['volume_ma'] * 2),
        ("EMA9 < EMA21", latest['ema_9'] < latest['ema_21']),
        ("Свеча красная", latest['close'] < latest['open'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("parabolic_exhaustion_reversal", "SELL", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_false_breakout_bear_trap(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    conditions = [
        ("Предыдущая свеча выше EMA200", prev['close'] > prev['ema_200']),
        ("Текущая свеча ниже EMA200", latest['close'] < latest['ema_200']),
        ("RSI падает", latest['rsi'] < prev['rsi']),
        ("MACD hist падает", latest['macd_hist'] < prev['macd_hist']),
        ("Пробой Bollinger верхней", latest['high'] > latest['boll_upper']),
        ("Свеча красная", latest['close'] < latest['open']),
        ("Объём > MA * 1.4", latest['volume'] > latest['volume_ma'] * 1.4)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("false_breakout_bear_trap", "SELL", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_vertical_blowoff_top(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    upper_wick = latest['high'] - max(latest['close'], latest['open'])
    candle_range = latest['high'] - latest['low']
    wick_ratio = upper_wick / max(candle_range, 1e-9)
    body_ratio = abs(latest['close'] - latest['open']) / max(candle_range, 1e-9)

    conditions = [
        ("Верхняя тень > 2.5%", wick_ratio > 0.025),
        ("Тело < 30%", body_ratio < 0.3),
        ("RSI > 70", latest['rsi'] > 70),
        ("RSI падает", latest['rsi'] < prev['rsi']),
        ("MACD hist падает", latest['macd_hist'] < prev['macd_hist']),
        ("EMA9 > EMA21", latest['ema_9'] > latest['ema_21']),
        ("Объём > MA * 2", latest['volume'] > latest['volume_ma'] * 2)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("vertical_blowoff_top", "SELL", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)

def strategy_reversed_slow_drift_fakeup(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    volume_1 = df.iloc[-2]['volume']
    volume_2 = df.iloc[-3]['volume']
    volume_3 = df.iloc[-4]['volume']

    conditions = [
        ("RSI < 60", latest['rsi'] < 60),
        ("RSI падает", latest['rsi'] < prev['rsi']),
        ("Bollinger ширина сжата", latest['boll_width'] < latest['boll_width_ma']),
        ("Объём 3 свечи падает", volume_3 > volume_2 > volume_1),
        ("MACD hist падает", latest['macd_hist'] < prev['macd_hist']),
        ("EMA9 ≈ EMA21", abs(latest['ema_9'] - latest['ema_21']) / latest['close'] < 0.002),
        ("Свеча красная", latest['close'] < latest['open'])
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("reversed_slow_drift_fakeup", "BUY", passed, total, conditions, tp_pct=0.01, sl_pct=0.007)

def strategy_macd_cross_fail_reversal(symbol, df):
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    passed, total = 0, 7

    # "MACD кросс вниз после вверх" = вчера был выше сигнальной, а сегодня ниже
    macd_cross_fail = prev['macd'] > prev['macd_signal'] and latest['macd'] < latest['macd_signal']

    conditions = [
        ("MACD ложный кросс вниз", macd_cross_fail),
        ("RSI падает", latest['rsi'] < prev['rsi']),
        ("RSI > 60", latest['rsi'] > 60),
        ("EMA9 < EMA21", latest['ema_9'] < latest['ema_21']),
        ("MACD hist < 0 и падает", latest['macd_hist'] < 0 and latest['macd_hist'] < prev['macd_hist']),
        ("Свеча красная", latest['close'] < latest['open']),
        ("Объём > MA * 1.2", latest['volume'] > latest['volume_ma'] * 1.2)
    ]

    for _, c in conditions:
        passed += c

    return format_strategy("macd_cross_fail_reversal", "SELL", passed, total, conditions, tp_pct=0.015, sl_pct=0.01)




def check_all_strategies(symbol, df):
    strategy_funcs = {
        "panic_wick_reversal": strategy_panic_wick_reversal,
        "volume_cliff_bounce": strategy_volume_cliff_bounce,
        "flash_crash_recover": strategy_flash_crash_recover,
        "oversold_rsi_explosion": strategy_oversold_rsi_explosion,
        "bb_lower_squeeze_pop": strategy_bb_lower_squeeze_pop,
        "trend_pullback_ema50": strategy_trend_pullback_ema50,
        "trend_breakout_rsi_macd": strategy_trend_breakout_rsi_macd,
        "ma_stack_squeeze_entry": strategy_ma_stack_squeeze_entry,
        "rsi_ema_confluence": strategy_rsi_ema_confluence,
        "adx_trend_follow": strategy_adx_trend_follow,
        "bull_trap_fakeout": strategy_bull_trap_fakeout,
        "reversed_rsi_macd_divergence_short": strategy_reversed_rsi_macd_divergence_short,
        "exhaustion_volume_top": strategy_exhaustion_volume_top,
        "macd_hist_decline_peak": strategy_macd_hist_decline_peak,
        "bollinger_pop_and_fade": strategy_bollinger_pop_and_fade,
        "rsi_divergence_reversal": strategy_rsi_divergence_reversal,
        "macd_divergence_reversal": strategy_macd_divergence_reversal,
        "stoch_rsi_diver_entry": strategy_stoch_rsi_diver_entry,
        "reversed_bollinger_squeeze_macd_pop": strategy_reversed_bollinger_squeeze_macd_pop,
        "reversed_volume_dry_spike": strategy_reversed_volume_dry_spike,
        "flat_range_breakout": strategy_flat_range_breakout,
        "reversed_engulfing_with_volume": strategy_reversed_engulfing_with_volume,
        "hammer_with_bb_support": strategy_hammer_with_bb_support,
        "morning_star_combo": strategy_morning_star_combo,
        "three_soldiers_entry": strategy_three_soldiers_entry,
        "multi_signal_confluence": strategy_multi_signal_confluence,
        "parabolic_exhaustion_reversal": strategy_parabolic_exhaustion_reversal,
        "false_breakout_bear_trap": strategy_false_breakout_bear_trap,
        "vertical_blowoff_top": strategy_vertical_blowoff_top,
        "reversed_slow_drift_fakeup": strategy_reversed_slow_drift_fakeup,
        "macd_cross_fail_reversal": strategy_macd_cross_fail_reversal,
    }


    items = list(strategy_funcs.items())
    random.shuffle(items)

    # ⬇️ Вставляем фильтрацию по cooldown
    now = datetime.now(timezone.utc)
    items = [(k, v) for k, v in items if k not in strategy_cooldowns or now > strategy_cooldowns[k]]

    for name, func in items:
        if not ENABLED_STRATEGIES.get(name, True):
            continue

        result = func(symbol, df)
        if result:
            print(f"\n🧠 Стратегия: {result['strategy']}")
            print(f"✅ Прошло условий: {result['passed']} из {result['total']}")
            for desc, ok in result['conditions']:
                print(f"   {'✅' if ok else '❌'} {desc}")

            if result['success']:
                 # ⬇️ Запоминаем cooldown
                strategy_cooldowns[result["strategy"]] = datetime.now(timezone.utc) + timedelta(minutes=STRATEGY_COOLDOWN_MINUTES)

                return {
                    "side": result["side"],
                    "strategy": result["strategy"],
                    "tp_pct": result.get("tp_pct"),
                    "sl_pct": result.get("sl_pct")
                }

    return None
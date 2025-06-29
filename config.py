API_KEY = "131212"
API_SECRET = "1212"


BOT_NAME = "Dayana"

# Основные торговые параметры
TRADE_AMOUNT = 100        # Сумма на сделку (в USDT)
TP_PCT = 0.019           # Take-Profit: +1.5%
SL_PCT = 0.011            # Stop-Loss: –1.0%
LEVERAGE = 4             # Кредитное плечо

# Таймфрейм и частота проверок
DEFAULT_INTERVAL = '5m'               # Таймфрейм
CHECK_INTERVAL_SECONDS = 28            # Интервал между циклами в секундах


# Список монет для анализа
SYMBOLS = [
        "1000SHIBUSDT", "1000PEPEUSDT", "1000FLOKIUSDT", "1000XECUSDT", "1000LUNCUSDT",
        "DOGEUSDT", "ADAUSDT", "XRPUSDT", "DOTUSDT",
        "AVAXUSDT", "MATICUSDT", "TRXUSDT", "LINKUSDT", "OPUSDT",
        "ARBUSDT", "RNDRUSDT", "SUIUSDT", "ENAUSDT", "ORDIUSDT",
        "TIAUSDT", "LQTYUSDT", "SEIUSDT", "WIFUSDT", "MEMEUSDT",
        "BLURUSDT", "NOTUSDT", "PYTHUSDT", "JUPUSDT", "STRKUSDT",
        "ZETAUSDT", "TOKENUSDT", "ARKMUSDT", "CYBERUSDT", "PIXELUSDT",
        "ACEUSDT", "IDUSDT", "PEOPLEUSDT", "AGIXUSDT", "SSVUSDT",
        "FETUSDT", "INJUSDT", "LINAUSDT", "GMTUSDT", "GALAUSDT",
        "LDOUSDT", "DYDXUSDT", "STORJUSDT", "XLMUSDT"
    ]


ENABLED_STRATEGIES = {
    "panic_wick_reversal": True,
    "volume_cliff_bounce": True,
    "flash_crash_recover": True,
    "oversold_rsi_explosion": True,
    "bb_lower_squeeze_pop": True,
    "trend_pullback_ema50": True,
    "trend_breakout_rsi_macd": True,
    "ma_stack_squeeze_entry": True,
    "rsi_ema_confluence": True,
    "adx_trend_follow": True,
    "bull_trap_fakeout": True,
    "reversed_rsi_macd_divergence_short": True,
    "exhaustion_volume_top": True,
    "macd_hist_decline_peak": True,
    "bollinger_pop_and_fade": True,
    "rsi_divergence_reversal": True,
    "macd_divergence_reversal": True,
    "stoch_rsi_diver_entry": True,
    "reversed_bollinger_squeeze_macd_pop": True,
    "reversed_volume_dry_spike": True,
    "flat_range_breakout": True,
    "reversed_engulfing_with_volume": True,
    "hammer_with_bb_support": True,
    "morning_star_combo": True,
    "three_soldiers_entry": True,
    "multi_signal_confluence": True,
    "parabolic_exhaustion_reversal": True,
    "false_breakout_bear_trap": True,
    "vertical_blowoff_top": True,
    "reversed_slow_drift_fakeup": True,
    "macd_cross_fail_reversal": True

}


# Ограничения
MAX_OPEN_TRADES = 5      # Максимум одновременных сделок
ENABLE_LONG = True       # Разрешить входы в LONG
ENABLE_SHORT = True      # Разрешить входы в SHORT

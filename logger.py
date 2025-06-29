import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
from datetime import timezone

LOG_FILE = 'logs/trades_log.csv'

def log_trade(symbol, side, entry_price, qty, tp, sl, strategy, indicators, is_exit=False):
    timestamp = datetime.now(ZoneInfo("Europe/Warsaw")).isoformat()

    row = {
        "timestamp_entry": timestamp,
        "symbol": symbol,
        "side": side,
        "strategy": strategy,
        "entry_price": entry_price,
        "tp_price": tp,
        "sl_price": sl,
        "qty": qty,
        "timestamp_exit": indicators.get("timestamp_exit", ""),
        "exit_price": indicators.get("exit_price", ""),
        "exit_reason": indicators.get("exit_reason", ""),
        "pnl": indicators.get("pnl", "")
    }

    for key, value in indicators.items():
        if isinstance(value, (int, float, str)) and key not in row:
            row[key] = value

    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"📘 Записано в лог: {symbol} {side} {strategy} — entry @ {entry_price}")
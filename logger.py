import csv
import os
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

LOG_DIR = 'logs'
LOG_FILE = os.path.join(LOG_DIR, 'trades_log.csv')

# ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)




def log_trade(symbol, side, entry_price, qty, tp, sl, strategy, indicators, is_exit=False):
    timestamp = datetime.now(ZoneInfo("Europe/Warsaw")).isoformat()

    pnl_value = indicators.get("pnl", "")
    result = ""
    try:
        if pnl_value != "":
            result = "profit" if float(pnl_value) >= 0 else "loss"
    except Exception:
        pass

    row = {
        "time": timestamp,
        "symbol": symbol,
        "side": side,
        "strategy": strategy,
        "entry_price": entry_price,
        "exit_price": indicators.get("exit_price", ""),
        "result": result,
        "pnl": pnl_value,
        "tp_price": tp,
        "sl_price": sl,
        "qty": qty,
        "exit_reason": indicators.get("exit_reason", "")
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

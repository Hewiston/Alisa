import threading
import os
import csv
from telegram.ext import Updater, CommandHandler
from binance.client import Client
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, API_KEY, API_SECRET
from logger import LOG_FILE

bot = None


def send_telegram_message(text: str):
    """Send a message via telegram."""
    global bot
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        if bot:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        print(f"Telegram error: {e}")


def command_balance(update, context):
    try:
        client = Client(API_KEY, API_SECRET)
        balances = client.futures_account_balance()
        usdt = next(b for b in balances if b['asset'] == 'USDT')
        update.message.reply_text(f"Balance: {usdt['balance']} USDT")
    except Exception as e:
        update.message.reply_text(f"Error: {e}")


def command_active(update, context):
    try:
        import dayana
        if not dayana.active_trades:
            update.message.reply_text('Нет активных сделок')
            return
        lines = []
        for sym, trade in dayana.active_trades.items():
            tp = trade.get('tp', '')
            sl = trade.get('sl', '')
            lines.append(f"{sym} {trade['side']} entry:{trade['entry_price']} TP:{tp} SL:{sl}")
        update.message.reply_text('\n'.join(lines))
    except Exception as e:
        update.message.reply_text(f"Error: {e}")


def command_stats(update, context):
    profit, loss, total_pnl = 0, 0, 0.0
    if os.path.isfile(LOG_FILE):
        with open(LOG_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pnl_str = row.get('pnl')
                if pnl_str:
                    pnl = float(pnl_str)
                    total_pnl += pnl
                    if pnl >= 0:
                        profit += 1
                    else:
                        loss += 1
    update.message.reply_text(
        f"Profit trades: {profit}\nLoss trades: {loss}\nTotal PnL: {total_pnl:.2f} USDT")


def command_pause(update, context):
    import dayana
    dayana.PAUSE_MODE = True
    update.message.reply_text('Приём сигналов остановлен')


def command_resume(update, context):
    import dayana
    dayana.PAUSE_MODE = False
    update.message.reply_text('Приём сигналов возобновлён')


def _run():
    global bot
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    bot = updater.bot
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('balance', command_balance))
    dp.add_handler(CommandHandler('active', command_active))
    dp.add_handler(CommandHandler('stats', command_stats))
    dp.add_handler(CommandHandler('pause', command_pause))
    dp.add_handler(CommandHandler('resume', command_resume))
    updater.start_polling()
    updater.idle()


def start_bot_thread():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print('Telegram not configured. Bot disabled.')
        return
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return thread
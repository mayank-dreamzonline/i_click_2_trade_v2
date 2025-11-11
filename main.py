from breeze_auth import BreezeAuth
from trade import TradeManager
import time
from datetime import datetime
import pytz   # install with `pip install pytz` if not already
import subprocess
import logging
from logging_config import setup_logging
import concurrent.futures  # <--- 1. Import this

logger = logging.getLogger(__name__)

import trade_logger  # <--- This line

setup_logging()
trade_logger.init_db()
logger.info("Starting i_click_2_gain v2...")

auth = BreezeAuth()
breeze = auth.get_client()   # this is the BreezeConnect object

fund = breeze.get_funds()

allocated_equity_value = fund['Success']['allocated_equity']

print(allocated_equity_value)
trade_mgr = TradeManager(breeze)

IST = pytz.timezone("Asia/Kolkata")

try:
    breeze.ws_connect()
    logger.info(f"Connected at: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S %Z')}")

except Exception as e:
    logger.info("Live socket connect failed:", e)

def mac_notify(title: str, text: str) -> None:
    subprocess.run(["terminal-notifier", "-title", title, "-message", text], check=False)

limt_order = False

executor = concurrent.futures.ThreadPoolExecutor(max_workers=5, thread_name_prefix="TickProcessor")

def process_tick(msg: dict):
    logger.info("RECO: %s \n", msg)
    if 'userId' in msg:
        return
    stock_desc = trade_mgr.get_field(msg, "stock_description")
    subscription_type = trade_mgr.get_field(msg, "subscription_type").lower()
    action_type = trade_mgr.get_field(msg, "action_type").lower()
    stock_code = trade_mgr.get_field(msg, "stock_code")
    if "iclick_2_gain" not in subscription_type:
        logger.info("Subscription type not iclick_2_gain -1, ignoring")
        return  # ignore other feeds
    if stock_desc.lower() != "margin":
        logger.info("Stock description not margin -1, ignoring")
        return  # v1 only handles intraday margin stocks
    if action_type not in ("buy", "sell") or not stock_code:
        logger.info("Action type not valid -1, ignoring")
        return  # malformed
    stock = (msg.get("stock_code") or msg.get("stockCode") or "")
    action = (msg.get("action_type") or msg.get("orderFlow") or "")
    trade_mgr.handle_market_reco(msg,limt_order, allocated_equity_value)
    now = (datetime.now().strftime("%H:%M:%S"))
    try:
        trade_logger.log_recommendation(msg)
    except Exception as e:
        logger.error(f"Failed to log recommendation: {e}")
    print("\a", end="")  # sound
    mac_notify("iClick2Gain Tick", f"{stock} {action} @ {now}")


def on_ticks(msg: dict):
    executor.submit(process_tick, msg)



breeze.on_ticks = on_ticks
breeze.subscribe_feeds(get_order_notification=True)
breeze.subscribe_feeds(stock_token="i_click_2_gain")


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    try: breeze.unsubscribe_feeds(stock_token="i_click_2_gain")
    except Exception: pass
    try: breeze.ws_disconnect()
    except Exception: pass



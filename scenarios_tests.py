## This file is used to test the scenarios
import pandas as pd
#from tabulate import tabulate
import logging
from logging_config import setup_logging
import time   # <--- ADDED: Required for high-resolution timing
from trade import TradeManager

logger = logging.getLogger(__name__)

setup_logging()

from trade import TradeManager

from breeze_auth import BreezeAuth

#auth = BreezeAuth()
#breeze = auth.get_client()   # this is the BreezeConnect object


def get_field( msg: dict, key: str) -> str:
    """Safely extract and strip a string field from msg dict."""
    return (msg.get(key) or "").strip()

msg ={'stock_name': 'GOKALDAS EXPORTS LIMITED(GOKEXP)Margin-Buy', 'stock_code': 'GOKEXP', 'action_type': 'buy', 'expiry_date': '', 'strike_price': '', 'option_type': '', 'stock_description': 'Margin', 'recommended_price_and_date': '876-877,2025-10-29 10:26:58', 'recommended_price_from': '876', 'recommended_price_to': '877', 'recommended_date': '2025-10-29 10:26:58', 'target_price': '888', 'sltp_price': '871', 'part_profit_percentage': '0,0', 'profit_price': '0', 'exit_price': '0', 'recommended_update': '   TGT1:2025-10-29 10:52:56  ', 'iclick_status': 'open', 'subscription_type': 'iclick_2_gain                 '}
recommended_update = get_field(msg, "recommended_update")
upd = (recommended_update or "").lower()
exit_hit = any(k in upd for k in ("book full profit", "book partial profit", "sltp", "exit", "tgt1"))
action_type = (msg.get("action_type") or "").lower()  # "buy" / "sell"
print(action_type)

if exit_hit:
    action_type = "sell" if action_type == "buy" else "buy"
print(recommended_update)
print(upd)
print(exit_hit)
print(action_type)
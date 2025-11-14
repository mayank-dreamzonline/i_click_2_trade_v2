## This file is used to test the scenarios
import pandas as pd
#from tabulate import tabulate
import logging
from logging_config import setup_logging
import time   # <--- ADDED: Required for high-resolution timing
from trade import TradeManager
import trade_logger

logger = logging.getLogger(__name__)

setup_logging()

from trade import TradeManager

from breeze_auth import BreezeAuth
trade_logger.init_db()


auth = BreezeAuth()
breeze = auth.get_client()   # this is the BreezeConnect object

stock_code = "FSNECO"
action_type = "buy"
order_type = "stoploss"
qty = 1
recommended_price_str = "261.4"
stoploss_price_str = "261"

payload_order = dict(
                stock_code=stock_code,
                exchange_code="NSE",
                product="margin",  # intraday/MIS
                action=action_type,  # buy/sell
                order_type=order_type,
                stoploss=stoploss_price_str,
                quantity=str(qty),
                price=recommended_price_str,
                validity="day",
            )
#print(payload_order)
#resp = breeze.place_order(**payload_order)
#print(resp)

resp=breeze.modify_order(order_id="20251114T300004392",
                    exchange_code="NSE",
                    order_type="limit",
                    stoploss="0",
                    quantity="2",
                    price="1515",
                    validity="day",
                    disclosed_quantity="0"
                    )
                    #validity_date="2025-08-22T06:00:00.000Z"
#               )

print(resp)
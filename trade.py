# trade.py
import os, json
from datetime import datetime
import logging
import time
from logging_config import setup_logging



from typing import TypedDict, Optional, Literal


logger = logging.getLogger(__name__)

class RecoMsg(TypedDict, total=False):
    stock_name: str
    stock_code: str
    action_type: Literal["buy", "sell"]   # only two valid values
    expiry_date: Optional[str]            # empty string if not future/option
    strike_price: Optional[str]
    option_type: Optional[Literal["call", "put", ""]]  # for options
    stock_description: Literal["Margin", "Future", "Options"]
    recommended_price_and_date: str
    recommended_price_from: str
    recommended_price_to: str
    recommended_date: str
    target_price: str
    sltp_price: str
    part_profit_percentage: str
    profit_price: str
    exit_price: str
    recommended_update: str
    iclick_status: Literal["open", "closed"]
    subscription_type: str

class OrderNotificationMsg(TypedDict, total=False):
    messageCategory: str                     # "Intraday Calls"
    orderExchangeCode: Literal["NSE","BSE"]
    stockCode: str
    orderFlow: Literal["Buy","Sell"]
    limitMarketFlag: Literal["Market","Limit"]
    orderType: Literal["Day","IOC","GTD","GTC"]
    orderLimitRate: str
    productType: Literal["Margin","Future","Options","CNC","NRML"]
    orderStatus: Literal["Placed","Pending","Executed","Cancelled","Rejected","Expired"]
    orderDate: str                           # "26-Aug-2025 12:32"
    orderTradeDate: str                      # "26-Aug-2025"
    orderReference: str
    orderQuantity: str
    openQuantity: str
    orderExecutedQuantity: str
    cancelledQuantity: str
    expiredQuantity: str
    orderDisclosedQuantity: str
    orderStopLossTrigger: str
    averageExecutedRate: str
    exchangeSegmentCode: str                 # e.g. "M"
    exchangeSegmentSettlement: str           # e.g. "2025163"
    marginSquareOffMode: Optional[str]
    channel: Optional[str]                   # "WEB", "API" etc.


class TradeManager:
    def __init__(self, breeze):
        self.breeze = breeze
        self.trade_mode = os.getenv("TRADE_MODE", "paper").lower()
        self.dry_run = self.trade_mode != "live"
        self.cash_qty = int(os.getenv("CASH_QTY", "1"))
        self.fut_qty  = int(os.getenv("FUT_QTY", "1"))
        self.opt_qty  = int(os.getenv("OPT_QTY", "50"))
        self.max_notional = float(os.getenv("MAX_NOTIONAL", "200000"))
        self._seen = set()

    def _log(self, event, **kw):
        rec = {"ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "event": event, "mode": self.trade_mode, **kw}
        print(json.dumps(rec, ensure_ascii=False))

    def get_field(self, msg: dict, key: str) -> str:
        """Safely extract and strip a string field from msg dict."""
        return (msg.get(key) or "").strip()

    def get_open_qty(self, stock_code: str) -> int:
        try:
            resp = self.breeze.get_portfolio_positions()
            positions = resp.get("Success", [])
            for pos in positions:
                if (pos.get("stock_code") == stock_code and
                        pos.get("segment") == "equity" and
                        pos.get("product_type", "").lower() == "margin"):
                    return int(pos.get("quantity", 0))
            return 0
        except Exception as e:
            print("[get_open_qty.error] \n", e)
            return 0

    def handle_market_reco(self, msg: dict, limit, fund):

           fund = 1000
           order_type = "limit"
           recommended_price_str = self.get_field(msg, "recommended_price_to")
           if recommended_price_str:  # This checks if the string is not empty or None
               price = float(recommended_price_str)
           else:
               price = 0.0  # Assign a default value, like 0.0, if the string is empty
           if price > 0:
               qty = int((fund / price)*4)
           else:
               qty = 0
               #"Disclosed qty cannot be greater than or equal to qt" Error will come if qty is 0
           stock_code = self.get_field(msg, "stock_code")
           subscription_type = self.get_field(msg, "subscription_type").lower()
           stock_desc = self.get_field(msg, "stock_description")
           action_type = self.get_field(msg, "action_type").lower()
           recommended_update = self.get_field(msg, "recommended_update")
           iclick_status = self.get_field(msg, "iclick_status").lower()

           ### Handling updated recommendations for exits
           upd = (recommended_update or "").lower()
           exit_hit = any(k in upd for k in ("book full profit", "book partial profit", "sltp", "exit", "tgt1")) or iclick_status == "closed"
           action_type = (msg.get("action_type") or "").lower()  # "buy" / "sell"

           if exit_hit:
                action_type = "sell" if action_type == "buy" else "buy"
                qty = self.get_open_qty(stock_code)
                order_type = "market"
                if qty <= 0:
                    return

           payload_order = dict(
                stock_code=stock_code,
                exchange_code="NSE",
                product="margin",  # intraday/MIS
                action=action_type,  # buy/sell
                order_type=order_type,
                quantity=str(qty),
                stoploss="0",
                price=recommended_price_str,
                validity="day",
            )

           try:
               if order_type == "limit":
                   logger.info("Placing limit order: %s \n", payload_order)
               else:
                   logger.info("Placing market order: %s \n", payload_order)
               resp = self.breeze.place_order(**payload_order)
               print("Response: \n", resp)
           except Exception as e:
               print("[order.error] \n", e)



    def handle_order_notification(msg: OrderNotificationMsg):
        code = msg.get("stockCode")
        flow = msg.get("orderFlow")
        status = msg.get("orderStatus")
        qty = msg.get("orderExecutedQuantity") or msg.get("orderQuantity")
        avg = msg.get("averageExecutedRate")
        ref = msg.get("orderReference")

        logger.info(f"[ORDER] {status} {flow} {qty} {code} @ {avg} (ref={ref})")


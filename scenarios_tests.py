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


#auth = BreezeAuth()
#breeze = auth.get_client()   # this is the BreezeConnect object


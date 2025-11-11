# trade_logger.py
import sqlite3
import os
import logging
from datetime import datetime

LOG_DIR = "logs"
DB_FILE = os.path.join(LOG_DIR, "trading.db")

logger = logging.getLogger(__name__)


# A simple helper to get a new database connection
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    # Ensure the log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    # Creates the file if it doesn't exist and returns a connection
    conn = sqlite3.connect(DB_FILE)
    # This will return rows as dictionaries, which is often easier to work with
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes the database and creates the 'recommendations' table
    if it doesn't already exist.
    Call this once when your application starts.
    """
    logger.info(f"Initializing database at {DB_FILE}...")

    # Define the table structure
    # We add 'logged_at' to timestamp when we saved it.
    # We use REAL for prices/targets and TEXT for everything else.
    create_table_sql = """
                       CREATE TABLE IF NOT EXISTS recommendations \
                       ( \
                           id \
                           INTEGER \
                           PRIMARY \
                           KEY \
                           AUTOINCREMENT, \
                           logged_at \
                           TEXT \
                           NOT \
                           NULL, \
                           stock_name \
                           TEXT, \
                           stock_code \
                           TEXT, \
                           action_type \
                           TEXT, \
                           expiry_date \
                           TEXT, \
                           strike_price \
                           TEXT, \
                           option_type \
                           TEXT, \
                           stock_description \
                           TEXT, \
                           recommended_price_and_date \
                           TEXT, \
                           recommended_price_from \
                           REAL, \
                           recommended_price_to \
                           REAL, \
                           recommended_date \
                           TEXT, \
                           target_price \
                           REAL, \
                           sltp_price \
                           REAL, \
                           part_profit_percentage \
                           TEXT, \
                           profit_price \
                           REAL, \
                           exit_price \
                           REAL, \
                           recommended_update \
                           TEXT, \
                           iclick_status \
                           TEXT, \
                           subscription_type \
                           TEXT
                       ); \
                       """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"An error occurred during database initialization: {e}")
        raise  # Re-raise the exception to stop the app if the DB can't be set up


def log_recommendation(msg: dict):
    """
    Logs a single recommendation message to the 'recommendations' table.
    """

    # SQL query with placeholders (?) to prevent SQL injection
    insert_sql = """
                 INSERT INTO recommendations (logged_at, stock_name, stock_code, action_type, expiry_date, \
                                              strike_price, option_type, stock_description, recommended_price_and_date, \
                                              recommended_price_from, recommended_price_to, recommended_date, \
                                              target_price, sltp_price, part_profit_percentage, profit_price, \
                                              exit_price, recommended_update, iclick_status, subscription_type) \
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) \
                 """

    try:
        # Prepare the data tuple in the correct order
        # We use .get(key) which returns None if the key doesn't exist
        data = (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            msg.get('stock_name'),
            msg.get('stock_code'),
            msg.get('action_type'),
            msg.get('expiry_date'),
            msg.get('strike_price'),
            msg.get('option_type'),
            msg.get('stock_description'),
            msg.get('recommended_price_and_date'),
            msg.get('recommended_price_from'),
            msg.get('recommended_price_to'),
            msg.get('recommended_date'),
            msg.get('target_price'),
            msg.get('sltp_price'),
            msg.get('part_profit_percentage'),
            msg.get('profit_price'),
            msg.get('exit_price'),
            msg.get('recommended_update'),
            msg.get('iclick_status'),
            msg.get('subscription_type')
        )

        # 'with' statement handles commit and close, or rollback on error
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(insert_sql, data)
            conn.commit()

    except sqlite3.Error as e:
        # This will log the error but not crash the main tick handler
        logger.error(f"Failed to log recommendation to SQLite: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred in log_recommendation: {e}")
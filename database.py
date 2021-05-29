import requests
import sqlite3
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time

"""Establish connection with sqlite"""
con = sqlite3.connect('erc20.db')
cur = con.cursor()

"""Create tables"""
TOKEN_INFO = "CREATE TABLE IF NOT EXISTS token_info (coingecko_id VARCHAR(50) UNIQUE PRIMARY KEY, symbol VARCHAR(50), " \
            "name VARCHAR(50), address VARCHAR(100))"

PRICES = "CREATE TABLE IF NOT EXISTS prices (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, timestamp FLOAT, " \
         "coingecko_id VARCHAR(50), prices FLOAT, FOREIGN KEY (coingecko_id) " \
         "REFERENCES token_info(coingecko_id) ON UPDATE CASCADE ON DELETE CASCADE)"

MARKET_CAPS = "CREATE TABLE IF NOT EXISTS market_caps (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, timestamp FLOAT, " \
         "coingecko_id VARCHAR(50), market_caps FLOAT, FOREIGN KEY (coingecko_id) " \
         "REFERENCES token_info(coingecko_id) ON UPDATE CASCADE ON DELETE CASCADE)"

TOTAL_VOLUMES = "CREATE TABLE IF NOT EXISTS total_volumes (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, timestamp FLOAT, " \
         "coingecko_id VARCHAR(50), total_volumes FLOAT, FOREIGN KEY (coingecko_id) " \
         "REFERENCES token_info(coingecko_id) ON UPDATE CASCADE ON DELETE CASCADE)"


cur.execute(TOKEN_INFO)
cur.execute(PRICES)
cur.execute(MARKET_CAPS)
cur.execute(TOTAL_VOLUMES)


con.commit()


"""Static list of symbols and names of ERC 20 tokens in top 80 rank coingecko. 
    These names are taken by matching info from coingecko and etherscan."""
#SYMBOLS = ["USDT", "BNB", "USDC", "UNI", "LINK", "BUSD", "THETA", "VET", "WBTC", "TRX", "DAI", "OKB", "CETH", "CUSDC", "MKR",
#            "CRO", "CDAI", "CEL", "HT", "BTT", "COMP", "SNX", "SUSHI", "LEO", "UST", "TEL", "CHZ", "HOT", "YFI", "ENJ", "ZIL",
#            "AMP", "PAX", "TUSD", "BAT", "HBTC"]

NAMES = ['Tether', 'Binance Coin', 'USD Coin', 'Uniswap', 'Chainlink', 'Binance USD', 'Theta Network', 'VeChain', 
        'Wrapped Bitcoin', 'TRON', 'Dai', 'OKB', 'cETH', 'cUSDC', 'Maker', 'Crypto.com Coin', 'cDAI', 'Celsius Network',
        'Huobi Token', 'BitTorrent', 'Compound', 'Synthetix Network Token', 'Sushi', 'LEO Token', 'Wrapped UST (BSC)', 
        'Telcoin', 'Chiliz', 'Holo', 'yearn.finance', 'Enjin Coin', 'Zilliqa', 'Amp', 'Paxos Standard', 'TrueUSD', 
        'Basic Attention Token', 'Huobi BTC']

"""coingecko API"""
BASE_URL = "https://api.coingecko.com/api/v3"

coins_list_url = f"{BASE_URL}/coins/list"
payload = {"include_platform": "true"}

response = requests.request("GET", coins_list_url, params=payload)
coins_list = json.loads(response.text)

erc20_tokens = []

"""Find coin ids and token addresses by accessing coingecko API"""
for coin in coins_list:
    for name in NAMES:
        if coin['name'] == name:
            """Unfortunately, for 7 out of 36 coins listed above, the token address are not in the coingecko API.
                These coins are omitted, so 29 coins remain."""
            if 'ethereum' in coin['platforms']:
                erc20_tokens.append((coin['id'], coin['symbol'], coin['name'], coin['platforms']['ethereum']))


"""Initialise token_info table"""

ADD_TOKEN = "INSERT INTO token_info (coingecko_id, symbol, name, address) VALUES (?, ?, ?, ?)"
con.executemany(ADD_TOKEN, erc20_tokens)
con.commit()

#find unix timestamps at current time
date_now = datetime.now()
unix_now = date_now.timestamp()
print(unix_now)

#find unix timestamps from 3 months ago
date_3m = date_now + relativedelta(months=-3)
unix_3m = date_3m.timestamp()
print(unix_3m)


for token_tuple in erc20_tokens:
    coingecko_id = token_tuple[0]

    market_chart_url = f"{BASE_URL}/coins/{coingecko_id}/market_chart/range"
    payload = {"vs_currency": "usd", "from": unix_3m, "to": unix_now}
    response = requests.request("GET", market_chart_url, params=payload)
    json_response = json.loads(response.text)
    
    for key, values in json_response.items():
        for value in values:
            cur.execute(f"INSERT INTO {key} (timestamp, coingecko_id, {key}) VALUES (?, ?, ?)", 
            (value[0], coingecko_id, value[1]))
        con.commit()

con.close()

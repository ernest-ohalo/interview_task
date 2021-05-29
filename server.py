import flask
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json

APP = flask.Flask(__name__)

GET_ADDRESS = "SELECT address FROM token_info WHERE symbol = ?"
GET_ID = "SELECT coingecko_id FROM token_info WHERE address = ?"
GET_ID_FROM_SYMBOL = "SELECT coingecko_id FROM token_info WHERE symbol = ?"
GET_VOLUME = "SELECT timestamp, total_volumes FROM total_volumes WHERE coingecko_id = ? AND timestamp < ? AND timestamp >= ?"
GET_PRICE = "SELECT timestamp, prices FROM prices WHERE coingecko_id = ? AND timestamp < ? AND timestamp >= ?"

@APP.route('/token/<address>/volume', methods=['GET'])
def get_volume(address):

    con = sqlite3.connect('erc20.db')
    cur = con.cursor()

    cur.execute(GET_ID, (address,))

    coingecko_id = cur.fetchone()

    date_now = datetime.now()

    if flask.request.args:
        date_now = datetime.strptime(flask.request.args["date"], "%Y-%m-%d")

    unix_now = date_now.timestamp() * 1000

    date_1w = date_now - timedelta(weeks=1)
    unix_1w = date_1w.timestamp() * 1000

    cur.execute(GET_VOLUME, (coingecko_id[0], unix_now, unix_1w))

    data = cur.fetchall()
    
    response = {"id": coingecko_id, "volume": {}}
    
    total_volume = 0
    for row in data:
        response["volume"][datetime.fromtimestamp(row[0]/1000).strftime("%d/%m/%Y %H:%M:%S")] = row[1]
        total_volume += row[1]

    response['estimated_weekly_volume'] = total_volume/24

    return response


@APP.route('/token/<symbol>/address', methods=['GET'])
def get_address(symbol):

    con = sqlite3.connect('erc20.db')
    cur = con.cursor()

    cur.execute(GET_ADDRESS, (symbol.lower(),))

    token_address = cur.fetchone()
    
    return {"token_address": token_address}


@APP.route('/token/<symbol>/price', methods=['GET'])
def get_average_price(symbol):

    con = sqlite3.connect('erc20.db')
    cur = con.cursor()

    cur.execute(GET_ID_FROM_SYMBOL, (symbol.lower(),))

    coingecko_id = cur.fetchone()
    
    date_now = datetime.now()
    if flask.request.args:
        date_now = datetime.strptime(flask.request.args["date"], "%Y-%m-%d")

    unix_now = date_now.timestamp()

    date_1m = date_now + relativedelta(months=-1)
    unix_1m = date_1m.timestamp()

    unix_ls = []

    unix_time = unix_1m
    while unix_time <= unix_now:
        unix_ls.append(unix_time)
        unix_time += 86400

    response = {"id": coingecko_id, "average_price": {}}
    
    for i in range(len(unix_ls)-1):
        start_time = unix_ls[i] * 1000
        end_time = unix_ls[i+1] * 1000

        cur.execute(GET_PRICE, (coingecko_id[0], end_time, start_time))

        data = cur.fetchall()

        average = 0
        for row in data:
            average += row[1]/len(data)

        response["average_price"][datetime.fromtimestamp(end_time/1000).strftime("%d/%m/%Y %H:%M:%S")] = average

    return flask.Response(json.dumps(response, indent=2), mimetype='application/json')
    

if __name__ == "__main__":
    APP.run(host='0.0.0.0', port='8082', debug=True)
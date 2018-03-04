from flask import Flask, jsonify
import ccxt
import api_keys
import logging
import json
from InvalidUsage import InvalidUsage

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('taurus')

sandbox = True
trades_allowed = True

logger.info('Trading enabled......' + str(trades_allowed))

app = Flask(__name__)

# Instantiate GDAX API
exchange = ccxt.gdax()
logger.debug('Loading exchange API keys.....')
exchange.apiKey = api_keys.API_KEYS['apiKey']
exchange.secret = api_keys.API_KEYS['secret']
exchange.password = api_keys.API_KEYS['passphrase']
logger.debug('Exchange API keys loaded successfully')

if sandbox and exchange.urls['test']:
    exchange.urls['api'] = exchange.urls['test']
    logger.info('Running in SANDBOX MODE')
else:
    logger.info('Running in PRODUCTION MODE')
logger.debug('Exchange API URL: ' + exchange.urls['api'])

# Check for bad exchange API keys early
try:
    json.dumps(exchange.fetch_balance())
# Handle bad keys
except ccxt.base.errors.AuthenticationError as e:
    raise InvalidUsage(str(e), status_code=403)


@app.route('/')
def hello_world():
    return 'Welcome to the Taurus API!'


# Fetch all balances
@app.route('/balance', methods=["GET"])
def get_balance():
    balance = json.dumps(exchange.fetch_balance())
    return balance


# Fetch all orders
@app.route('/orders', defaults={'symbol': None}, methods=["GET"])
@app.route('/orders/<symbol>', methods=["GET"])
def get__orders(symbol):
    if exchange.hasFetchOrders:
        return json.dumps(exchange.fetch_orders(symbol=symbol))
    else:
        raise InvalidUsage('Exchange does not support fetching orders', status_code=422)


# Fetch all open orders
@app.route('/orders/open', defaults={'symbol': None}, methods=["GET"])
@app.route('/orders/open/<symbol>', methods=["GET"])
def get_open_orders(symbol):
    if exchange.hasFetchOpenOrders:
        return json.dumps(exchange.fetch_open_orders(symbol=symbol))
    else:
        raise InvalidUsage('Exchange does not support fetching open orders', status_code=422)


# Fetch all closed orders
@app.route('/orders/closed', defaults={'symbol': None}, methods=["GET"])
@app.route('/orders/closed/<symbol>', methods=["GET"])
def get_open_orders(symbol):
    if exchange.hasFetchClosedOrders:
        return json.dumps(exchange.fetch_closed_orders(symbol=symbol))
    else:
        raise InvalidUsage('Exchange does not support fetching closed orders', status_code=422)


# Place new order
@app.route('/order', methods=["POST"])
def make_order():
    symbol = request.args.get('symbol')
    side = request.args.get('side')
    order_type = request.args.get('type')
    amount = request.args.get('amount')
    price = request.args.get('price')

    if order_type == "market":
        if side == "buy":
            return json.dumps(exchange.create_market_buy_order(symbol, amount))
        elif side == "sell":
            return json.dumps(exchange.create_market_sell_order(symbol, amount))
        else:
            raise InvalidUsage('Invalid order side', status_code=400)
    elif order_type == "limit":
        if side == "buy":
            return json.dumps(exchange.create_limit_buy_order(symbol, amount, price))
        elif side == "sell":
            return json.dumps(exchange.create_limit_sell_order(symbol, amount, price))
        raise InvalidUsage('Invalid order side', status_code=400)
    else:
        raise InvalidUsage('Invalid order type', status_code=400)


# Cancel order
@app.route('/cancel/<order_id>', methods=["POST"])
def cancel_order(order_id):
    return json.dumps(exchange.cancel_order(order_id))



@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run()

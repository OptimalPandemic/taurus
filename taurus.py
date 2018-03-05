import datetime

import jwt
from flask import Flask, jsonify, request, Response, make_response
import ccxt
import api_keys
import logging
import json
import requests
from passlib.apps import custom_app_context as pwd_context
from InvalidUsage import InvalidUsage

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('taurus')

sandbox = True
trades_allowed = True
METIS_URL = 'https://localhost:3000/'

logger.info('Trading enabled......' + str(trades_allowed))

app = Flask(__name__)

# Instantiate GDAX API
exchange = ccxt.gdax()
logger.debug('Loading exchange API keys.....')
exchange.apiKey = api_keys.EXCHANGE['apiKey']
exchange.secret = api_keys.EXCHANGE['secret']
exchange.password = api_keys.EXCHANGE['passphrase']
logger.debug('Exchange API keys loaded successfully')

if sandbox and exchange.urls['test']:
    exchange.urls['api'] = exchange.urls['test']
    logger.info('Running in SANDBOX MODE')
else:
    logger.info('Running in PRODUCTION MODE')
logger.debug('Exchange API URL: ' + exchange.urls['api'])

# Check for bad exchange API keys early
try:
    exchange.fetch_balance()
# Handle bad keys
except ccxt.base.errors.AuthenticationError as e:
    raise InvalidUsage(str(e), status_code=403)


# Authorize requests before any
@app.before_request
def authenticate_token():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            response_obj = {
                'status': 'failure',
                'message': 'Bearer token malformed.'
            }
            return make_response(jsonify(response_obj)), 401
    else:
        auth_token = ''

    if auth_token:
        resp = decode_auth_token(auth_token)

        # If token is invalid, return invalid response, otherwise do nothing and move on
        if isinstance(resp, Response):
            return resp
    else:
        response_object = {
            'status': 'failure',
            'message': 'Provide a valid Bearer token. If you don\'t have one, authenticate against /login first.'
        }
        return make_response(jsonify(response_object)), 401


@app.route('/login')
def login():
    data = request.get_json()
    try:
        # Check if user is legit
        if check_user(data['user_id'], data['password']):

            # Issue token
            auth_token = encode_auth_token(data['user_id'])
            if auth_token:
                response_obj = {
                    'status': 'success',
                    'message': 'Successfully authenticated.',
                    'auth_token': auth_token
                }
                return make_response(jsonify(response_obj)), 200
            else:
                return Response('An error occurred issuing a token.', status=500)
        else:
            return Response('Invalid credentials.', status=401)

    except Exception as e:
        logger.error("     An error occurred issuing a token to an authenticated user: " + str(e))
        response_obj = {
            'status': 'error',
            'message': 'Please try again later.'
        }
        return make_response(jsonify(response_obj)), 500


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
def get_orders(symbol):
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
def get_closed_orders(symbol):
    if exchange.hasFetchClosedOrders:
        return json.dumps(exchange.fetch_closed_orders(symbol=symbol))
    else:
        raise InvalidUsage('Exchange does not support fetching closed orders', status_code=422)


# Place new order
@app.route('/order', methods=["POST"])
def make_order():
    data = request.get_json()

    if data.get('side'):
        symbol = data['symbol']
        logger.debug("   Symbol: " + symbol)
    else:
        raise InvalidUsage('Missing symbol parameter', status_code=400)

    if data.get('side'):
        side = data['side']
        logger.debug("   Side: " + side)
    else:
        raise InvalidUsage('Missing side parameter', status_code=400)

    if data.get('type'):
        order_type = data['type']
        logger.debug("   Order type: " + order_type)
    else:
        raise InvalidUsage('Missing type parameter', status_code=400)

    if data.get('amount'):
        amount = data['amount']
        logger.debug("   Amount: " + amount)
    else:
        raise InvalidUsage('Missing price parameter', status_code=400)

    if data.get('price'):
        price = data['price']
        logger.debug("   Price: " + price)
    else:
        price = None

    if order_type == "market":
        if side == "buy":
            return json.dumps(exchange.create_market_buy_order(symbol, amount))
        elif side == "sell":
            return json.dumps(exchange.create_market_sell_order(symbol, amount))
        else:
            raise InvalidUsage('Invalid order side', status_code=400)
    elif order_type == "limit":
        if not data.get('price'):
            raise InvalidUsage('Missing price parameter', status_code=400)

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


# Disable trading
@app.route('/disable', methods=["POST"])
def disable():
    global trades_allowed
    trades_allowed = False
    return Response("Trading disabled", status=200)


# Enable trading
@app.route('/enable', methods=["POST"])
def enable():
    global trades_allowed
    trades_allowed = True
    return Response("Trading enabled", status=200)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def encode_auth_token(user_id):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=30),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        logger.error("     An error occurred while signing a token: " + str(e))
        return Response('Signing error', status=500)


def decode_auth_token(token):
    try:
        payload = jwt.decode(token, app.config.get('SECRET_KEY'))
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return Response('Signature expired, please authenticate again.', status=401)
    except jwt.InvalidTokenError:
        return Response('Invalid token, please authenticate again.', status=401)


# TODO Add auth for Metis API
def check_user(user_id, password):
    metis_uri = METIS_URL + 'taurus-users/' + user_id
    response = requests.get(metis_uri)
    data = response.json()
    return pwd_context.verify(password, data['password'])


if __name__ == '__main__':
    app.run()

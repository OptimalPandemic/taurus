# Data Structure

## Candlesticks
Candlesticks are price arrays that show opening price, highest price, lowest price, closing price, and volume for a particular period.
Prices and volume are in units of the base currency (default is BTC).

```
[
    [
        1504541580000, // UTC timestamp in milliseconds, integer
        4235.4,        // (O)pen price, float
        4240.6,        // (H)ighest price, float
        4230.0,        // (L)owest price, float
        4230.7,        // (C)losing price, float
        37.72941911    // (V)olume (in terms of the base currency), float,
        'ETH/BTC'      // Symbol
    ]
]
```

## Trades
```
[
    {
        'id':			1							// integer id in database
        'info':         { ... },                    // the original decoded JSON as is
        'trade_id':     '12345-67890:09876/54321',  // string trade id
        'timestamp':    1502962946216,              // Unix timestamp in milliseconds
        'datetime':     '2017-08-17 12:42:48.000',  // ISO8601 datetime with milliseconds
        'symbol':       'ETH/BTC',                  // symbol
        'order_id':     '12345-67890:09876/54321',  // string order id or undefined/None/null
        'type':         'limit',                    // order type, 'market', 'limit' or undefined/None/null
        'side':         'buy',                      // direction of the trade, 'buy' or 'sell'
        'takerOrMaker': 'taker',                    // string, 'taker' or 'maker'
        'price':        0.06917684,                 // float price in quote currency
        'amount':       1.5,                        // amount of base currency
        'cost':         0.10376526,                 // total cost (including fees), `price * amount + fee`
        'fee_cost':     0.0015,                     // float
        'fee_currency': 'ETH',                      // usually base currency for buys, quote currency for sells
        'fee_rate':     0.002,                      // the fee rate (if available, will be negative if not)
    }
]
```

# Routes
This is a list of API endpoints for the Collector service.

### Get All Candlesticks

### Get Candlestick by Timestamp

### Get Candlesticks by Timestamp Range

### Get Candlesticks by Symbol

### Get Candlesticks by Symbol and Timestamp Range 

### Get All Trade History

### Get Trade by ID

### Get Trade by Timestamp

### Get Trades by Timestamp range

### Get Trades by Symbol

### Get Trades by Type
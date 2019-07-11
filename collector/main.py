import asyncio
import time
import mysql.connector
import ccxt
from concurrent import futures


from collector_pb2 import *
from collector_pb2_grpc import *
from navigator_pb2_grpc import *
from web_pb2_grpc import *


class Collector(CollectorServicer):

    db = mysql.connector.connect(   # TODO variable-ize this
        host="db",
        user="root",
        passwd="root",
        port=3306,
        use_pure=True,
        database="taurus"
    )

    channel_navigator = grpc.insecure_channel('localhost:8082')
    navigator_stub = NavigatorStub(channel_navigator)
    channel_web = grpc.insecure_channel('localhost:8080')
    web_stub = WebStub(channel_web)

    async def manage_database(self):
        period = 1800  # 30 minutes
        num_periods = 25
        data_age = period * num_periods

        exchange = ccxt.poloniex()
        symbols = [
            'ETH/BTC',
            'BCH/BTC'
        ]

        # Check if database is empty or stale

        cursor = self.db.cursor(prepared=True)
        query = """SELECT IFNULL(MAX(time), -1) FROM candlesticks"""
        cursor.execute(query)
        timestamp_highest = int(cursor.fetchone()[0])
        to_inform = CandlestickSet()

        if timestamp_highest == -1:
            # Database is empty
            for symbol in symbols:
                since = int(time.time() - data_age)
                candlesticks = Collector.poll_candlesticks(exchange, symbols, since)
                for c in candlesticks:
                    self.write_candlestick(c[0]/1000, c[1], c[2], c[3], c[4], c[5], symbol, cursor)
                    to_inform = to_inform.CandlestickSet.extend([Candlestick(c[0]/1000, c[1], c[2], c[3], c[4], c[5], symbol)])  # TODO fix

        elif timestamp_highest < int(time.time() - period):
            # Database is stale (older than 30m)
            # if data is older than data_age, only pull data since then
            # otherwise pull all data since most recent stored data
            since = time.time() - data_age if timestamp_highest < time.time() - data_age else time.time() - period
            for symbol in symbols:
                candlesticks = Collector.poll_candlesticks(exchange, symbols, int(since))
                for c in candlesticks:
                    self.write_candlestick(c[0]/1000, c[1], c[2], c[3], c[4], c[5], symbol, cursor)
                    to_inform = to_inform.CandlestickSet.extend([Candlestick(c[0]/1000, c[1], c[2], c[3], c[4], c[5], symbol)])

        # Give candlesticks to navigator and web  TODO do something smart here to prevent duplicate data in navigator
        # response_navigator = self.navigator_stub.PutCandlesticks(candlesticks=to_inform)
        # response_web = self.web_stub.InformCandlesticks(candlesticks=to_inform)

        # Do poll to database every 15 minutes and write to db and give to navigator
        while True:
            for symbol in symbols:
                to_inform = CandlestickSet()
                candlesticks = Collector.poll_candlesticks(exchange, symbols, int(time.time()))
                for c in candlesticks:
                    self.write_candlestick(c[0]/1000, c[1], c[2], c[3], c[4], c[5], symbol, cursor)
                    to_inform = to_inform.CandlestickSet.extend([Candlestick(c[0]/1000, c[1], c[2], c[3], c[4], c[5], symbol)])
            response_navigator = self.navigator_stub.PutCandlesticks(candlesticks=to_inform)
            response_web = self.web_stub.InformCandlesticks(candlesticks=to_inform)
            await asyncio.sleep(period / 2)

    def GetCandlestick(self, request, context):
        cursor = self.db.cursor(prepared=True)
        if request.timestamp_start is not None and request.symbol is not None \
                and request.symbol.match("([A-Z]){3}\/([A-Z]){3}"):
            if request.timestamp_end is not None and request.timestamp_start < request.timestamp_end:
                # Request is for candlestick range and should use GetCandlesticks
                return self.GetCandlesticks(request, context)

            # Else request is asking for specific candlestick in time
            query = """SELECT * from candlesticks WHERE time=%s AND symbol=%s"""
            timestamp = request.timestamp_start
            symbol = request.symbol
            cursor.execute(query, (timestamp, symbol))
            candlestick = cursor.fetchone()
            cursor.close()

            return Candlestick(
                timestamp=candlestick[1],
                open=candlestick[2],
                high=candlestick[3],
                low=candlestick[4],
                close=candlestick[5],
                volume=candlestick[6],
                symbol=candlestick[7],
            )

        else:
            # Request is malformed
            context.set_details("Timestamp is missing, symbol is missing, or symbol is malformed.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return Candlestick()

    def GetCandlesticks(self, request, context):
        cursor = self.db.cursor(prepared=True)
        if request.timestamp_start is not None and request.symbol is not None \
                and request.symbol.match("([A-Z]){3}\/([A-Z]){3}"):
            if request.timestamp_end is not None and request.timestamp_start < request.timestamp_end:
                # Request is for candlestick range
                query = """SELECT * from candlesticks WHERE time BETWEEN from_unixtime(%s) AND from_unixtime(%s) AND symbol=%s"""
                time_start = request.timestamp_start
                time_end = request.timestamp_end
                symbol = request.symbol
                cursor.execute(query, (time_start, time_end, symbol))
                candlesticks = cursor.fetchall()
                cursor.close()

                # Add all pulled candlesticks to candlestick set
                candlestick_set = CandlestickSet

                for candlestick in candlesticks:
                    candlestick_set.add(Candlestick(
                        timestamp=candlestick[1],
                        open=candlestick[2],
                        high=candlestick[3],
                        low=candlestick[4],
                        close=candlestick[5],
                        volume=candlestick[6],
                        symbol=candlestick[7]
                    ))
                return candlestick_set

            # Else request is asking for specific candlestick in time and should use GetCandlestick
            return self.GetCandlestick(request, context)

        else:
            # Request is malformed
            context.set_details("Timestamp is missing, symbol is missing, or symbol is malformed.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return CandlestickSet()

    def GetTrade(self, request, context):
        cursor = self.db.cursor(prepared=True)
        if request.timestamp_start is not None and request.symbol is not None \
                and request.symbol.match("([A-Z]){3}\/([A-Z]){3}"):
            if request.timestamp_end is not None and request.timestamp_start < request.timestamp_end:
                # Request is for trade range and should use GetTrades
                return self.GetTrades(request, context)

            # Else request is asking for specific candlestick in time
            query = """SELECT * from trades WHERE time=%s AND symbol=%s"""
            timestamp = request.timestamp_start
            symbol = request.symbol
            cursor.execute(query, (timestamp, symbol))
            trade = cursor.fetchone()
            cursor.close()

            return Trade(
                info=trade[1],
                id=trade[2],
                timestamp=trade[3],
                datetime=trade[4],
                symbol=trade[5],
                order=trade[6],
                type=trade[7],
                side=trade[8],
                takerOrMaker=trade[9],
                price=trade[10],
                amount=trade[11],
                cost=trade[12],
                fee_cost=trade[13],
                fee_currency=trade[14],
                fee_rate=trade[15]
            )

        else:
            # Request is malformed
            context.set_details("Timestamp is missing, symbol is missing, or symbol is malformed.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return Trade()

    def GetTrades(self, request, context):
        cursor = self.db.cursor(prepared=True)
        if request.timestamp_start is not None and request.symbol is not None \
                and request.symbol.match("([A-Z]){3}\/([A-Z]){3}"):
            if request.timestamp_end is not None and request.timestamp_start < request.timestamp_end:
                # Request is for candlestick range
                query = """SELECT * from trades WHERE time BETWEEN from_unixtime(%s) AND from_unixtime(%s) AND symbol=%s"""
                time_start = request.timestamp_start
                time_end = request.timestamp_end
                symbol = request.symbol
                cursor.execute(query, (time_start, time_end, symbol))
                trades = cursor.fetchall()
                cursor.close()

                # Add all pulled trades to trade set
                trade_set = TradeSet

                for trade in trades:
                    trade_set.add(Trade(
                        info=trade[1],
                        id=trade[2],
                        timestamp=trade[3],
                        datetime=trade[4],
                        symbol=trade[5],
                        order=trade[6],
                        type=trade[7],
                        side=trade[8],
                        takerOrMaker=trade[9],
                        price=trade[10],
                        amount=trade[11],
                        cost=trade[12],
                        fee_cost=trade[13],
                        fee_currency=trade[14],
                        fee_rate=trade[15]
                    ))
                return trade_set

            # Else request is asking for specific trade in time and should use GetTrade
            return self.GetTrade(request, context)

        else:
            # Request is malformed
            context.set_details("Timestamp is missing, symbol is missing, or symbol is malformed.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return TradeSet()

    """
    Polls exchanges for candlestick data asynchronously.
    
    :param exchange: exchange to pull data from
    :type exchange: CCXT object
    :param since: timestamp of the first candlestick to pull, -1 to continuously poll from now
    :param symbol: all currency symbols to pull data for
    :type str: e.g. 'BTC/USD'
    :type timestamp: unix timestamp
    :returns: candlesticks
    :type: array
    """
    @staticmethod
    def poll_candlesticks(exchange, symbols, since=-1):
        ret = []
        if exchange.has['fetchOHLCV'] and exchange.has['fetchOHLCV'] is not 'emulated':
            if since == -1:
                # Poll for data continuously
                while True:
                    for symbol in symbols:
                        time.sleep(exchange.rateLimit / 1000)
                        sticks = exchange.fetch_ohlcv(symbol, '30m')
                        for stick in sticks:
                            ret.append(stick)
            elif since != -1:
                # Pull data for timespan
                for symbol in symbols:
                    time.sleep(exchange.rateLimit / 1000)
                    sticks = exchange.fetch_ohlcv(symbol, '30m', since*1000)
                    for stick in sticks:
                        ret.append(stick)
            else:
                raise AssertionError
            return ret
        else:
            print('Exchange', exchange, 'does not support candlesticks! Failing loudly.')
            raise Exception

    """
    Writes candlestick to database, and leaves cursor open.
    
    :param cursor: MySQL database cursor
    :type object: from mysql.connect 
    """
    def write_candlestick(self, time, open, high, low, close, volume, symbol, cursor):
        query = """INSERT INTO candlesticks(time, open, high, low, close, volume, symbol) VALUES(%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (time, open, high, low, close, volume, symbol))
        self.db.commit()


async def main():
    c = Collector()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_CollectorServicer_to_server(c, server)
    server.add_insecure_port('[::]:50051')
    await server.start()  # Wait for gRPC messages
    await c.manage_database()  # Start polling

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())


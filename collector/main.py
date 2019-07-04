import grpc
import mysql.connector
import ccxt
import time

from collector import collector_pb2_grpc, collector_pb2


def main():
    candlestick = Collector.poll_candlesticks()


class Collector(collector_pb2_grpc.CollectorServicer):
    exchange = ccxt.binance()

    db = mysql.connector.connect(   # TODO variable-ize this
        host="localhost",
        user="root",
        passwd="root"
    )

    cursor = db.cursor(prepared=True)

    def GetCandlestick(self, request, context):
        if request.timestamp_start is not None and request.symbol is not None \
                and request.symbol.match("([A-Z]){3}\/([A-Z]){3}"):
            if request.timestamp_end is not None and request.timestamp_start < request.timestamp_end:
                # Request is for candlestick range and should use GetCandlesticks
                return self.GetCandlesticks(request, context)

            # Else request is asking for specific candlestick in time
            query = """SELECT * from candlesticks WHERE time=%s AND symbol=%s"""
            timestamp = request.timestamp_start
            symbol = request.symbol
            self.cursor.execute(query, (timestamp, symbol))
            candlestick = self.cursor.fetchone()
            self.cursor.close()

            return collector_pb2.Candlestick(
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
            return collector_pb2.Candlestick()

    def GetCandlesticks(self, request, context):
        if request.timestamp_start is not None and request.symbol is not None \
                and request.symbol.match("([A-Z]){3}\/([A-Z]){3}"):
            if request.timestamp_end is not None and request.timestamp_start < request.timestamp_end:
                # Request is for candlestick range
                query = """SELECT * from candlesticks WHERE time BETWEEN from_unixtime(%s) AND from_unixtime(%s) AND symbol=%s"""
                time_start = request.timestamp_start
                time_end = request.timestamp_end
                symbol = request.symbol
                self.cursor.execute(query, (time_start, time_end, symbol))
                candlesticks = self.cursor.fetchall()
                self.cursor.close()

                # Add all pulled candlesticks to candlestick set
                candlestick_set = collector_pb2.CandlestickSet

                for candlestick in candlesticks:
                    candlestick_set.add(collector_pb2.Candlestick(
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
            return collector_pb2.CandlestickSet()

    def GetTrade(self, request, context):
        if request.timestamp_start is not None and request.symbol is not None \
                and request.symbol.match("([A-Z]){3}\/([A-Z]){3}"):
            if request.timestamp_end is not None and request.timestamp_start < request.timestamp_end:
                # Request is for trade range and should use GetTrades
                return self.GetTrades(request, context)

            # Else request is asking for specific candlestick in time
            query = """SELECT * from trades WHERE time=%s AND symbol=%s"""
            timestamp = request.timestamp_start
            symbol = request.symbol
            self.cursor.execute(query, (timestamp, symbol))
            trade = self.cursor.fetchone()
            self.cursor.close()

            return collector_pb2.Trade(
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
            return collector_pb2.Trade()

    def GetTrades(self, request, context):
        if request.timestamp_start is not None and request.symbol is not None \
                and request.symbol.match("([A-Z]){3}\/([A-Z]){3}"):
            if request.timestamp_end is not None and request.timestamp_start < request.timestamp_end:
                # Request is for candlestick range
                query = """SELECT * from trades WHERE time BETWEEN from_unixtime(%s) AND from_unixtime(%s) AND symbol=%s"""
                time_start = request.timestamp_start
                time_end = request.timestamp_end
                symbol = request.symbol
                self.cursor.execute(query, (time_start, time_end, symbol))
                trades = self.cursor.fetchall()
                self.cursor.close()

                # Add all pulled trades to trade set
                trade_set = collector_pb2.TradeSet

                for trade in trades:
                    trade_set.add(collector_pb2.Trade(
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
            return collector_pb2.TradeSet()

    @staticmethod
    async def poll_candlesticks(self, start_time=-1):
        if self.exchange.has['fetchOHLCV'] and start_time == -1:
            if start_time == -1:
                # Poll for data continuously
                while True:
                    for symbol in self.exchange.markets:
                        time.sleep(self.exchange.rateLimit / 1000)
                        yield await self.exchange.fetch_ohclv(symbol, '30m')  # Return to caller as polled
            elif start_time != -1:
                # Pull data for timespan
                for symbol in self.exchange.markets:
                    time.sleep(self.exchange.rateLimit / 1000)
                    yield await self.exchange.fetch_ohclv(symbol, '30m', start_time)
            else:
                raise Exception
        else:
            raise Exception     # TODO do something better here

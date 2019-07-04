import grpc
import mysql.connector
import re

from collector import collector_pb2_grpc, collector_pb2


class Collector(collector_pb2_grpc.CollectorServicer):

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
            query = """SELECT * from candlesticks WHERE time=%s"""
            timestamp = request.timestamp_start
            self.cursor.execute(query, timestamp)
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
                query = """SELECT * from candlesticks WHERE time BETWEEN from_unixtime(%s) AND from_unixtime(%s)"""
                time_start = request.timestamp_start
                time_end = request.timestamp_end
                self.cursor.execute(query, (time_start, time_end))
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
                        symbol=candlestick[7],
                    ))
                return candlestick_set

            # Else request is asking for specific candlestick in time and should use GetCandlestick
            return self.GetCandlestick(request, context)

        else:
            # Request is malformed
            context.set_details("Timestamp is missing, symbol is missing, or symbol is malformed.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return collector_pb2.Candlestick()

    def GetTrade(self, request, context):
        return collector_pb2.Trade()

    def GetTrades(self, request, context):
        return collector_pb2.TradeSet()

import grpc

from collector import collector_pb2_grpc, collector_pb2


class Collector(collector_pb2_grpc.CollectorServicer):

    def GetCandlestick(self, request, context):
        return collector_pb2.Candlestick()

    def GetCandlesticks(self, request, context):
        return collector_pb2.CandlestickSet()

    def GetTrade(self, request, context):
        return collector_pb2.Trade()

    def GetTrades(self, request, context):
        return collector_pb2.TradeSet()

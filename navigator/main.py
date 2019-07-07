import asyncio
import grpc
from concurrent import futures
import tensorflow as tf

from navigator import navigator_pb2_grpc, navigator_pb2


class Navigator(navigator_pb2_grpc.NavigatorServicer):

    price_tensor = tf.constant([])

    def PutCandlesticks(self, request, context):
        # convert CandlestickSet to 2D array
        temp = []
        for c in request:
            temp.append([c.timestamp, c.open, c.high, c.low, c.close, c.volume, c.symbol])
        # convert array to tensor
        self.price_tensor = tf.convert_to_tensor(temp)
        return navigator_pb2.CandlestickReply(message='success')

    def InformPortfolio(self, request, context):


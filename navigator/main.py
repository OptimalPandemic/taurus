import asyncio
import time

import grpc
from concurrent import futures
import tensorflow as tf

from navigator_pb2 import *
from navigator_pb2_grpc import *


class Navigator(NavigatorServicer):

    price_tensor = tf.constant([])

    def PutCandlesticks(self, request, context):
        print("Candlesticks received!")
        print(request)

        # convert CandlestickSet to 2D array
        temp = []
        for c in request.candlesticks:
            temp.append([c.timestamp, c.open, c.high, c.low, c.close, c.volume, c.symbol])
        # convert array to tensor
        self.price_tensor = tf.convert_to_tensor(temp)
        return CandlestickReply(message='success')

    def InformPortfolio(self, request, context):
        return CandlestickReply()


async def main():
    n = Navigator()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_NavigatorServicer_to_server(n, server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()  # Wait for gRPC messages
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

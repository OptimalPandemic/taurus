import asyncio
import time

from concurrent import futures

from web_pb2 import *
from web_pb2_grpc import *


class Web(WebServicer):

    def GetConstraints(self, request, context):
        return ConstraintSet()

    def InformTrade(self, request, context):
        return InformReply

    def InformCandlesticks(self, request, context):
        return InformReply


async def main():
    w = Web()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_WebServicer_to_server(w, server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()  # Wait for gRPC messages
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())

grpc:
	python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=collector --grpc_python_out=collector protocol-buffers/collector.proto
	python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=navigator --grpc_python_out=navigator protocol-buffers/navigator.proto
	python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=trader --grpc_python_out=trader protocol-buffers/trader.proto
	python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=web --grpc_python_out=web protocol-buffers/web.proto
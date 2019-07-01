grpc:
	protoc -Iprotocol-buffers --python_out=protocol-buffers protocol-buffers/*.proto
	python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=protocol-buffers --grpc_python_out=protocol-buffers protocol-buffers/*.proto
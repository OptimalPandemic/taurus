all: grpc build start
.PHONY: all


grpc:
	$(info Make: Transpiling gRPC and protobuf configs....)
	@python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=collector --grpc_python_out=collector protocol-buffers/*.proto
	@python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=navigator --grpc_python_out=navigator protocol-buffers/*.proto
	@python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=web --grpc_python_out=web protocol-buffers/*.proto
	@python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=trader --grpc_python_out=trader protocol-buffers/*.proto

build:
	$(info Make: Building containers....)
	@docker-compose build --no-cache
	@make -s clean

start:
	$(info Make: Starting containers....)
	@docker-compose up -d

stop:
	$(info Make: Stopping containers....)
	@docker-compose stop

restart:
	$(info Make: Restarting containers....)
	@make -s stop
	@make -s start

clean:
	@docker system prune --volumes --force

rebuild:
	@make build
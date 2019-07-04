ifndef $(TAG)
@TAG=latest
endif

all: grpc build start
.PHONY: all


grpc:
	$(info Make: Transpiling gRPC and protobuf configs for collector....)
	@python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=collector --grpc_python_out=collector protocol-buffers/collector.proto
	$(info Make: Transpiling gRPC and protobuf configs for navigator....)
	@python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=navigator --grpc_python_out=navigator protocol-buffers/navigator.proto
	$(info Make: Transpiling gRPC and protobuf configs for trader....)
	@python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=trader --grpc_python_out=trader protocol-buffers/trader.proto
	$(info Make: Transpiling gRPC and protobuf configs for web....)
	@python3 -m grpc_tools.protoc -Iprotocol-buffers --python_out=web --grpc_python_out=web protocol-buffers/web.proto

build:
	$(info Make: Building containers....)
	@TAG=$(TAG) docker-compose build --no-cache
	@make -s clean

start:
	$(info Make: Starting containers....)
	@TAG=$(TAG) docker-compose up -d

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

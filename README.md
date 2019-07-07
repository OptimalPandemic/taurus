# Taurus
A cryptocurrency trading platform using deep reinforcement learning.

## Structure
Taurus is based on several microservices in a monorepo:
* The deep learning model that turns price data into trade decisions (/navigator)
* The trading system that executes and tracks trades (/trader)
* The data collection service that feeds data into the ML model (/collector)
* The web application for user control and monitoring (/web)

The microservices communicate via gRPC (https://grpc.io). The current version only supports being run on a single server, so no key exchange occurs between APIs.

## Prerequisites
This application requires protoc/protobuf, gRPC, Docker and Docker Compose to build.

## Usage
TBD

## Under Development
* RPC/messaging interfaces
* Data collection logic
* Trading logic
* Machine learning model & training
* Web interface
* Logging

## Credits
The reinforcement learning model for this project is based on a graduate paper from Zhengyao Jiang, Dixing Xu, and Jinjun Liang of Xi'an Jiaotong-Liverpool University in Suzhou, China.
https://arxiv.org/abs/1706.10059

This project uses the CCXT library (https://github.com/ccxt/ccxt) to interact with exchanges for data collection and trading.

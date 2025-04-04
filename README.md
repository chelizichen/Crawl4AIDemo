
## PROTO COMPILE

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/math.proto

https://pypi.tuna.tsinghua.edu.cn/simple/


## ERRORS

1. no module named grpc
    python -m pip install grpcio
2. no module named grpc_tools
    python -m pip install grpcio-tools
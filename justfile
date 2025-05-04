grpc_directory := "thesis/schemas/generated"

gen_grpc:
    python -m grpc_tools.protoc -I protos/ --python_out={{grpc_directory}} --pyi_out={{grpc_directory}} --grpc_python_out={{grpc_directory}} protos/quota.proto

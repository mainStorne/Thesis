web_grpc := "web/src/grpc"
agent_grpc := "agent/src/grpc"

gen_grpc:
    uv run python -m grpc_tools.protoc -I protos/ --python_out={{web_grpc}} --pyi_out={{web_grpc}} --grpc_python_out={{web_grpc}} protos/quota.proto
    uv run python -m grpc_tools.protoc -I protos/ --python_out={{agent_grpc}} --pyi_out={{agent_grpc}} --grpc_python_out={{agent_grpc}} protos/quota.proto


migrate:
    cd /workspace/web && alembic revision --autogenerate && alembic upgrade head

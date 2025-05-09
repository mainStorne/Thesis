from dataclasses import dataclass

from grpc.aio import Channel


@dataclass
class State:
    grpc_channel: Channel


state = State(None)

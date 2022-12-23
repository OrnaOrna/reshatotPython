import socket


class Group:

    def __init__(self, name: str, group_id: int, password: str):
        self.name: str = name
        self.id: int = group_id
        self.password: str = password
        self.member_connections: list[socket.socket] = []
        self.participant_names: list[str] = []

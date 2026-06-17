from dataclasses import dataclass
from typing import Dict

@dataclass
class Message:
    sender: str
    receiver: str
    msg_type: str
    payload: Dict
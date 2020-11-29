import time
import uuid
from decimal import Decimal
from dataclasses import dataclass


class OrderAction:
    ASK = 1
    BID = 2


@dataclass
class Order:
    price: Decimal
    volume: Decimal
    owner_id: str
    status: str
    id: uuid.uuid4 = uuid.uuid4()
    timestamp: int = time.time_ns()


class OrderList:
    pass


class OrderBook:
    pass

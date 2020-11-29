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

    def __init__(self):
        pass

    @property
    def market_data(self):
        pass

    def add_order(self, order: Order):
        pass

    def remove_order(self, order_id):
        pass

    def get_order_by(self, order_id):
        pass

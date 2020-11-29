import time
import uuid
from decimal import Decimal
from collections import UserList, OrderedDict, defaultdict
from dataclasses import dataclass


class OrderedDefaultDict(OrderedDict, defaultdict):
    def __init__(self, default_factory=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory


class OrderAction:
    ASK = 1
    BID = 2


class OrderStatus:
    INIT = "init"
    OPEN = "open"
    TRADE = "trade"
    CLOSE = "close"


@dataclass
class Order:
    price: Decimal
    volume: Decimal
    type: str
    owner_id: str
    __status: str = 'init'
    __id: str = uuid.uuid4()
    __timestamp: int = time.time_ns()

    @property
    def id(self):
        return self.__id

    @property
    def ts(self):
        return self.__timestamp

    @property
    def status(self):
        return self.__status

    def __post_init__(self):
        if not isinstance(self.price, Decimal) or not isinstance(self.volume, Decimal):
            raise Exception("Price and Volume should be Decimal instance")
        if self.price <= 0:
            raise Exception(f"Try to create invalid order. Set invalid {self.price=}")
        if self.volume <= 0:
            raise Exception(f"Try to create invalid order. Set invalid {self.volume=}")


class OrderList(UserList):
    # self.data -> list .... TODO: change to another more faster class.
    #  Need push and pop with O(1) and slow insert sorted by timestamp

    def __init__(self):
        super().__init__(self)
        self.price = None
        self.quantity = 0

    def _process_order(self, order: Order):
        if not isinstance(order, Order):
            raise Exception
        if self.price is None and self.quantity == 0:
            self.price = order.price
        self.quantity += order.volume

    def append(self, val):
        self._process_order(val)
        self.insert(len(self.data), val)

    def del_order(self, order_id):
        if order_id in self.data:
            return

        raise Exception("Order not exist in this orderList")

    # def __delitem__(self, ii):
    #     """Delete an item"""
    #     del self._list[ii]




class OrderBook:

    def __init__(self):
        self.asks = OrderedDefaultDict(OrderList)
        self.bids = OrderedDefaultDict(OrderList)

    @property
    def market_data(self):
        pass

    def add_order(self, order: Order):
        pass

    def remove_order(self, order_id):
        pass

    def get_order_by(self, order_id):
        pass



if __name__ == "__main__":
    Order(Decimal("-1"), Decimal("-2"), 'qwe', 'qwe1')
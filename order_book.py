import time
import uuid
from decimal import Decimal
from collections import UserList
from dataclasses import dataclass, field

from sortedcontainers import SortedDict


class SortedDefaultDict(SortedDict):
    def __init__(self, default_factory=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __missing__(self, key):
        result = self[key] = self.default_factory()
        return result


class OrderType:
    ASK = "ask"
    BID = "bid"


class OrderStatus:
    INIT = "init"
    OPEN = "open"
    TRADE = "trade"
    CLOSE = "close"


# @total_ordering
@dataclass
class Order:
    trading_pair: str
    price: Decimal
    volume: Decimal
    type: str
    owner_id: str
    __status: str = OrderStatus.INIT
    __curr_volume: Decimal = None
    __id: str = field(default_factory=lambda: str(uuid.uuid4()))
    __timestamp: int = field(default_factory=time.time_ns)

    def __post_init__(self):
        if not isinstance(self.price, Decimal) or not isinstance(self.volume, Decimal):
            raise Exception("Price and Volume should be Decimal instance")
        if self.price <= 0:
            raise Exception(f"Try to create invalid order. Set invalid {self.price=}")
        if self.volume <= 0:
            raise Exception(f"Try to create invalid order. Set invalid {self.volume=}")

        self.__curr_volume = self.volume

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.id
        if isinstance(other, self.__class__):
            return self.id == other.id
        return False

    @property
    def id(self):
        return self.__id

    @property
    def ts(self):
        return self.__timestamp

    @property
    def status(self):
        return self.__status

    def early_than(self, order: "Order"):
        return self.ts < order.ts


class OrderList(UserList):
    # self.data -> list .... TODO: change to another more faster class.
    #  Need push and pop with O(1) and slow insertion by ordered timestamp like queue

    def __init__(self):
        super().__init__(self)
        self.price = None
        self.quantity = 0

    def _process_order(self, order: Order):
        if self.price is None and self.quantity == 0:
            self.price = order.price
        if self.price == order.price:
            self.quantity += order.volume
            return

        raise Exception

    def _remove_process(self, order: Order):
        if self.price == order.price \
                and self.quantity > 0 \
                and self.quantity > order.volume:
            self.quantity -= order.volume
            return

        raise Exception

    def add_order(self, val):

        self._process_order(val)
        self.insert(0, val)
        # self.insert(len(self.data), val)

    def del_order(self, order_id):
        if order_id in self.data:
            idx = self.data.index(order_id)
            order = self.data[idx]
            self._remove_process(order)
            del self.data[idx]
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
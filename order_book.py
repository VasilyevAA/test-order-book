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


# Simplest way, Its use some model from Django\FastApi with validating method =)
@dataclass(frozen=True)
class Order:
    trading_pair: str
    price: Decimal
    volume: Decimal
    type: str
    owner_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ts: int = field(default_factory=time.time_ns)

    def __post_init__(self):
        if not isinstance(self.price, Decimal) or not isinstance(self.volume, Decimal):
            raise Exception("Price and Volume should be Decimal instance")
        quntil = Decimal("1.00000000")
        if self.price != self.price.quantize(quntil) or self.volume != self.volume.quantize(quntil):
            raise Exception("Max precisions for decimals = 8")
        if self.price <= 0:
            raise Exception(f"Try to create invalid order. Set invalid {self.price=}")
        if self.volume <= 0:
            raise Exception(f"Try to create invalid order. Set invalid {self.volume=}")

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.id
        if isinstance(other, self.__class__):
            return self.id == other.id
        return False

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

        raise Exception(f"Invalid price or state for this order container. Curr data: {self.price=}, {self.quantity=}")

    def _remove_process(self, order: Order):
        if self.price == order.price \
                and self.quantity > 0 \
                and self.quantity > order.volume:
            self.quantity -= order.volume
            return

        raise Exception("Order not exist in this container")

    def add_order(self, val):
        self._process_order(val)
        # self.insert(0, val)
        self.insert(len(self.data), val)

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

    def __init__(self, trading_pair: str, asks_count=10, bids_count=10):
        self.asks = SortedDefaultDict(OrderList)  # TODO: should be reversed
        self.bids = SortedDefaultDict(OrderList)
        self.orders_meta = dict()
        self.trading_pair = trading_pair
        self.asks_count = asks_count
        self.bids_count = bids_count

    def __to_market_table(self, asks_or_bids, count_of_items):
        count_of_items = count_of_items if len(asks_or_bids) > count_of_items else len(asks_or_bids)
        data = [asks_or_bids.peekitem(i) for i in range(count_of_items)]
        return {str(k): str(v.quantity) for k, v in data}

    def _check_order_exist_and_get_meta(self, order_id):
        if order_id in self.orders_meta:
            return None
        KeyError(f"Not exist entity {order_id=}")

    @property
    def market_data(self):
        #  TODO: Maybe i should use event-base implementation with mutex for good speed and support clearly snapshot,
        #   but it so long way for implementation.
        #   (support mutex in orderList layer(adding\remove)+ global mutex for orderBook layer)

        return {
            "asks": self.__to_market_table(self.asks, self.asks_count),
            "bids": self.__to_market_table(self.bids, self.bids_count),
        }

    def add_order(self, order: Order):
        if not isinstance(order, Order) and order.trading_pair == self.trading_pair:
            raise Exception
        if order.id in self.orders_meta:
            raise Exception("Order exist in this OrderBook")
        if order.type == OrderType.ASK:
            self.asks[order.price].add_order(order)
        elif order.type == OrderType.BID:
            self.bids[order.price].add_order(order)
        else:
            raise Exception(f"Not supported {order.type=}")
        self.orders_meta[order.id] = (order.price, order.type)

    def __find_order_list_with_specific_order(self, order_id, remove_from_list) -> OrderList:
        self._check_order_exist_and_get_meta(order_id)
        if remove_from_list:
            price, type_ = self.orders_meta.pop(order_id)
        else:
            price, type_ = self.orders_meta[order_id]
        return self.asks[price] if type_ == OrderType.ASK else self.bids[price]

    def remove_order(self, order_id):
        order_list = self.__find_order_list_with_specific_order(order_id, remove_from_list=True)
        order_list.del_order(order_id)

    def get_order_by(self, order_id):
        order_list = self.__find_order_list_with_specific_order(order_id, remove_from_list=False)
        return [i for i in order_list if order_id == i][0]


if __name__ == "__main__":
    from random import randint, choice
    from hypothesis import given, strategies as st

    qwe = SortedDefaultDict(list)
    qwe[4].append(1)
    qwe[2].append(2)
    qwe[3].append(2)
    qwe[1].append(2)
    qwe[5].append(2)
    print(qwe)

    order_book = OrderBook('BTC_USD')
    ord = Order('BTC_USD', Decimal("2"), Decimal("22"), OrderType.ASK, 'qwe1')
    ord_2 = Order('BTC_USD', Decimal("2"), Decimal("22"), OrderType.BID, 'qwe1')

    order_book.add_order(ord)
    for i in range(30):
        ord = Order('BTC_USD', Decimal(str(randint(1, 5))), Decimal(str(randint(1, 20))), choice([OrderType.BID, OrderType.ASK]), 'qwe1')
        order_book.add_order(ord)
    print(order_book.market_data)
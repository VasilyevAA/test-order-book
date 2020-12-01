"""
Исходя из задания, проверяться непосредственно будет только класс OrderBook и его методы прописанные в рамках П.2
"""
import uuid
from decimal import Decimal
from collections import defaultdict
from random import choice, randint, uniform

import pytest
from hypothesis import given, strategies as st

from order_book import Order, OrderType, OrderBook


DEFAULT_TRADING_PAIR = "BTC_USD"


def get_rnd_decimal():
    return Decimal(str(uniform(0.00000001, 20))).quantize(Decimal("1.00000000"))


def generate_order_obj(**kwargs):
    kwargs.setdefault("trading_pair", DEFAULT_TRADING_PAIR)
    kwargs.setdefault("price", get_rnd_decimal())
    kwargs.setdefault("volume", get_rnd_decimal())
    kwargs.setdefault("type", choice([OrderType.ASK, OrderType.BID]))
    kwargs.setdefault("owner_id", str(uuid.uuid4()))
    return Order(**kwargs)


def params_by_order_type():
    return pytest.mark.parametrize('order_type', [OrderType.ASK, OrderType.BID], ids=['ASK', 'BID'])


def params_count_of_orders():
    return pytest.mark.parametrize('count_of_orders', [1, 5], ids=["one_order", "many_orders"])


class BaseOrderBookTest:

    def setup(self):
        self.order_book = OrderBook(DEFAULT_TRADING_PAIR)

    def __get_orders_from(self, bids_or_asks):
        all_orders = []
        for order_list in bids_or_asks.values():
            all_orders.extend(order_list)
        return all_orders

    def get_orders_from_bids(self):
        return self.__get_orders_from(self.order_book.bids)

    def get_orders_from_asks(self):
        return self.__get_orders_from(self.order_book.asks)


class TestAddOrderInOrderBook(BaseOrderBookTest):

    def test_positive_add_bid_order(self):
        ord = generate_order_obj(type=OrderType.BID)
        self.order_book.add_order(ord)
        assert self.order_book.bids
        assert not self.order_book.asks
        assert len(self.get_orders_from_bids()) == 1

    def test_positive_add_asc_order(self):
        ord = generate_order_obj(type=OrderType.ASK)
        self.order_book.add_order(ord)
        assert self.order_book.asks
        assert not self.order_book.bids
        assert len(self.get_orders_from_asks()) == 1

    def test_negative_add_same_order_twice(self):
        ord = generate_order_obj(type=OrderType.BID)
        self.order_book.add_order(ord)
        with pytest.raises(Exception) as e:
            self.order_book.add_order(ord)
        assert "Order exist in" in str(e.value)
        assert len(self.get_orders_from_bids()) == 1

    @params_by_order_type()
    def test_negative_add_order_with_invalid_trading_pair_with_type(self, order_type):
        ord = generate_order_obj(type=order_type, trading_pair=st.text(min_size=1, max_size=5).example())
        with pytest.raises(Exception) as e:
            self.order_book.add_order(ord)
        assert "not supported trading pair" in str(e.value)
        assert not self.order_book.asks
        assert not self.order_book.bids

    def test_negative_add_order_with_invalid_type(self):
        ord = generate_order_obj(type=st.text(max_size=5).example())
        with pytest.raises(Exception) as e:
            self.order_book.add_order(ord)
        assert "Not supported order.type" in str(e.value)
        assert not self.order_book.asks
        assert not self.order_book.bids


class TestRemoveOrderFromOrderBook(BaseOrderBookTest):

    @params_by_order_type()
    def test_positive_delete_order_with_type(self, order_type):
        ord = generate_order_obj(type=order_type)
        self.order_book.add_order(ord)
        self.order_book.remove_order(ord.id)
        assert not self.get_orders_from_bids()
        assert not self.get_orders_from_asks()

    @params_by_order_type()
    def test_negative_delete_exist_order_twice_with_type(self, order_type):
        ord = generate_order_obj(type=order_type)
        self.order_book.add_order(ord)
        self.order_book.remove_order(ord.id)
        with pytest.raises(Exception) as e:
            self.order_book.remove_order(ord.id)
        assert "Not exist order_id=" in str(e.value)
        assert not self.get_orders_from_bids()
        assert not self.get_orders_from_asks()

    def test_negative_delete_not_exist_order(self):
        ord = generate_order_obj()
        with pytest.raises(Exception) as e:
            self.order_book.remove_order(ord.id)
        assert "Not exist order_id=" in str(e.value)
        assert not self.get_orders_from_bids()
        assert not self.get_orders_from_asks()

    @given(invalid_id=st.text(max_size=5))
    def test_negative_delete_order_by_invalid_data(self, invalid_id):
        with pytest.raises(Exception) as e:
            self.order_book.remove_order(invalid_id)
        assert "Not exist order_id=" in str(e.value)


class TestGetOrderFromOrderBook(BaseOrderBookTest):

    def test_positive_get_exist_bid_order(self):
        ord = generate_order_obj(type=OrderType.BID)
        self.order_book.add_order(ord)
        actual_order = self.order_book.get_order_by(ord.id)
        assert actual_order is ord

    def test_positive_get_exist_ask_order(self):
        ord = generate_order_obj(type=OrderType.ASK)
        self.order_book.add_order(ord)
        actual_order = self.order_book.get_order_by(ord.id)
        assert actual_order is ord

    @params_by_order_type()
    def test_negative_get_removed_order_with_type(self, order_type):
        ord = generate_order_obj(type=order_type)
        self.order_book.add_order(ord)
        self.order_book.remove_order(ord.id)
        with pytest.raises(Exception) as e:
            self.order_book.get_order_by(ord.id)
        assert "Not exist order_id=" in str(e.value)
        assert not self.get_orders_from_bids()
        assert not self.get_orders_from_asks()

    def test_negative_not_exist_order(self):
        ord = generate_order_obj()
        with pytest.raises(Exception) as e:
            self.order_book.get_order_by(ord.id)
        assert "Not exist order_id=" in str(e.value)


class TestGetMarketDataFromOrderBook(BaseOrderBookTest):

    def aggregate_orders(self, orders):
        data = defaultdict(int)
        for i in orders:
            data[i.price] += i.volume
        return [{"price": str(price), "quantity": str(data[price])} for price in sorted(data.keys())]

    def expected_market_data(self, bids=None, asks=None):
        return {
            "asks": asks or [],
            "bids": bids or [],
        }

    @params_count_of_orders()
    def test_positive_market_data_with_bids(self, count_of_orders):
        orders = []
        price = st.decimals("1", "10", places=8).example()
        for _ in range(count_of_orders):
            ord = generate_order_obj(price=price, type=OrderType.BID)
            self.order_book.add_order(ord)
            orders.append(ord)
        expected_market_data = self.expected_market_data(bids=self.aggregate_orders(orders))
        assert self.order_book.market_data == expected_market_data
        assert len(self.get_orders_from_bids()) == count_of_orders

    @params_count_of_orders()
    def test_positive_market_data_with_asks(self, count_of_orders):
        price = st.decimals("1", "10", places=8).example()
        orders = [generate_order_obj(price=price, type=OrderType.ASK) for _ in range(count_of_orders)]
        for ord in orders:
            self.order_book.add_order(ord)
        expected_market_data = self.expected_market_data(asks=self.aggregate_orders(orders))
        assert self.order_book.market_data == expected_market_data
        assert len(self.get_orders_from_asks()) == count_of_orders

    def test_positive_market_data_with_a_lot_of_different_bid_prices(self):
        orders = [generate_order_obj(type=OrderType.BID) for _ in range(10)]
        for ord in orders:
            self.order_book.add_order(ord)
        expected_market_data = self.expected_market_data(bids=self.aggregate_orders(orders))
        assert self.order_book.market_data == expected_market_data
        assert len(self.get_orders_from_bids()) == 10

    def test_positive_market_data_with_a_lot_of_different_ask_prices(self):
        orders = [generate_order_obj(type=OrderType.ASK) for _ in range(10)]
        for ord in orders:
            self.order_book.add_order(ord)
        expected_market_data = self.expected_market_data(asks=self.aggregate_orders(orders))
        assert self.order_book.market_data == expected_market_data
        assert len(self.get_orders_from_asks()) == 10

    @params_count_of_orders()
    def test_positive_market_data_with_bids_and_asks(self, count_of_orders):
        bid_orders = [generate_order_obj(type=OrderType.BID) for _ in range(count_of_orders)]
        ask_orders = [generate_order_obj(type=OrderType.ASK) for _ in range(count_of_orders)]
        for b_ord in bid_orders:
            self.order_book.add_order(b_ord)
        for a_ord in ask_orders:
            self.order_book.add_order(a_ord)
        expected_market_data = self.expected_market_data(
            bids=self.aggregate_orders(bid_orders), asks=self.aggregate_orders(ask_orders)
        )
        assert self.order_book.market_data == expected_market_data
        assert len(self.get_orders_from_bids()) == count_of_orders
        assert len(self.get_orders_from_asks()) == count_of_orders

    @params_by_order_type()
    def test_positive_remove_order_check_market_data_empty_lists(self, order_type):
        ord = generate_order_obj(type=order_type)
        self.order_book.add_order(ord)
        self.order_book.remove_order(ord.id)
        expected_market_data = self.expected_market_data()
        assert self.order_book.market_data == expected_market_data

    @params_by_order_type()
    def test_positive_remove_one_of_many_order_check_market_data_quantity_changes_by_order_type(self, order_type):
        orders = []
        for _ in range(10):
            ord = generate_order_obj(type=order_type)
            self.order_book.add_order(ord)
            orders.append(ord)
        deleted_order = orders.pop(randint(0, len(orders) - 1))
        self.order_book.remove_order(deleted_order.id)
        expected_market_data = self.expected_market_data(**{order_type + 's': self.aggregate_orders(orders)})
        assert self.order_book.market_data == expected_market_data

    def test_positive_market_data_without_data(self):
        expected_market_data = self.expected_market_data()
        assert self.order_book.market_data == expected_market_data

    def test_market_data_check_max_bid_print_size_limiter(self):
        order_book = OrderBook(DEFAULT_TRADING_PAIR, 2, 2)
        orders = [generate_order_obj(type=OrderType.BID) for _ in range(5)]
        for ord in orders:
            order_book.add_order(ord)
        old_market_data = order_book.market_data
        orders = sorted(orders, key=lambda i: i.price)
        delete_order = orders[0]
        order_book.remove_order(delete_order.id)
        assert order_book.market_data != old_market_data
        expected_data = self.expected_market_data(bids=self.aggregate_orders(orders[1:3]))
        assert order_book.market_data == expected_data

    def test_market_data_check_max_ask_print_size_limiter(self):
        order_book = OrderBook(DEFAULT_TRADING_PAIR, 2, 2)
        orders = [generate_order_obj(type=OrderType.ASK) for _ in range(5)]
        for ord in orders:
            order_book.add_order(ord)
        old_market_data = order_book.market_data
        orders = sorted(orders, key=lambda i: i.price)
        delete_order = orders[0]
        order_book.remove_order(delete_order.id)
        assert order_book.market_data != old_market_data
        expected_data = self.expected_market_data(asks=self.aggregate_orders(orders[1:3]))
        assert order_book.market_data == expected_data


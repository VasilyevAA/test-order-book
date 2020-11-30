"""
Исходя из задания, проверять непосредственно будет только класс OrderBook и его методы прописанные в рамках П.2
"""
from random import choice

import pytest
from hypothesis import given, strategies as st

from order_book import Order, OrderType, OrderBook


DEFAULT_TRADING_PAIR = "BTC_USD"


def generate_order_obj(**kwargs):
    kwargs.setdefault("trading_pair", DEFAULT_TRADING_PAIR)
    kwargs.setdefault("price", st.decimals("0.00000001", 20, places=8).example())
    kwargs.setdefault("volume", st.decimals("0.00000001", 20, places=8).example())
    kwargs.setdefault("type", choice([OrderType.ASK, OrderType.BID]))
    kwargs.setdefault("owner_id", st.uuids().example())
    return Order(**kwargs)


def params_by_order_type():
    return pytest.mark.parametrize('order_type', [OrderType.ASK, OrderType.BID], ids=['ASK', 'BID'])


class BaseOrderBookTest:

    def setup(self):
        self.order_book = OrderBook(DEFAULT_TRADING_PAIR)


class TestAddOrderInOrderBook(BaseOrderBookTest):

    def test_positive_add_bid_order(self):
        pass

    def test_positive_add_asc_order(self):
        pass

    def test_negative_add_same_order_twice(self):
        pass

    @params_by_order_type()
    def test_negative_add_order_with_invalid_trading_pair_with_type(self, order_type):
        pass

    @given(order_type=st.text(max_size=5))
    def test_negative_add_order_with_invalid_type(self):
        pass


class TestRemoveOrderFromOrderBook(BaseOrderBookTest):

    @params_by_order_type()
    def test_positive_delete_order_with_type(self, order_type):
        pass

    @params_by_order_type()
    def test_negative_delete_exist_order_twice_with_type(self, order_type):
        pass

    def test_negative_delete_not_exist_order(self):
        pass

    def test_negative_delete_order_by_invalid_data(self):
        pass


class TestGetOrderFromOrderBook(BaseOrderBookTest):

    @params_by_order_type()
    def test_positive_get_exist_order_with_type(self, order_type):
        pass

    @params_by_order_type()
    def test_negative_get_removed_order_with_type(self, order_type):
        pass

    def test_negative_not_exist_order(self):
        pass


class TestGetMarketData:

    def test_positive_market_data_with_bids_only(self):
        pass

    def test_positive_market_data_with_asks_only(self):
        pass

    def test_positive_market_data_with_a_lot_of_bid_prices(self):
        pass

    def test_positive_market_data_with_a_lot_of_ask_prices(self):
        pass

    def test_positive_market_data_with_bids_and_asks(self):
        pass

    def test_positive_remove_order_from_market_data(self):
        pass

    def test_positive_market_data_without_data(self):
        pass

    def test_market_data_max_print_size_limiter(self):
        pass

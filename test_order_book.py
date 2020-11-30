from random import choice

import pytest
from hypothesis import strategies as st

from order_book import Order, OrderType, OrderBook

DEFAULT_TRADING_PAIR = "BTC_USD"


def generate_order_obj(**kwargs):
    kwargs.setdefault("trading_pair", DEFAULT_TRADING_PAIR)
    kwargs.setdefault("price", st.decimals("0.00000001", 20, places=8).example())
    kwargs.setdefault("volume", st.decimals("0.00000001", 20, places=8).example())
    kwargs.setdefault("type", choice([OrderType.ASK, OrderType.BID]))
    kwargs.setdefault("owner_id", st.uuids().example())
    return Order(**kwargs)


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

    @pytest.mark.parametrize('invalid_map_data', [{}], ids=['different'])
    def test_negative_add_unprocessable_order(self):
        pass


class TestRemoveOrderFromOrderBook(BaseOrderBookTest):

    def test_positive_delete_order_with_type(self):
        pass

    def test_negative_delete_exist_order_twice_with_type(self):
        pass

    def test_negative_delete_not_exist_order_with_type(self):
        pass


class TestGetOrderFromOrderBook(BaseOrderBookTest):

    def test_positive_get_exist_order_with_type(self):
        pass

    def test_negative_get_removed_order_with_type(self):
        pass

    def test_negative_not_exist_order_with_type(self):
        pass


class TestGetMarketData:

    def test_positive_market_data_with_bids_only(self):
        pass

    def test_positive_market_data_with_asks_only(self):
        pass

    def test_positive_market_data_with_bids_and_asks(self):
        pass

    def test_positive_market_data_without_data(self):
        pass
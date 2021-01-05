import datetime
import json

import requests
from bs4 import BeautifulSoup

from richard_utils import RichardUtils


class Article:

    # TODO: Put path constants elsewhere ?
    PATH_ARTICLE = ["initialState", "pdp", "article"]
    PATH_ARTICLE_TITLE = PATH_ARTICLE + ["title"]
    PATH_ARTICLE_SUBTITLE = PATH_ARTICLE + ["subtitle"]
    PATH_ARTICLE_CONDITION = PATH_ARTICLE + ["condition_key"]
    PATH_ARTICLE_END_DATE = PATH_ARTICLE + ["end_date"]
    PATH_ARTICLE_IMAGES_URL = PATH_ARTICLE + ["images"]
    PATH_ARTICLE_DESCRIPTION = PATH_ARTICLE + ["description", "html"]

    PATH_SHIPPING_FEE = PATH_ARTICLE + ["shippingInfo", "cost"]

    PATH_OFFER = PATH_ARTICLE + ["offer"]
    PATH_OFFER_TYPE = PATH_OFFER + ["offer_type"]
    PATH_OFFER_PRICE = PATH_OFFER + ["price"]
    PATH_OFFER_REMAINING_TIME = PATH_OFFER + ["remaining_time"]

    PATH_BID = ["initialState", "pdp", "bid"]
    PATH_BID_NEXT_MIN_BID = PATH_BID + ["data", "next_minimum_bid"]
    PATH_BID_LIST = PATH_BID + ["data", "bids"]

    PATH_QUICK_ARTICLE_URL = ["url"]
    PATH_QUICK_ARTICLE_IS_PROMO = ["isPromo"]
    PATH_QUICK_ARTICLE_TITLE = ["title"]
    PATH_QUICK_ARTICLE_END_DATE = ["endDate"]
    PATH_QUICK_ARTICLE_HAS_AUCTION = ["hasAuction"]
    PATH_QUICK_ARTICLE_HAS_BUY_NOW = ["hasBuyNow"]
    PATH_QUICK_ARTICLE_NEXT_BID = ["bidPrice"]
    PATH_QUICK_ARTICLE_OFFER_PRICE = ["buyNowPrice"]
    PATH_QUICK_ARTICLE_SHIPPING_FEE = ["shipping", "cost"]
    PATH_QUICK_ARTICLE_CONDITION = ["conditionKey"]

    # TODO: meh...
    def __init__(self, link: str):
        self.link: str = link
        self.article_dict: dict = {}

    # TODO: oof...
    def quick_update(self, quick_article_dict: dict):
        title = RichardUtils.access_property(quick_article_dict, Article.PATH_QUICK_ARTICLE_TITLE)
        RichardUtils.set_property(self.article_dict, Article.PATH_ARTICLE_TITLE, title)

        end_date = RichardUtils.access_property(quick_article_dict, Article.PATH_QUICK_ARTICLE_END_DATE)
        RichardUtils.set_property(self.article_dict, Article.PATH_ARTICLE_END_DATE, end_date)

        condition = RichardUtils.access_property(quick_article_dict, Article.PATH_QUICK_ARTICLE_CONDITION)
        RichardUtils.set_property(self.article_dict, Article.PATH_ARTICLE_CONDITION, condition)

        shipping_fee = RichardUtils.access_property(quick_article_dict, Article.PATH_QUICK_ARTICLE_SHIPPING_FEE)
        RichardUtils.set_property(self.article_dict, Article.PATH_SHIPPING_FEE, shipping_fee)

        has_auction = RichardUtils.access_property(quick_article_dict, Article.PATH_QUICK_ARTICLE_HAS_AUCTION)
        RichardUtils.set_property(self.article_dict, Article.PATH_BID_NEXT_MIN_BID, None)
        if has_auction:
            next_bid = RichardUtils.access_property(quick_article_dict, Article.PATH_QUICK_ARTICLE_NEXT_BID)
            RichardUtils.set_property(self.article_dict, Article.PATH_BID_NEXT_MIN_BID, next_bid)

        has_buy_now = RichardUtils.access_property(quick_article_dict, Article.PATH_QUICK_ARTICLE_HAS_BUY_NOW)
        RichardUtils.set_property(self.article_dict, Article.PATH_OFFER_PRICE, None)
        if has_buy_now:
            offer_price = RichardUtils.access_property(quick_article_dict, Article.PATH_QUICK_ARTICLE_OFFER_PRICE)
            RichardUtils.set_property(self.article_dict, Article.PATH_OFFER_PRICE, offer_price)

        offer_type = "auction"
        if has_auction and has_buy_now:
            offer_type = "auction_with_buynow"
        elif has_buy_now:
            offer_type = "fixed_price"

        RichardUtils.set_property(self.article_dict, Article.PATH_OFFER_TYPE, offer_type)

    def update(self):
        page = requests.get(self.link)
        soup = BeautifulSoup(page.content, 'html.parser')
        soup_js = soup.find_all("script")[3]

        # Parsing JS object
        self.article_dict = json.loads(soup_js.contents[0][15:-1])

    @property
    def article_title(self) -> str:
        return RichardUtils.access_property(self.article_dict, Article.PATH_ARTICLE_TITLE)

    @property
    def article_subtitle(self) -> str:
        if RichardUtils.check_target_exists(self.article_dict, Article.PATH_ARTICLE_SUBTITLE):
            return RichardUtils.access_property(self.article_dict, Article.PATH_ARTICLE_SUBTITLE)
        return ""

    @property
    def article_condition(self) -> str:
        return RichardUtils.access_property(self.article_dict, Article.PATH_ARTICLE_CONDITION)

    @property
    def article_next_bid(self) -> float:
        next_bid = RichardUtils.access_property(self.article_dict, Article.PATH_BID_NEXT_MIN_BID)
        return float(next_bid) if next_bid is not None else None

    @property
    def article_fixed_price(self) -> float:
        offer_price = RichardUtils.access_property(self.article_dict, Article.PATH_OFFER_PRICE)
        return float(offer_price) if offer_price is not None else None

    @property
    def article_smart_price(self) -> float:
        if self.article_offer_type == "fixed_price":
            return self.article_fixed_price
        return self.article_next_bid

    @property
    def number_of_bid(self) -> int:
        return len(RichardUtils.access_property(self.article_dict, Article.PATH_BID_LIST))

    @property
    def article_offer_type(self) -> str:
        return RichardUtils.access_property(self.article_dict, Article.PATH_OFFER_TYPE)

    @property
    def article_end_date(self) -> datetime.datetime:
        datetime_str = RichardUtils.access_property(self.article_dict, Article.PATH_ARTICLE_END_DATE)
        datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
        return datetime_obj

    def __hash__(self):
        return hash(self.link)

    def __eq__(self, other):
        return self.link == other.link

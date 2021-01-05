import json

import requests
from bs4 import BeautifulSoup

from richard_utils import RichardUtils
from article import Article


class Richard:

    RICARDO_URL = "https://www.ricardo.ch"
    RICARDO_URL_SEARCH = "/en/s/{query}/?sort={sort_by}&next_offset={next_offset}"

    SEARCH_OFFSET_STEP = 59

    # TODO: Put path constants somewhere else ?
    PATH_RESULT = ["initialState", "srp"]
    PATH_ARTICLE_LIST = PATH_RESULT + ["results"]
    PATH_TOTAL_ARTICLES_COUNT = PATH_RESULT + ["totalArticlesCount"]

    PATH_ARTICLE_URL = ["url"]

    SORT_BY_RELEVANCE = "default"
    SORT_BY_CLOSE_TO_END = "close_to_end"
    SORT_BY_NEWEST = "newest"
    SORT_BY_MOST_BIDS = "most_bids"
    SORT_BY_CHEAPEST = "cheapest"
    SORT_BY_MOST_EXPENSIVE = "most_expensive"

    CONDITION_NEW = "new"
    CONDITION_LIKE_NEW = "like_new"
    CONDITION_USED = "used"
    CONDITION_DAMAGED = "damaged"
    CONDITION_ANTIQUE = "antique"

    FILTER_PARAM_CONDITION = "item_condition"
    FILTER_CONDITION_NEW_SEE_DESCRIPTION = "new_see_description"
    FILTER_CONDITION_NEW_ORIGINAL_PACKAGE = "new_original_package"
    FILTER_CONDITION_USED = "used"
    FILTER_CONDITION_ANTIQUE = "antik"
    FILTER_CONDITION_DAMAGED = "defekt"

    FILTER_PARAM_OFFER_TYPE = "offer_type"
    FILTER_OFFER_TYPE_AUCTION = "auction"
    FILTER_OFFER_TYPE_FIXED_PRICE = "fixed_price"

    FILTER_PARAM_PRICE_RANGE_MIN = "range_filters.price.min"
    FILTER_PARAM_PRICE_RANGE_MAX = "range_filters.price.max"

    def __init__(self):
        self.article_list: list = []

    # TODO: Really heavy function, could use some cleaning up
    def load_articles(self, query: str, quantity: int = 100, sort_by: str = SORT_BY_CLOSE_TO_END, filter_str: str = ""):
        result_dict = self.load_result_dict(Richard.build_search_url(query, sort_by, filter_string=filter_str))
        total_articles_count = RichardUtils.access_property(result_dict, Richard.PATH_TOTAL_ARTICLES_COUNT)

        loaded_articles = []
        current_offset = 0

        if total_articles_count < quantity:
            quantity = total_articles_count

        while quantity > len(loaded_articles):
            articles_list = RichardUtils.access_property(result_dict, Richard.PATH_ARTICLE_LIST)

            for article in articles_list:
                article_url = Richard.RICARDO_URL + RichardUtils.access_property(article, Richard.PATH_ARTICLE_URL)
                article_obj = Article(article_url)
                article_obj.quick_update(article)
                loaded_articles.append(article_obj)

                if quantity <= len(loaded_articles):
                    break

            current_offset += Richard.SEARCH_OFFSET_STEP
            result_dict = self.load_result_dict(Richard.build_search_url(query, sort_by, current_offset, filter_str))

        self.article_list.extend(loaded_articles)

    def update_articles(self):
        for article in self.article_list:
            article.update()

    def clear_articles(self):
        self.article_list.clear()

    def sort_list_by_end_date(self):
        self.article_list.sort(key=lambda x: x.article_end_date)

    # TODO: Clean up
    def sort_list_by_price(self):
        lmbd = lambda x: x.article_next_bid if x.article_offer_type != "fixed_price" else x.article_fixed_price
        self.article_list.sort(key=lmbd)

    @staticmethod
    def load_result_dict(search_url: str) -> dict:
        page = requests.get(search_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        soup_js = soup.find_all("script")[4]
        return json.loads(soup_js.contents[0][15:-1])

    # TODO: Function too heavy ?
    @staticmethod
    def build_filter_string(price_range: tuple = None, condition: list = None, offer_type: list = None):
        filter_list = []
        str_price_range = ""
        if price_range is not None and type(price_range) is tuple:
            str_price_range += Richard.FILTER_PARAM_PRICE_RANGE_MIN + "=" + str(min(price_range))
            str_price_range += "&"
            str_price_range += Richard.FILTER_PARAM_PRICE_RANGE_MAX + "=" + str(max(price_range))
            filter_list.append(str_price_range)

        str_condition = ""
        if condition is not None and len(condition) > 0:
            str_condition += Richard.FILTER_PARAM_CONDITION + "="
            str_condition += "%2C".join(condition)
            filter_list.append(str_condition)

        str_offer_type = ""
        if offer_type is not None and len(offer_type) > 0:
            str_offer_type += Richard.FILTER_PARAM_OFFER_TYPE + "="
            str_offer_type += "%2C".join(offer_type)
            filter_list.append(str_offer_type)

        return "&".join(filter_list)

    @staticmethod
    def build_search_url(query: str, sort_by: str, next_offset: int = 0, filter_string: str = "") -> str:
        return Richard.RICARDO_URL + Richard.RICARDO_URL_SEARCH.format(
            query=query,
            sort_by=sort_by,
            next_offset=next_offset
        ) + filter_string


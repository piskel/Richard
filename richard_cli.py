from rich.prompt import Prompt
from rich.table import Table
from richard import Richard
from article import Article


class RichardCLI:

    CONDITION_COLOR = {
        Richard.CONDITION_NEW: "green",
        Richard.CONDITION_LIKE_NEW: "green",
        Richard.CONDITION_USED: "yellow",
        Richard.CONDITION_DAMAGED: "red",
        Richard.CONDITION_ANTIQUE: "red"
    }

    def __init__(self):
        self.richard: Richard = Richard()
        self._table_articles: Table = Table()

    def init_table_articles(self):
        self._table_articles = Table(highlight=True)
        self._table_articles.add_column("Name")
        self._table_articles.add_column("Condition", justify="center")
        self._table_articles.add_column("Deadline")
        self._table_articles.add_column("Price")
        self._table_articles.add_column("Link")

    @staticmethod
    def prompt_search():
        return Prompt("Search")

    @property
    def table_articles(self) -> Table:
        return self._table_articles

    @table_articles.setter
    def table_articles(self, value: Table):
        self._table_articles = value

    def add_article_to_table_articles(self, article: Article) -> None:
        title = "[link={link}]{title}[/link]".format(title=article.article_title, link=article.link)

        condition = article.article_condition
        condition_color = RichardCLI.CONDITION_COLOR[condition] if condition in RichardCLI.CONDITION_COLOR else "red"
        condition = "[{color}]{condition}[/{color}]".format(condition=condition, color=condition_color)

        # deadline = str(article.article_end_date - datetime.now())
        deadline = str(article.article_end_date)

        price = "CHF {}".format(str(article.article_smart_price))

        self._table_articles.add_row(
            title,
            condition,
            deadline,
            price,
            article.link
        )


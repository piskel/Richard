import msvcrt

from rich.live import Live
from rich.panel import Panel
from richard import Richard
from richard_cli import RichardCLI


def get_input():
    input_chr1 = msvcrt.getch()
    result = list()
    result.append(input_chr1)
    if input_chr1 == b'\xe0':
        input_chr2 = msvcrt.getch()
        result.append(input_chr2)

    return result


r_cli = RichardCLI()
r_cli.init_table_articles()
pan = Panel(r_cli.table_articles)

filter_str = r_cli.richard.build_filter_string(
    price_range=(0.5, 50),
    condition=[Richard.FILTER_CONDITION_USED, Richard.FILTER_CONDITION_ANTIQUE],
    offer_type=[Richard.FILTER_OFFER_TYPE_AUCTION]
)
r_cli.richard.load_articles("seiko", 20, filter_str=filter_str)

# for article in r_cli.richard.article_list:
#     print(article.article_title)
#     print(article.article_next_bid)
#     print(article.article_fixed_price)
#     print(article.article_condition)
#     print(article.article_offer_type)
#     print(article.article_end_date)
#     print()


with Live(r_cli.table_articles, auto_refresh=True, transient=True) as live:
    for article in r_cli.richard.article_list:
        r_cli.add_article_to_table_articles(article)
        live.update(pan)

    cursor = 0
    run = True
    while run:
        r_cli.table_articles.rows[cursor].style = "reverse underline bold"
        live.update(pan)
        inputs = get_input()

        if len(inputs) == 1 and inputs[0] == b'\x03':
            exit()

        if len(inputs) > 1:
            r_cli.table_articles.rows[cursor].style = ""
            cursor += 1
            cursor %= len(r_cli.table_articles.rows)



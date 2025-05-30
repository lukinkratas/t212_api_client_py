import datetime
import os

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from t212 import APIClient

load_dotenv(override=True)

t212_client = APIClient(key=os.environ['T212_API_KEY'])


def test_create_report() -> None:
    to_dt = datetime.datetime.today()
    from_dt = to_dt - relativedelta(months=1)
    report = t212_client.create_report(from_dt, to_dt)

    assert report is not None
    assert report.get('reportId')


def test_list_reports() -> None:
    reports = t212_client.list_reports()

    assert reports is not None
    for key in (
        'reportId',
        'timeFrom',
        'timeTo',
        'dataIncluded',
        'status',
        'downloadLink',
    ):
        assert key in reports[0]


def test_get_portfolio() -> None:
    portfolio = t212_client.get_portfolio()

    assert portfolio is not None
    for key in (
        'ticker',
        'quantity',
        'averagePrice',
        'currentPrice',
        'ppl',
        'fxPpl',
        'initialFillDate',
        'frontend',
        'maxBuy',
        'maxSell',
        'pieQuantity',
    ):
        assert key in portfolio[0]


def test_get_transactions() -> None:
    # test all transactions
    transactions = t212_client.get_transactions()

    assert transactions is not None
    for key in ('type', 'amount', 'reference', 'dateTime'):
        assert key in transactions[0]

    # # test datetime from_dt - WIP
    # transactions_2025 = t212_client.get_transactions(
    #     datetime.datetime(2025, 5, 24, 14, 15, 22)
    # )
    # print(f'{transactions_2025=}')

    # # test str from_dt - WIP
    # transactions_2025 = t212_client.get_transactions('2025-05-24T14:15:22Z')
    # print(f'{transactions_2025=}')


def test_get_orders() -> None:
    # test all orders
    orders = t212_client.get_orders()

    assert orders is not None
    for key in (
        'type',
        'id',
        'fillId',
        'parentOrder',
        'ticker',
        'orderedQuantity',
        'filledQuantity',
        'limitPrice',
        'stopPrice',
        'timeValidity',
        'orderedValue',
        'filledValue',
        'executor',
        'dateModified',
        'dateExecuted',
        'dateCreated',
        'fillResult',
        'fillPrice',
        'fillCost',
        'taxes',
        'fillType',
        'status',
    ):
        assert key in orders[0]

    # # test ticker
    # aapl_orders = t212_client.get_orders('AAPL_US_EQ')

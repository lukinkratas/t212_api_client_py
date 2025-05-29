import datetime
import os
import time
from copy import copy
from typing import Any

import requests
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv


class APIClient(object):
    def __init__(self, key: str):
        self.key = key

    def _post_request_loop(
        self, url: str, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        while True:
            response = requests.post(
                url,
                headers={'Content-Type': 'application/json', 'Authorization': self.key},
                json=payload,
            )
            print(f'{response.status_code=}')

            # in case of 429 limited Try again
            if response.status_code != 429:
                break

            time.sleep(10)

        if response.status_code != 200:
            return None

        return response.json()

    def _get_request_loop(
        self, url: str, query: dict[str, str] | None = None
    ) -> Any | None:
        while True:
            response = requests.get(
                url, headers={'Authorization': self.key}, params=query
            )
            print(f'{response.status_code=}')

            # in case of 429 limited Try again
            if response.status_code != 429:
                break

            time.sleep(10)

        if response.status_code != 200:
            return None

        return response.json()

    def _get_request_items(
        self, base_url: str, query: dict[str, str] | None = None
    ) -> list[dict[str, str]] | None:
        items = []

        url = copy(base_url)

        while True:
            response_json = self._get_request_loop(url, query)

            if not response_json:
                return None

            if response_json.get('items'):
                items.extend(response_json['items'])

            if not response_json.get('nextPagePath'):
                break

            next_page_path = response_json['nextPagePath']

            print(next_page_path)
            # nextPagePath transactions: limit=20&cursor=245a5a7f-04b4-45d3-affa-72eb8ff6d62a&time=2025-05-07T00:03:03.896Z # noqa: E501
            # nextPagePath orders: /api/v0/equity/history/orders?cursor=1651066203000&limit=20&instrumentCode # noqa: E501
            if '?' in next_page_path:
                next_page_path = next_page_path.split('?')[1]

            print(next_page_path)
            url = f'{base_url}?{next_page_path}'

        return items

    def create_report(
        self,
        from_dt: str | datetime.datetime | datetime.date,
        to_dt: str | datetime.datetime | datetime.date,
        include_dividends: bool = True,
        include_interest: bool = True,
        include_orders: bool = True,
        include_transactions: bool = True,
    ) -> dict[str, int] | None:
        """Spawns T212 csv export process.

        Args:
            from_dt - start as datetime or string format %Y-%m-%dT%H:%M:%SZ
            to_dt - end as datetime or string format %Y-%m-%dT%H:%M:%SZ

        Returns:
            reportId of the created report if the api call was successful,
            None otherwise
        """
        url = 'https://live.trading212.com/api/v0/history/exports'

        if isinstance(from_dt, (datetime.datetime, datetime.date)):
            from_dt = from_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        if isinstance(to_dt, (datetime.datetime, datetime.date)):
            to_dt = to_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        payload = {
            'dataIncluded': {
                'includeDividends': include_dividends,
                'includeInterest': include_interest,
                'includeOrders': include_orders,
                'includeTransactions': include_transactions,
            },
            'timeFrom': from_dt,
            'timeTo': to_dt,
        }

        # return response.json()
        return self._post_request_loop(url, payload=payload)

    def list_reports(self) -> list[dict[str, Any]] | None:
        """Fetches list of reports.

        Returns:
            list of dicts of report attributes if the api call was successful,
            None otherwise
        """
        url = 'https://live.trading212.com/api/v0/history/exports'

        # return response.json()
        return self._get_request_loop(url)

    def get_portfolio(self) -> dict[str, str] | None:
        url = 'https://live.trading212.com/api/v0/equity/portfolio'
        return self._get_request_loop(url)

    def get_transactions(
        self, from_dt: str | datetime.datetime | datetime.date | None = None
    ) -> list[dict[str, str]] | None:
        """
        Args:
            from_dt - start as datetime or string format %Y-%m-%dT%H:%M:%SZ
        """

        if isinstance(from_dt, (datetime.datetime, datetime.date)):
            from_dt = from_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        print(f'{from_dt=}')
        url = 'https://live.trading212.com/api/v0/history/transactions'
        query = {'limit': '50'}  # 'cursor': '0',
        if from_dt:
            query['time'] = from_dt

        transactions = self._get_request_items(url, query)

        if not transactions:
            return None

        return transactions

    def get_orders(self, ticker: str | None = None) -> list[dict[str, str]] | None:
        url = 'https://live.trading212.com/api/v0/equity/history/orders'
        query = {'limit': '50'}  # 'cursor': '0',
        if ticker:
            query['ticker'] = ticker
        orders = self._get_request_items(url, query)

        if not orders:
            return None

        return orders


def main() -> None:
    load_dotenv(override=True)

    t212_client = APIClient(key=os.environ['T212_API_KEY'])

    # test create_report
    to_dt = datetime.datetime.today()
    from_dt = to_dt - relativedelta(months=1)
    report = t212_client.create_report(from_dt, to_dt)
    print(f'{report=}')

    # test list_reports
    reports = t212_client.list_reports()
    print(f'{reports=}')

    # test portfolio
    portfolio = t212_client.get_portfolio()
    print(f'{portfolio=}')

    # test all transactions
    transactions = t212_client.get_transactions()
    print(f'{transactions=}')

    # # test datetime from_dt - WIP
    # transactions_2025 = t212_client.get_transactions(
    #     datetime.datetime(2025, 5, 24, 14, 15, 22)
    # )
    # print(f'{transactions_2025=}')

    # # test str from_dt - WIP
    # transactions_2025 = t212_client.get_transactions('2025-05-24T14:15:22Z')
    # print(f'{transactions_2025=}')

    # test all orders
    orders = t212_client.get_orders()
    print(f'{orders=}')

    # test AAPL orders
    aapl_orders = t212_client.get_orders('AAPL_US_EQ')
    print(f'{aapl_orders=}')


if __name__ == '__main__':
    main()

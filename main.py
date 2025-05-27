import datetime
import time
from typing import Any

import requests


class APIClient(object):
    def __init__(self, key: str):
        self.key = key

    def _post_request_loop(
        self, url: str, payload: dict[str, str]
    ) -> dict[str, Any] | None:
        kwargs = {
            'headers': {'Content-Type': 'application/json', 'Authorization': self.key},
            'json': payload,
        }

        while True:
            response = requests.post(url, **kwargs)
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
    ) -> dict[str, Any] | None:
        kwargs = {'headers': {'Authorization': self.key}}

        if query:
            kwargs['params'] = query

        while True:
            response = requests.get(url, **kwargs)
            print(f'{response.status_code=}')

            # in case of 429 limited Try again
            if response.status_code != 429:
                break

            time.sleep(10)

        if response.status_code != 200:
            return None

        return response.json()

    def _get_request_items(
        self, url: str, query: dict[str, str] | None = None
    ) -> list[dict[str, str]] | None:
        items = []

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
            # nextPagePath transactions: "limit=20&cursor=245a5a7f-04b4-45d3-affa-72eb8ff6d62a&time=2025-05-07T00:03:03.896Z"
            # nextPagePath orders: /api/v0/equity/history/orders?cursor=1651066203000&limit=20&instrumentCode
            if '?' in next_page_path:
                next_page_path = next_page_path.split('?')[1]

            print(next_page_path)
            url = f'https://live.trading212.com/api/v0/history/transactions?{next_page_path}'

        return items

    def create_report(
        self,
        from_dt: str | datetime.datetime,
        to_dt: str | datetime.datetime,
        include_dividends: bool = True,
        include_interest: bool = True,
        include_orders: bool = True,
        include_transactions: bool = True,
    ) -> int | None:
        """Spawns T212 csv export process.

        Args:
            start_dt - start as datetime or string format %Y-%m-%dT%H:%M:%SZ
            end_dt - end as datetime or string format %Y-%m-%dT%H:%M:%SZ

        Returns:
            reportId of the created report if the api call was successful,
            None otherwise
        """
        url = 'https://live.trading212.com/api/v0/history/exports'

        if isinstance(from_dt, datetime.datetime):
            from_dt = from_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        if isinstance(to_dt, datetime.datetime):
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
        portfolio = self._get_request_loop(url)

        if not portfolio:
            return None

        return portfolio

    def get_transactions(self) -> dict[str, str] | None:
        url = 'https://live.trading212.com/api/v0/history/transactions'
        query = {
            # "cursor": "0",
            # "time": "2025-04-16T00:03:01.086Z",
            'limit': '50'
        }
        transactions = self._get_request_items(url, query)

        if not transactions:
            return None

        return transactions

    def get_orders(self) -> dict[str, str] | None:
        url = 'https://live.trading212.com/api/v0/equity/history/orders'
        query = {
            # "cursor": "0",
            'ticker': 'AAPL_US_EQ',
            'limit': '50',
        }
        orders = get_request_items(url, query)

        if not orders:
            return None

        return orders


class Report(object):
    def __init__(
        self,
        reportId: int,  # noqa: N803
        timeFrom: str,  # noqa: N803
        timeTo: str,  # noqa: N803
        dataIncluded: dict[str, bool],  # noqa: N803
        status: str,
        downloadLink: str,  # noqa: N803
    ):
        self.report_id = reportId
        self.time_from = timeFrom
        self.time_to = timeTo
        self.data_included = dataIncluded
        self.status = status
        self.download_link = downloadLink

    def download(self) -> bytes | None:
        response = requests.get(self.download_link)

        if response.status_code != 200:
            decorators.logger.warning(f'{response.status_code=}')
            return None

        return response.content


def main() -> None:
    t212_client = APIClient(key=os.environ['T212_API_KEY'])

    report_id: int = t212_client.create_report(from_dt, to_dt)

    reports: list[dict[str, Any]] = t212_client.list_reports()
    report_dict: dict[str, Any] = next(
        filter(lambda report: report.get('reportId') == report_id, reports[::-1])
    )
    report = Report(**report_dict)

    t212_df_encoded: bytes = report.download()


if __name__ == '__main__':
    main()

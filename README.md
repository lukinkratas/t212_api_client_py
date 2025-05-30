# Trading 212 Client

Very basic client from Trading 212 API.

TODO

- [ ] add asyncio

```bash
uv sync
```

```bash
uv run streamlit run main.py
```

```python
from t212 import APIClient

t212_client = APIClient(key=t212_api_key)

report = t212_client.create_report(from_dt, to_dt) # datetime or str in format %Y-%m-%dT%H:%M:%SZ

reports = t212_client.list_reports()

portfolio = t212_client.get_portfolio()

transactions = t212_client.get_transactions()

orders = t212_client.get_orders()
aapl_orders = t212_client.get_orders('AAPL_US_EQ')
```

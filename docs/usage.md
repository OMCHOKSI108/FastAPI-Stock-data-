# Quick Usage Guide

This quick guide explains how to use the Market Data endpoints in the FastAPI Stock & Crypto Data API. It covers both URL styles (path and query), example requests in cURL / Python / JavaScript, and common troubleshooting notes.

Base URL

```
https://fastapi-stock-data.onrender.com
```

Summary of relevant endpoints

- Get index price (path): GET /api/v1/market/price/index/{index}
- Get index price (query): GET /api/v1/market/price/index?index={index}

- Get stock price (path): GET /api/v1/market/price/stock/{symbol}
- Get stock price (query): GET /api/v1/market/price/stock?symbol={symbol}

Notes
- Both forms are supported for backwards compatibility. Use whichever is convenient for your client.
- Index examples: `NIFTY`, `BANKNIFTY` (use the simple name for the index price endpoint).
- Historical index endpoints use Yahoo-style symbols (for example `^NSENIFTY`) — see the full docs for historical data.
- Stock symbols for NSE generally use the `.NS` suffix (for example `RELIANCE.NS`) — the query endpoint will try a best-effort fallback if you pass `RELIANCE`.

1) Get Index Price

Description: Returns the latest price data for a market index.

Endpoint (path):

```
GET /api/v1/market/price/index/{index}
```

Example (path form):

```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/index/NIFTY"
```

Endpoint (query):

```
GET /api/v1/market/price/index?index={index}
```

Example (query form):

```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/index?index=NIFTY"
```

Example response:

```json
{
  "symbol": "NIFTY",
  "lastPrice": 23456.75,
  "pChange": 0.85,
  "change": 198.50,
  "timestamp": "09-Dec-2024 15:30:00"
}
```

Errors
- 400 Bad Request: missing or malformed query parameter
- 404 Not Found: index not found or no data returned from source
- 500 Server Error: unexpected internal error (rare — please check logs and upstream data source)

2) Get Stock Price

Description: Returns the latest price data for an NSE stock.

Endpoint (path):

```
GET /api/v1/market/price/stock/{symbol}
```

Example (path form):

```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/stock/RELIANCE.NS"
```

Endpoint (query):

```
GET /api/v1/market/price/stock?symbol={symbol}
```

Example (query form). The API will try the exact symbol and then fall back to appending `.NS` if needed:

```bash
curl "https://fastapi-stock-data.onrender.com/api/v1/market/price/stock?symbol=RELIANCE"
```

Example response:

```json
{
  "symbol": "RELIANCE.NS",
  "companyName": "Reliance Industries Ltd",
  "lastPrice": 2456.75,
  "pChange": 1.25,
  "change": 30.5,
  "timestamp": "09-Dec-2024 15:30:00"
}
```

Errors
- 400 Bad Request: missing required parameter `symbol`
- 404 Not Found: symbol not supported or delisted
- 500 Server Error: unexpected internal error

Client examples

Python (requests)

```python
import requests

BASE = "https://fastapi-stock-data.onrender.com"

# Index
r = requests.get(f"{BASE}/api/v1/market/price/index/NIFTY")
if r.ok:
    print(r.json())
else:
    print("Error", r.status_code, r.text)

# Stock (query form)
r = requests.get(f"{BASE}/api/v1/market/price/stock", params={"symbol": "RELIANCE"})
if r.ok:
    print(r.json())
else:
    print("Error", r.status_code, r.text)
```

JavaScript (fetch)

```javascript
const base = 'https://fastapi-stock-data.onrender.com';

// Index
fetch(`${base}/api/v1/market/price/index?index=NIFTY`)
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);

// Stock
fetch(`${base}/api/v1/market/price/stock?symbol=RELIANCE`)
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

Tips & Troubleshooting

- If you get `404` with message like "No lastPrice found... Available keys: [...]", the upstream NSE response shape changed for that symbol or the symbol is not available. Try:
  - Verify the symbol on the NSE website
  - Use the alternative form (path vs query)
  - Try the `.NS` suffix for stocks
- For indices use the simple names (`NIFTY`, `BANKNIFTY`). Historical endpoints require Yahoo-style symbols like `^NSENIFTY`.
- For crypto and other parts of the API, refer to the corresponding API docs pages under `docs/api`.

Best practices

- Cache responses where suitable (indices do not change every millisecond for most use cases).
- Respect upstream rate limits (NSE, Binance). Add client-side throttling.
- Prefer the path form in server-to-server calls (stable, easier to log), use the query form if your client framework builds query params more conveniently.

Further reading

- Full API reference: `docs/api/market.md`
- Symbol reference: `docs/symbols/nse-stocks.md`

---

If you want, I can add this file to the navigation (`mkdocs.yml`) and update examples across the docs so both URL styles are shown consistently.

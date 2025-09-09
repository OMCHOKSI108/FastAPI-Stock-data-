# Project Shiva — API Endpoints Catalog

*A compact, developer-friendly Markdown reference listing **all useful endpoints** for Project Shiva (options analytics + market quotes + signals + alerts + realtime). Includes a single **All-in-One endpoint** spec at the end that dashboards and mobile apps can call to get everything in one request.*

---

## Conventions

* Base path: `/api/v1`
* All times are returned in **UTC ISO 8601** unless stated otherwise.
* `index` examples: `NIFTY`, `BANKNIFTY`.
* `symbol` examples: `RELIANCE`, `INFY`.
* Authentication: endpoints marked **(auth)** require an API key / JWT.
* Pagination: use `page` and `size` query params for list endpoints.

---

## Quick table of contents

1. Data ingestion
2. Snapshot retrieval & download
3. Market quotes
4. Analytics & metrics
5. Signals & alerts
6. Jobs & backtests
7. Realtime & streaming
8. Admin, health & metrics
9. Utilities & housekeeping
10. **Main All‑in‑One Endpoint** (full spec)

---

# 1. Data ingestion (fetch / schedule)

### POST /api/v1/options/fetch  **(auth)**

Trigger immediate fetch for the *nearest expiry* and persist a snapshot.

* Body: `{ "index": "NIFTY", "num_strikes": 50 }`
* Use case: Manual refresh (admin or user-triggered).
* Response: `202 Accepted` with `job_id` or `200 OK` with snapshot metadata if sync.

### POST /api/v1/options/fetch/expiry  **(auth)**

Fetch & save for a specific expiry.

* Body: `{ "index": "NIFTY", "expiry": "25-Sep-2025", "num_strikes": 30 }`
* Use case: targeted fetch for backtesting or specific analysis.

### POST /api/v1/options/schedule  **(auth, admin)**

Register periodic fetches.

* Body: `{ "index":"NIFTY", "interval_minutes":5, "num_strikes":30 }`
* Use case: Automated ingestion; worker reads schedules and enqueues jobs.

### DELETE /api/v1/options/schedule/{schedule\_id}  **(auth, admin)**

Remove scheduled job.

---

# 2. Snapshot retrieval & download

### GET /api/v1/options/latest

Return most recent snapshot rows for an index (nearest expiry by default).

* Query: `index=...`, `expiry=...` (optional), `limit` (optional)
* Use case: populate dashboard table quickly.

### GET /api/v1/options/snapshots  **(auth)**

Paged list of saved snapshot metadata.

* Query: `index`, `start_date`, `end_date`, `page`, `size`.

### GET /api/v1/options/snapshot/{snapshot\_id}  **(auth)**

Return full snapshot payload (rows + metadata).

### GET /api/v1/options/download  **(auth)**

Download snapshot file as CSV or Parquet.

* Query: `snapshot_id` or (`index` + `expiry` + `timestamp`), `format=csv|parquet`.

### GET /api/v1/options/expiries

Return available expiries for an index (live API or cached latest snapshot).

* Query: `index`.

### GET /api/v1/options/{expiry}

Return snapshot slice filtered by expiry and optional strike-window.

* Query: `index`, `fromStrike`, `toStrike`.

---

# 3. Market quotes

### GET /api/v1/market/price/index

* Query: `index` (required)
* Returns: `{symbol, lastPrice, pChange, change, timestamp}`
* Use case: show live index price on UI header.

### GET /api/v1/market/price/stock

* Query: `symbol` (required)
* Returns: `{symbol, companyName, lastPrice, pChange, change, timestamp}`
* Use case: quick stock lookup for underlying selection.

---

# 4. Analytics & metrics

(Use functions: `calculate_pcr`, `find_high_oi_strikes`, `calculate_max_pain`, IV surface, skew)

### GET /api/v1/analytics/pcr

* Query: `index`, `expiry` (optional), `by=oi|volume` (optional)
* Returns: `{pcr_by_oi, pcr_by_volume}`
* Use case: sentiment gauge for UI / alerts.

### GET /api/v1/analytics/top-oi

* Query: `index`, `expiry`(opt), `top_n` (default 5)
* Returns top call and put OI strikes.

### GET /api/v1/analytics/max-pain

* Query: `index`, `expiry`(opt)
* Returns: `{max_pain_strike, total_loss_value}`

### GET /api/v1/analytics/iv-surface

* Query: `index`, `expiry`, `grid_res` (optional)
* Returns IVs across strikes & expiries for heatmaps.

### GET /api/v1/analytics/summary

* Query: `index`, `expiry` (optional)
* Returns combined analytics for quick dashboard header (see example in All‑in‑One).

---

# 5. Signals & alerts

### POST /api/v1/signals/compute  **(auth)**

Stateless computation of signals on the latest snapshot.

* Body: `{index, expiry(optional), methods:["oi_spike","iv_spike"], params:{...}}`
* Returns: array of signals with `type, strike, side, severity, reason`.

### POST /api/v1/alerts  **(auth)**

Create an alert rule that runs periodically.

* Body example:

```json
{
  "name":"ATM OI Spike",
  "index":"NIFTY",
  "rule":{"type":"oi_spike","side":"CE","threshold_pct":50},
  "notify":{"type":"telegram","chat_id":"-12345"},
  "enabled":true
}
```

### GET /api/v1/alerts  **(auth)**

List user alerts and their status.

### GET /api/v1/alerts/{alert\_id}  **(auth)**

View alert details.

### PUT /api/v1/alerts/{alert\_id}  **(auth)**

Update/enable/disable alert rule.

### DELETE /api/v1/alerts/{alert\_id}  **(auth)**

Remove alert.

### GET /api/v1/alerts/history  **(auth)**

Fetch triggered events for auditing/backtesting.

* Query: `alert_id`, `from_date`, `to_date`.

---

# 6. Jobs, backtests & task management

### POST /api/v1/jobs/backtest  **(auth)**

Start a backtest on historical snapshots.

* Body: `{index, expiry, strategy, start_date, end_date, params}`
* Returns: `job_id`.

### GET /api/v1/jobs/{job\_id}  **(auth)**

Check job status and results.

### GET /api/v1/jobs  **(auth)**

List jobs (filter by owner/status).

### POST /api/v1/jobs/cancel/{job\_id}  **(auth)**

Cancel a running job.

---

# 7. Realtime & streaming

### WS /api/v1/ws/options/live  **(auth)**

WebSocket channel for live snapshots and signals.

* Subscribe by `index` and optional `expiry`.
* Messages: `{type, payload}` where `type` is `snapshot`, `signal`, `ping`.

### GET /api/v1/sse/options/stream  **(auth)**

Server-sent events stream alternative for lightweight clients.

### POST /api/v1/webhook/register  **(auth)**

Register external webhook endpoints for event notifications.

* Body: `{url, events:["signal_trigger","snapshot_saved"], secret}`

---

# 8. Admin, health & metrics

### GET /api/v1/health

* Returns server liveness and last successful fetch per index.
* Use for load balancer / monitoring.

### GET /api/v1/metrics

* Prometheus-like or JSON metrics: fetch counts, avg duration, error rates.

### POST /api/v1/admin/reload-config  **(auth, admin)**

Hot-reload alert rules, schedule configs.

### POST /api/v1/maintenance/cleanup  **(auth, admin)**

Cleanup old snapshots and files.

* Body: `{retention_days: 30, dry_run: true}`

---

# 9. Utilities & housekeeping

### GET /api/v1/docs/schema

Return OpenAPI schema or generated client SDK info.

### POST /api/v1/auth/token

Issue API tokens or JWTs.

### GET /api/v1/users/me  **(auth)**

Return user account and permissions.

---

# 10. MAIN ALL‑IN‑ONE ENDPOINT (Single call for dashboards / mobile apps)

This endpoint returns a compact but comprehensive payload that includes: latest snapshot metadata, a small sample of rows (or aggregated metrics), market quote, analytics (PCR, max pain, top OI) and any active signals. It is intended for dashboards and mobile apps that want one request to populate the entire header + snapshot card.

### GET /api/v1/combined/summary  **(auth optional, recommended auth for production)**

* Query parameters:

  * `index` (required)
  * `expiry` (optional) — if omitted, nearest expiry is used
  * `snapshot_id` (optional) — override
  * `rows` (optional, default `20`) — number of sample rows to return
  * `include` (comma-separated): `rows,analytics,signals,quote,download` (default: `rows,analytics,quote`)

#### Use case

* Dashboard header: show underlying price, ATM, PCR, Top OI resistance/support, Max Pain, a short table of strikes, and any active signals.

#### Response schema (example)

```json
{
  "meta": {
    "index":"NIFTY",
    "expiry":"11-Sep-2025",
    "snapshot_id":"uuid",
    "createdAtUTC":"2025-09-09T07:30:00Z",
    "underlying": 18876.25,
    "atmStrike": 18875
  },
  "quote": {"symbol":"NIFTY","lastPrice":18876.25,"pChange":0.45},
  "analytics": {
    "pcr_by_oi": 1.12,
    "pcr_by_volume": 0.98,
    "max_pain_strike": 18900,
    "top_oi": {
      "resistance": [{"strike":19000,"oi":123000}],
      "support": [{"strike":18800,"oi":115000}]
    }
  },
  "signals": [
    {"type":"oi_spike","strike":18900,"side":"CE","severity":0.82,"reason":"OI +150% in 15m"}
  ],
  "rows": [
    {"strikePrice":18825,"CE_lastPrice":12.5,"PE_lastPrice":8.1},
    {"strikePrice":18875,"CE_lastPrice":7.8,"PE_lastPrice":10.2}
  ],
  "download_links": {
    "csv":"/api/v1/options/download?snapshot_id=uuid&format=csv",
    "parquet":"/api/v1/options/download?snapshot_id=uuid&format=parquet"
  }
}
```

#### Notes & recommendations

* Keep this endpoint cached for short TTL (10–30s) when used by many clients; push updates via WebSocket for real-time users.
* `include` lets clients request only what they need to reduce payload size.
* Consider offering an `etag` or `lastModified` header so clients can conditional GET.

---

# Implementation suggestions & priorities

* **Phase 1 (MVP)**: Implement endpoints in *Must-have* + `combined/summary` + analytics endpoints. Use synchronous fetch for manual triggers; persist snapshots to disk + Postgres metadata table.
* **Phase 2**: Add job queue, scheduling, alerts persistence, and download endpoints.
* **Phase 3**: WebSocket, webhook registration, backtesting, and Prometheus metrics.

# Postscript

If you want, I can:

* generate a ready-to-drop **`routes.py`** FastAPI stub implementing the top 12 endpoints, or
* produce **SQL schema** for `snapshots`, `signals`, `alerts`, and `jobs`, or
* produce a one-file **`combined/summary`** implementation using your current script.

Tell me which artifact to produce next, Captain.

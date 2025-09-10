from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import os
import time
import json
import bisect
import tempfile
from datetime import datetime
import pandas as pd
from nsepython import option_chain, nse_quote
from ..schemas import IndexPriceResponse, StockQuote, FetchOptionsRequest, FetchExpiryRequest, FetchResultMeta, AnalyticsResponse, OptionPriceResponse, DirectOptionsData, OptionStrikeData, OptionHistoricalData

router = APIRouter()

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'option_chain_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def _expand_side(df: pd.DataFrame, side: str) -> pd.DataFrame:
    valid_rows = df[df[side].apply(lambda x: isinstance(x, dict))]
    if valid_rows.empty:
        return pd.DataFrame()
    side_data = valid_rows[side].apply(pd.Series)
    side_data = side_data.add_prefix(f'{side}_')
    return side_data

def _atomic_write_csv(df: pd.DataFrame, target_path: str):
    dirpath = os.path.dirname(target_path)
    os.makedirs(dirpath, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=dirpath, delete=False, suffix=".csv") as tmp:
        tmp_name = tmp.name
        df.to_csv(tmp_name, index=False)
    os.replace(tmp_name, target_path)

def _atomic_write_json(obj: dict, target_path: str):
    dirpath = os.path.dirname(target_path)
    os.makedirs(dirpath, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=dirpath, delete=False, suffix=".json", encoding="utf-8") as tmp:
        tmp_name = tmp.name
        json.dump(obj, tmp, indent=2)
    os.replace(tmp_name, target_path)

def _normalize_index_name(index: str) -> str:
    if not index:
        return ""
    s = index.strip().upper()
    if s in ("NIFTY50", "NIFTY", "NSEI"):
        return "NIFTY"
    if s in ("BANKNIFTY", "NSEBANK"):
        return "BANKNIFTY"
    # BSE indices
    if s in ("SENSEX", "BSESN"):
        return "SENSEX"
    if s in ("BANKEX", "BSEBANK"):
        return "BANKEX"
    if s in ("AUTO", "CNXAUTO"):
        return "AUTO"
    if s in ("FINANCE", "CNXFIN"):
        return "FINANCE"
    if s in ("IT", "CNXIT"):
        return "IT"
    if s in ("METAL", "CNXMETAL"):
        return "METAL"
    if s in ("PHARMA", "CNXPHARMA"):
        return "PHARMA"
    if s in ("REALTY", "CNXREALTY"):
        return "REALTY"
    return s

def calculate_pcr(df: pd.DataFrame) -> dict:
    pcr_data = {'pcr_by_oi': 0.0, 'pcr_by_volume': 0.0}
    if 'PE_openInterest' in df.columns and 'CE_openInterest' in df.columns:
        total_pe_oi = df['PE_openInterest'].fillna(0).sum()
        total_ce_oi = df['CE_openInterest'].fillna(0).sum()
        if total_ce_oi > 0:
            pcr_data['pcr_by_oi'] = round(total_pe_oi / total_ce_oi, 2)
    if 'PE_totalTradedVolume' in df.columns and 'CE_totalTradedVolume' in df.columns:
        total_pe_volume = df['PE_totalTradedVolume'].fillna(0).sum()
        total_ce_volume = df['CE_totalTradedVolume'].fillna(0).sum()
        if total_ce_volume > 0:
            pcr_data['pcr_by_volume'] = round(total_pe_volume / total_ce_volume, 2)
    return pcr_data

def find_high_oi_strikes(df: pd.DataFrame, top_n: int = 5) -> dict:
    results = {'resistance_strikes': [], 'support_strikes': []}
    if 'CE_openInterest' in df.columns:
        top_calls = df.nlargest(top_n, 'CE_openInterest')[['strikePrice', 'CE_openInterest']].fillna(0)
        results['resistance_strikes'] = top_calls.to_dict('records')
    if 'PE_openInterest' in df.columns:
        top_puts = df.nlargest(top_n, 'PE_openInterest')[['strikePrice', 'PE_openInterest']].fillna(0)
        results['support_strikes'] = top_puts.to_dict('records')
    return results

def calculate_max_pain(df: pd.DataFrame) -> dict:
    if 'strikePrice' not in df.columns:
        return {'max_pain_strike': None, 'max_loss_value': 0}
    strikes = sorted(df['strikePrice'].dropna().unique())
    total_loss_at_strike = {}
    for strike_price in strikes:
        loss = 0
        if 'CE_openInterest' in df.columns and 'CE_lastPrice' in df.columns:
            ce_data = df[['strikePrice', 'CE_openInterest', 'CE_lastPrice']].dropna()
            for _, row in ce_data.iterrows():
                if row['strikePrice'] > strike_price:
                    loss += (row['strikePrice'] - strike_price) * row['CE_openInterest']
        if 'PE_openInterest' in df.columns and 'PE_lastPrice' in df.columns:
            pe_data = df[['strikePrice', 'PE_openInterest', 'PE_lastPrice']].dropna()
            for _, row in pe_data.iterrows():
                if row['strikePrice'] < strike_price:
                    loss += (strike_price - row['strikePrice']) * row['PE_openInterest']
        total_loss_at_strike[strike_price] = loss
    if not total_loss_at_strike:
        return {'max_pain_strike': None, 'max_loss_value': 0}
    max_pain_strike = min(total_loss_at_strike, key=total_loss_at_strike.get)
    return {'max_pain_strike': int(max_pain_strike), 'max_loss_value': int(total_loss_at_strike[max_pain_strike])}

def _prepare_option_chain_df(resp: dict, expiry: str) -> pd.DataFrame:
    if not (isinstance(resp, dict) and 'records' in resp and 'data' in resp['records']):
        raise RuntimeError("Invalid response structure from NSE.")
    df_full = pd.DataFrame(resp['records']['data'])
    if df_full.empty:
        raise RuntimeError("No option chain data returned by NSE.")
    if 'strikePrice' not in df_full.columns:
        raise RuntimeError("Column 'strikePrice' missing from NSE response.")
    df_full['strikePrice'] = pd.to_numeric(df_full['strikePrice'], errors='coerce')
    df = df_full[df_full['expiryDate'] == expiry].copy()
    if df.empty:
        raise RuntimeError(f"No data for expiry {expiry}")
    ce_data = _expand_side(df, 'CE')
    pe_data = _expand_side(df, 'PE')
    df_processed = pd.concat([df[['strikePrice', 'expiryDate']].reset_index(drop=True), ce_data.reset_index(drop=True), pe_data.reset_index(drop=True)], axis=1)
    return df_processed

def _select_strikes_and_save(df_processed: pd.DataFrame, resp: dict, index_name: str, expiry: str, num_strikes: int) -> FetchResultMeta:
    underlying_value = float(resp['records'].get('underlyingValue', 0))
    strikes = sorted(df_processed['strikePrice'].dropna().unique())
    if not strikes:
        raise RuntimeError("No strikes found after processing")
    atm_strike_index = bisect.bisect_left(strikes, underlying_value)
    if atm_strike_index > 0 and abs(strikes[atm_strike_index-1] - underlying_value) < abs(strikes[atm_strike_index] - underlying_value):
        atm_strike_index -= 1
    low_index = max(0, atm_strike_index - num_strikes)
    high_index = min(len(strikes) - 1, atm_strike_index + num_strikes)
    selected_strikes = strikes[low_index:high_index+1]
    df_final = df_processed[df_processed['strikePrice'].isin(selected_strikes)].sort_values(['strikePrice']).reset_index(drop=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_expiry = str(expiry).replace(' ', '_').replace('/', '-')
    base_filename = f"{index_name.lower()}_option_chain_{safe_expiry}_{timestamp}"
    csv_path = os.path.join(OUTPUT_DIR, f"{base_filename}.csv")
    meta_path = os.path.join(OUTPUT_DIR, f"{base_filename}.json")
    _atomic_write_csv(df_final, csv_path)
    metadata = {
        'createdAtUTC': datetime.utcnow().isoformat(),
        'indexName': index_name,
        'nearestExpiry': expiry,
        'underlyingValue': float(underlying_value),
        'atmStrike': int(strikes[atm_strike_index]) if 0 <= atm_strike_index < len(strikes) else None,
        'selectedStrikesRange': [int(selected_strikes[0]), int(selected_strikes[-1])],
        'totalStrikesFetched': int(len(df_final))
    }
    _atomic_write_json(metadata, meta_path)
    return FetchResultMeta(**metadata)

def fetch_and_save_option_chain(index_name: str, num_strikes_around_atm: int = 25) -> FetchResultMeta:
    start_time = time.time()
    resp = option_chain(index_name)
    expiries = resp['records'].get('expiryDates', [])
    if not expiries:
        raise RuntimeError("No expiries in NSE response.")
    nearest_expiry = expiries[0]
    df_processed = _prepare_option_chain_df(resp, nearest_expiry)
    meta = _select_strikes_and_save(df_processed, resp, index_name, nearest_expiry, num_strikes_around_atm)
    elapsed = time.time() - start_time
    print(f"Saved option chain for {index_name} expiry {nearest_expiry} in {elapsed:.2f}s")
    return meta

def fetch_specific_expiry_option_chain(index_name: str, expiry_date: str, num_strikes_around_atm: int = 25) -> FetchResultMeta:
    start_time = time.time()
    resp = option_chain(index_name)
    expiries = resp['records'].get('expiryDates', [])
    if expiry_date not in expiries:
        raise HTTPException(status_code=422, detail=f"Expiry '{expiry_date}' not available. Available: {expiries}")
    df_processed = _prepare_option_chain_df(resp, expiry_date)
    meta = _select_strikes_and_save(df_processed, resp, index_name, expiry_date, num_strikes_around_atm)
    elapsed = time.time() - start_time
    print(f"Saved option chain for {index_name} expiry {expiry_date} in {elapsed:.2f}s")
    return meta

def get_available_expiries(index_name: str) -> List[str]:
    try:
        resp = option_chain(index_name)
        return resp['records'].get('expiryDates', [])
    except Exception as e:
        print(f"get_available_expiries error: {e}")
        return []

def fetch_index_price(index_name: str) -> dict:
    try:
        # Map NSE index names to Yahoo Finance symbols
        index_mapping = {
            'NIFTY': '^NSEI',
            'BANKNIFTY': '^NSEBANK',
            'NIFTY50': '^NSEI',
            'NSEI': '^NSEI',
            'NSEBANK': '^NSEBANK'
        }
        
        yf_symbol = index_mapping.get(index_name.upper(), f'^{index_name.upper()}')
        
        from ..providers import yfinance_provider
        # Use sync version
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        quote = loop.run_until_complete(yfinance_provider.get_quote(yf_symbol))
        loop.close()
        
        if quote:
            return {
                'symbol': index_name,
                'lastPrice': quote['price'],
                'pChange': 0.0,  # yfinance doesn't provide pChange in this format
                'change': 0.0,
                'timestamp': quote['timestamp']
            }
        else:
            raise HTTPException(status_code=404, detail=f"No data for index {index_name}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def fetch_stock_price(stock_symbol: str) -> dict:
    try:
        # For NSE stocks, append .NS if not already present
        if not stock_symbol.upper().endswith('.NS'):
            yf_symbol = f"{stock_symbol.upper()}.NS"
        else:
            yf_symbol = stock_symbol.upper()
        
        from ..providers import yfinance_provider
        # Use sync version
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        quote = loop.run_until_complete(yfinance_provider.get_quote(yf_symbol))
        loop.close()
        
        if quote:
            return {
                'symbol': stock_symbol,
                'companyName': stock_symbol,  # yfinance doesn't provide company name in this format
                'lastPrice': quote['price'],
                'pChange': 0.0,
                'change': 0.0,
                'timestamp': quote['timestamp']
            }
        else:
            raise HTTPException(status_code=404, detail=f"No data for stock {stock_symbol}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/expiries", response_model=List[str])
def api_get_expiries(index: str = Query(..., description="Index symbol, e.g. NIFTY")):
    idx = _normalize_index_name(index)
    expiries = get_available_expiries(idx)
    if not expiries:
        raise HTTPException(status_code=404, detail=f"No expiries found for {idx}")
    return expiries

@router.get("/index-price", response_model=IndexPriceResponse)
def api_index_price(index: str = Query(..., description="Index symbol, e.g. NIFTY")):
    idx = _normalize_index_name(index)
    data = fetch_index_price(idx)
    return IndexPriceResponse(**data)

@router.get("/stock-price", response_model=StockQuote)
def api_stock_price(symbol: str = Query(..., description="Stock symbol (NSE), e.g. RELIANCE")):
    data = fetch_stock_price(symbol.upper())
    return StockQuote(**data)

@router.post("/fetch", response_model=FetchResultMeta, status_code=201)
def api_fetch_options(request: FetchOptionsRequest):
    idx = _normalize_index_name(request.index)
    try:
        meta = fetch_and_save_option_chain(idx, request.num_strikes)
        return meta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fetch/expiry", response_model=FetchResultMeta, status_code=201)
def api_fetch_options_expiry(req: FetchExpiryRequest):
    idx = _normalize_index_name(req.index)
    try:
        meta = fetch_specific_expiry_option_chain(idx, req.expiry, req.num_strikes)
        return meta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New JSON endpoints that return data directly instead of saving to CSV
@router.post("/fetch/json", response_model=DirectOptionsData)
def api_fetch_options_json(request: FetchOptionsRequest):
    """Fetch options data and return JSON directly (does not save to CSV)"""
    idx = _normalize_index_name(request.index)

    try:
        resp = option_chain(idx)
        if not (isinstance(resp, dict) and 'records' in resp and 'data' in resp['records']):
            raise HTTPException(status_code=500, detail="Invalid response from NSE")

        df_full = pd.DataFrame(resp['records']['data'])
        if df_full.empty:
            raise HTTPException(status_code=404, detail="No option chain data found")

        # Get nearest expiry
        expiries = resp['records'].get('expiryDates', [])
        if not expiries:
            raise HTTPException(status_code=404, detail="No expiry dates available")
        nearest_expiry = expiries[0]

        # Filter by nearest expiry
        df_filtered = df_full[df_full['expiryDate'] == nearest_expiry]
        if df_filtered.empty:
            raise HTTPException(status_code=404, detail=f"No data found for nearest expiry {nearest_expiry}")

        underlying_value = float(resp['records'].get('underlyingValue', 0))

        # Select strikes around ATM
        strikes = sorted(df_filtered['strikePrice'].dropna().unique())
        if not strikes:
            raise HTTPException(status_code=404, detail="No strikes found")

        atm_index = bisect.bisect_left(strikes, underlying_value)
        if atm_index > 0 and abs(strikes[atm_index-1] - underlying_value) < abs(strikes[atm_index] - underlying_value):
            atm_index -= 1

        low_index = max(0, atm_index - request.num_strikes)
        high_index = min(len(strikes) - 1, atm_index + request.num_strikes)
        selected_strikes = strikes[low_index:high_index+1]

        df_final = df_filtered[df_filtered['strikePrice'].isin(selected_strikes)].sort_values(['strikePrice'])

        # Convert to list of dicts
        options_data = []
        for _, row in df_final.iterrows():
            option_row = {
                'strikePrice': row['strikePrice'],
                'expiryDate': row['expiryDate']
            }

            # Add CE data
            if isinstance(row.get('CE'), dict):
                option_row['CE'] = row['CE']

            # Add PE data
            if isinstance(row.get('PE'), dict):
                option_row['PE'] = row['PE']

            options_data.append(option_row)

        return DirectOptionsData(
            index=idx,
            expiry=nearest_expiry,
            underlying_value=underlying_value,
            options=options_data,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fetch/expiry/json", response_model=DirectOptionsData)
def api_fetch_options_expiry_json(req: FetchExpiryRequest):
    """Fetch options data for specific expiry and return JSON directly (does not save to CSV)"""
    idx = _normalize_index_name(req.index)

    # Convert DDMMYY format to DD-MMM-YYYY format
    try:
        if len(req.expiry) == 6 and req.expiry.isdigit():
            # Parse DDMMYY format
            day = req.expiry[:2]
            month = req.expiry[2:4]
            year = '20' + req.expiry[4:]  # Assume 20xx for years

            # Convert month number to month name
            month_names = {
                '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
                '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
            }

            if month not in month_names:
                raise HTTPException(status_code=400, detail="Invalid month in expiry date")

            nse_expiry = f"{day}-{month_names[month]}-{year}"
        else:
            # Assume it's already in DD-MMM-YYYY format
            nse_expiry = req.expiry
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid expiry date format: {req.expiry}. Use DDMMYY format (e.g. 160925)")

    try:
        resp = option_chain(idx)
        if not (isinstance(resp, dict) and 'records' in resp and 'data' in resp['records']):
            raise HTTPException(status_code=500, detail="Invalid response from NSE")

        df_full = pd.DataFrame(resp['records']['data'])
        if df_full.empty:
            raise HTTPException(status_code=404, detail="No option chain data found")

        # Filter by expiry
        df_filtered = df_full[df_full['expiryDate'] == nse_expiry]
        if df_filtered.empty:
            available_expiries = resp['records'].get('expiryDates', [])
            raise HTTPException(
                status_code=404,
                detail=f"No data found for expiry '{nse_expiry}' (input: {req.expiry}). "
                       f"Available expiries: {available_expiries[:5]}"
            )

        underlying_value = float(resp['records'].get('underlyingValue', 0))

        # Select strikes around ATM
        strikes = sorted(df_filtered['strikePrice'].dropna().unique())
        if not strikes:
            raise HTTPException(status_code=404, detail="No strikes found")

        atm_index = bisect.bisect_left(strikes, underlying_value)
        if atm_index > 0 and abs(strikes[atm_index-1] - underlying_value) < abs(strikes[atm_index] - underlying_value):
            atm_index -= 1

        low_index = max(0, atm_index - req.num_strikes)
        high_index = min(len(strikes) - 1, atm_index + req.num_strikes)
        selected_strikes = strikes[low_index:high_index+1]

        df_final = df_filtered[df_filtered['strikePrice'].isin(selected_strikes)].sort_values(['strikePrice'])

        # Convert to list of dicts
        options_data = []
        for _, row in df_final.iterrows():
            option_row = {
                'strikePrice': row['strikePrice'],
                'expiryDate': row['expiryDate']
            }

            # Add CE data
            if isinstance(row.get('CE'), dict):
                option_row['CE'] = row['CE']

            # Add PE data
            if isinstance(row.get('PE'), dict):
                option_row['PE'] = row['PE']

            options_data.append(option_row)

        return DirectOptionsData(
            index=idx,
            expiry=nse_expiry,  # Return the NSE format
            underlying_value=underlying_value,
            options=options_data,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics", response_model=AnalyticsResponse)
def api_analytics_for_latest(index: str = Query(...), limit: int = Query(500, gt=0, le=5000)):
    idx = _normalize_index_name(index)
    files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(f"{idx.lower()}_") and f.endswith('.csv')]
    if not files:
        raise HTTPException(status_code=404, detail=f"No saved option-chain CSVs found for {idx}")
    latest_file = sorted(files, reverse=True)[0]
    csv_path = os.path.join(OUTPUT_DIR, latest_file)
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to read saved CSV")
    if limit:
        df = df.head(limit)
    pcr = calculate_pcr(df)
    top_oi = find_high_oi_strikes(df, top_n=5)
    max_pain = calculate_max_pain(df)
    meta_file = csv_path.replace('.csv', '.json')
    meta_obj = {}
    if os.path.exists(meta_file):
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta_obj = json.load(f)
    meta_obj.setdefault('createdAtUTC', datetime.utcnow().isoformat())
    meta = FetchResultMeta(**meta_obj)
    return AnalyticsResponse(meta=meta, pcr=pcr, top_oi=top_oi, max_pain=max_pain)

@router.get("/option-price", response_model=OptionPriceResponse)
def api_get_option_price(
    index: str = Query(..., description="Index symbol, e.g. NIFTY"),
    strike: float = Query(..., description="Strike price"),
    expiry: str = Query(..., description="Expiry date (DDMMYY format, e.g. 160925 for 16-Sep-2025)"),
    option_type: str = Query(..., description="Option type: CE or PE")
):
    """Get price for a specific option (CE/PE) by strike and expiry"""
    idx = _normalize_index_name(index)
    option_type = option_type.upper()
    
    if option_type not in ['CE', 'PE']:
        raise HTTPException(status_code=400, detail="Option type must be CE or PE")
    
    # Convert DDMMYY format to DD-MMM-YYYY format
    try:
        if len(expiry) == 6 and expiry.isdigit():
            # Parse DDMMYY format
            day = expiry[:2]
            month = expiry[2:4]
            year = '20' + expiry[4:]  # Assume 20xx for years
            
            # Convert month number to month name
            month_names = {
                '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
                '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
            }
            
            if month not in month_names:
                raise HTTPException(status_code=400, detail="Invalid month in expiry date")
            
            nse_expiry = f"{day}-{month_names[month]}-{year}"
        else:
            # Assume it's already in DD-MMM-YYYY format
            nse_expiry = expiry
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid expiry date format: {expiry}. Use DDMMYY format (e.g. 160925)")
    
    try:
        resp = option_chain(idx)
        if not (isinstance(resp, dict) and 'records' in resp and 'data' in resp['records']):
            raise HTTPException(status_code=500, detail="Invalid response from NSE")
        
        df_full = pd.DataFrame(resp['records']['data'])
        if df_full.empty:
            raise HTTPException(status_code=404, detail="No option chain data found")
        
        # Filter by expiry and strike
        df_filtered = df_full[(df_full['expiryDate'] == nse_expiry) & (df_full['strikePrice'] == strike)]
        if df_filtered.empty:
            # Try to provide helpful error message
            available_expiries = resp['records'].get('expiryDates', [])
            available_strikes = sorted(df_full['strikePrice'].dropna().unique())
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for strike {strike} and expiry '{nse_expiry}' (input: {expiry}). "
                       f"Available expiries: {available_expiries[:5]}. "
                       f"Strike range: {min(available_strikes)} - {max(available_strikes)}"
            )
        
        row = df_filtered.iloc[0]
        option_data = row.get(option_type, {})
        
        if not isinstance(option_data, dict):
            raise HTTPException(status_code=404, detail=f"No {option_type} data available for this strike")
        
        return OptionPriceResponse(
            symbol=f"{idx}{strike}{option_type}",
            strike=strike,
            expiry=nse_expiry,  # Return the NSE format
            option_type=option_type,
            lastPrice=option_data.get('lastPrice'),
            openInterest=option_data.get('openInterest'),
            volume=option_data.get('totalTradedVolume'),
            bid=option_data.get('bidprice'),
            ask=option_data.get('askPrice'),
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/direct-data", response_model=DirectOptionsData)
def api_get_direct_options_data(
    index: str = Query(..., description="Index symbol, e.g. NIFTY"),
    expiry: str = Query(..., description="Expiry date (DDMMYY format, e.g. 160925 for 16-Sep-2025)"),
    num_strikes: int = Query(25, description="Number of strikes around ATM")
):
    """Get options data directly without saving to CSV"""
    idx = _normalize_index_name(index)
    
    # Convert DDMMYY format to DD-MMM-YYYY format
    try:
        if len(expiry) == 6 and expiry.isdigit():
            # Parse DDMMYY format
            day = expiry[:2]
            month = expiry[2:4]
            year = '20' + expiry[4:]  # Assume 20xx for years
            
            # Convert month number to month name
            month_names = {
                '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
                '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
            }
            
            if month not in month_names:
                raise HTTPException(status_code=400, detail="Invalid month in expiry date")
            
            nse_expiry = f"{day}-{month_names[month]}-{year}"
        else:
            # Assume it's already in DD-MMM-YYYY format
            nse_expiry = expiry
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid expiry date format: {expiry}. Use DDMMYY format (e.g. 160925)")
    
    try:
        resp = option_chain(idx)
        if not (isinstance(resp, dict) and 'records' in resp and 'data' in resp['records']):
            raise HTTPException(status_code=500, detail="Invalid response from NSE")
        
        df_full = pd.DataFrame(resp['records']['data'])
        if df_full.empty:
            raise HTTPException(status_code=404, detail="No option chain data found")
        
        # Filter by expiry
        df_filtered = df_full[df_full['expiryDate'] == nse_expiry]
        if df_filtered.empty:
            available_expiries = resp['records'].get('expiryDates', [])
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for expiry '{nse_expiry}' (input: {expiry}). "
                       f"Available expiries: {available_expiries[:5]}"
            )
        
        underlying_value = float(resp['records'].get('underlyingValue', 0))
        
        # Select strikes around ATM
        strikes = sorted(df_filtered['strikePrice'].dropna().unique())
        if not strikes:
            raise HTTPException(status_code=404, detail="No strikes found")
        
        atm_index = bisect.bisect_left(strikes, underlying_value)
        if atm_index > 0 and abs(strikes[atm_index-1] - underlying_value) < abs(strikes[atm_index] - underlying_value):
            atm_index -= 1
        
        low_index = max(0, atm_index - num_strikes)
        high_index = min(len(strikes) - 1, atm_index + num_strikes)
        selected_strikes = strikes[low_index:high_index+1]
        
        df_final = df_filtered[df_filtered['strikePrice'].isin(selected_strikes)].sort_values(['strikePrice'])
        
        # Convert to list of dicts
        options_data = []
        for _, row in df_final.iterrows():
            option_row = {
                'strikePrice': row['strikePrice'],
                'expiryDate': row['expiryDate']
            }
            
            # Add CE data
            if isinstance(row.get('CE'), dict):
                option_row['CE'] = row['CE']
            
            # Add PE data
            if isinstance(row.get('PE'), dict):
                option_row['PE'] = row['PE']
            
            options_data.append(option_row)
        
        return DirectOptionsData(
            index=idx,
            expiry=nse_expiry,  # Return the NSE format
            underlying_value=underlying_value,
            options=options_data,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strike-data", response_model=OptionStrikeData)
def api_get_strike_data(
    index: str = Query(..., description="Index symbol, e.g. NIFTY"),
    strike: float = Query(..., description="Strike price"),
    expiry: str = Query(..., description="Expiry date (DDMMYY format, e.g. 160925 for 16-Sep-2025)"),
    option_type: str = Query("BOTH", description="Option type: CE, PE, or BOTH")
):
    """Get option data for a specific strike, expiry, and option type(s)"""
    idx = _normalize_index_name(index)
    option_type = option_type.upper()
    
    if option_type not in ['CE', 'PE', 'BOTH']:
        raise HTTPException(status_code=400, detail="Option type must be CE, PE, or BOTH")
    
    # Convert DDMMYY format to DD-MMM-YYYY format
    try:
        if len(expiry) == 6 and expiry.isdigit():
            day = expiry[:2]
            month = expiry[2:4]
            year = '20' + expiry[4:]
            
            month_names = {
                '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
                '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
            }
            
            if month not in month_names:
                raise HTTPException(status_code=400, detail="Invalid month in expiry date")
            
            nse_expiry = f"{day}-{month_names[month]}-{year}"
        else:
            nse_expiry = expiry
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid expiry date format: {expiry}. Use DDMMYY format (e.g. 160925)")
    
    try:
        resp = option_chain(idx)
        if not (isinstance(resp, dict) and 'records' in resp and 'data' in resp['records']):
            raise HTTPException(status_code=500, detail="Invalid response from NSE")
        
        df_full = pd.DataFrame(resp['records']['data'])
        if df_full.empty:
            raise HTTPException(status_code=404, detail="No option chain data found")
        
        # Filter by expiry and strike
        df_filtered = df_full[(df_full['expiryDate'] == nse_expiry) & (df_full['strikePrice'] == strike)]
        if df_filtered.empty:
            available_expiries = resp['records'].get('expiryDates', [])
            available_strikes = sorted(df_full['strikePrice'].dropna().unique())
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for strike {strike} and expiry '{nse_expiry}' (input: {expiry}). "
                       f"Available expiries: {available_expiries[:5]}. "
                       f"Strike range: {min(available_strikes)} - {max(available_strikes)}"
            )
        
        row = df_filtered.iloc[0]
        underlying_value = float(resp['records'].get('underlyingValue', 0))
        
        ce_data = None
        pe_data = None
        
        if option_type in ['CE', 'BOTH']:
            if isinstance(row.get('CE'), dict):
                ce_data = row['CE']
        
        if option_type in ['PE', 'BOTH']:
            if isinstance(row.get('PE'), dict):
                pe_data = row['PE']
        
        if option_type == 'CE' and ce_data is None:
            raise HTTPException(status_code=404, detail=f"No CE data available for strike {strike}")
        
        if option_type == 'PE' and pe_data is None:
            raise HTTPException(status_code=404, detail=f"No PE data available for strike {strike}")
        
        return OptionStrikeData(
            index=idx,
            strike=strike,
            expiry=nse_expiry,
            option_type=option_type,
            ce_data=ce_data,
            pe_data=pe_data,
            underlying_value=underlying_value,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical/{symbol}", response_model=OptionHistoricalData)
async def api_get_option_historical(
    symbol: str,
    strike: float = Query(..., description="Strike price"),
    expiry: str = Query(..., description="Expiry date (DDMMYY format, e.g. 160925 for 16-Sep-2025)"),
    option_type: str = Query(..., description="Option type: CE or PE"),
    period: str = Query("1d", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
):
    """Get historical data for a specific option contract"""
    option_type = option_type.upper()
    
    if option_type not in ['CE', 'PE']:
        raise HTTPException(status_code=400, detail="Option type must be CE or PE")
    
    # Convert DDMMYY format to DD-MMM-YYYY format
    try:
        if len(expiry) == 6 and expiry.isdigit():
            day = expiry[:2]
            month = expiry[2:4]
            year = '20' + expiry[4:]
            
            month_names = {
                '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
                '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug',
                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
            }
            
            if month not in month_names:
                raise HTTPException(status_code=400, detail="Invalid month in expiry date")
            
            nse_expiry = f"{day}-{month_names[month]}-{year}"
        else:
            nse_expiry = expiry
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid expiry date format: {expiry}. Use DDMMYY format (e.g. 160925)")
    
    # Check if expiry is in the future
    try:
        expiry_date = datetime.strptime(nse_expiry, "%d-%b-%Y")
        current_date = datetime.now()
        if expiry_date > current_date:
            raise HTTPException(status_code=400, detail=f"Cannot get historical data for future expiry date: {nse_expiry}")
    except ValueError:
        # If parsing fails, assume it's valid
        pass
    
    # Construct the option symbol for yfinance
    # Format: INDEXYYMMDDSTRIKECPE (e.g., NIFTY25SEP24850CE)
    try:
        # Parse expiry to get YYMMDD format
        expiry_parts = nse_expiry.split('-')
        if len(expiry_parts) == 3:
            day = expiry_parts[0].zfill(2)
            month_name = expiry_parts[1]
            year_short = expiry_parts[2][2:]  # Last 2 digits of year
            
            # Convert month name to number
            month_names = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            
            month_num = month_names.get(month_name)
            if not month_num:
                raise HTTPException(status_code=400, detail=f"Invalid month name: {month_name}")
            
            yf_expiry = f"{year_short}{month_num}{day}"
            
            # Construct yfinance symbol
            index_name = symbol.upper()
            strike_int = int(strike)
            yf_symbol = f"{index_name}{yf_expiry}{strike_int}{option_type}.NS"
            
            # Instead of yfinance, check for stored CSV data
            # Note: Stored CSV has current data, not historical time series
            # For historical data, you would need to store time series data separately
            
            # For now, return error as historical time series is not implemented
            raise HTTPException(status_code=501, detail="Historical time series data for options is not implemented. Use current option chain data from stored CSVs.")
        else:
            raise HTTPException(status_code=400, detail="Invalid expiry format")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live-chain", response_model=Dict[str, Any])
def api_get_live_option_chain(
    index: str = Query(..., description="Index symbol, e.g. NIFTY"),
    expiry: str = Query(None, description="Specific expiry date, if not provided uses nearest")
):
    """
    Fetch fresh option chain data without saving to CSV.
    Returns the processed DataFrame as JSON.
    """
    idx = _normalize_index_name(index)
    try:
        resp = option_chain(idx)
        expiries = resp['records'].get('expiryDates', [])
        if not expiries:
            raise HTTPException(status_code=404, detail=f"No expiries found for {idx}")
        
        selected_expiry = expiry if expiry and expiry in expiries else expiries[0]
        df_processed = _prepare_option_chain_df(resp, selected_expiry)
        
        # Convert to dict for JSON response
        data = {
            'index': idx,
            'expiry': selected_expiry,
            'underlying_value': float(resp['records'].get('underlyingValue', 0)),
            'data': df_processed.to_dict('records'),
            'timestamp': datetime.now().isoformat()
        }
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live-analytics", response_model=Dict[str, Any])
def api_get_live_analytics(
    index: str = Query(..., description="Index symbol, e.g. NIFTY"),
    expiry: str = Query(None, description="Specific expiry date, if not provided uses nearest"),
    limit: int = Query(500, gt=0, le=5000)
):
    """
    Fetch fresh option chain data and compute analytics without saving to CSV.
    """
    idx = _normalize_index_name(index)
    try:
        resp = option_chain(idx)
        expiries = resp['records'].get('expiryDates', [])
        if not expiries:
            raise HTTPException(status_code=404, detail=f"No expiries found for {idx}")
        
        selected_expiry = expiry if expiry and expiry in expiries else expiries[0]
        df_processed = _prepare_option_chain_df(resp, selected_expiry)
        
        # Apply limit
        if limit:
            df_processed = df_processed.head(limit)
        
        # Compute analytics
        pcr = calculate_pcr(df_processed)
        top_oi = find_high_oi_strikes(df_processed, top_n=5)
        max_pain = calculate_max_pain(df_processed)
        
        data = {
            'index': idx,
            'expiry': selected_expiry,
            'underlying_value': float(resp['records'].get('underlyingValue', 0)),
            'pcr': pcr,
            'top_oi': top_oi,
            'max_pain': max_pain,
            'timestamp': datetime.now().isoformat()
        }
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/live-expiries", response_model=List[str])
def api_get_live_expiries(index: str = Query(..., description="Index symbol, e.g. NIFTY")):
    """
    Fetch fresh list of available expiries without using stored data.
    """
    idx = _normalize_index_name(index)
    expiries = get_available_expiries(idx)
    if not expiries:
        raise HTTPException(status_code=404, detail=f"No expiries found for {idx}")
    return expiries

@router.get("/live-price", response_model=Dict[str, Any])
def api_get_live_option_price(
    index: str = Query(..., description="Index symbol, e.g. NIFTY"),
    strike: float = Query(..., description="Strike price"),
    expiry: str = Query(..., description="Expiry date"),
    option_type: str = Query(..., description="Option type: CE or PE")
):
    """
    Get live option price for specific strike, expiry, and type without using stored CSV.
    """
    idx = _normalize_index_name(index)
    option_type = option_type.upper()
    if option_type not in ['CE', 'PE']:
        raise HTTPException(status_code=400, detail="Option type must be CE or PE")
    
    try:
        resp = option_chain(idx)
        expiries = resp['records'].get('expiryDates', [])
        if expiry not in expiries:
            raise HTTPException(status_code=404, detail=f"Expiry '{expiry}' not available")
        
        df_processed = _prepare_option_chain_df(resp, expiry)
        # Find the row for the strike
        row = df_processed[df_processed['strikePrice'] == strike]
        if row.empty:
            raise HTTPException(status_code=404, detail=f"Strike {strike} not found for expiry {expiry}")
        
        # Get the price data
        price_data = {}
        if option_type == 'CE':
            price_data = {
                'strike': strike,
                'expiry': expiry,
                'type': 'CE',
                'lastPrice': row['CE_lastPrice'].iloc[0] if 'CE_lastPrice' in row.columns else None,
                'openInterest': row['CE_openInterest'].iloc[0] if 'CE_openInterest' in row.columns else None,
                'volume': row['CE_totalTradedVolume'].iloc[0] if 'CE_totalTradedVolume' in row.columns else None
            }
        else:  # PE
            price_data = {
                'strike': strike,
                'expiry': expiry,
                'type': 'PE',
                'lastPrice': row['PE_lastPrice'].iloc[0] if 'PE_lastPrice' in row.columns else None,
                'openInterest': row['PE_openInterest'].iloc[0] if 'PE_openInterest' in row.columns else None,
                'volume': row['PE_totalTradedVolume'].iloc[0] if 'PE_totalTradedVolume' in row.columns else None
            }
        
        return price_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# BSE Options Endpoints
# Note: BSE options data may have limited availability compared to NSE

@router.post("/bse/fetch", response_model=FetchResultMeta, status_code=201)
def api_fetch_bse_options(request: FetchOptionsRequest):
    """Fetch BSE options chain data (limited availability)"""
    idx = _normalize_index_name(request.index)
    
    # Check if it's a BSE index
    bse_indices = ['SENSEX', 'BANKEX', 'BSE100', 'BSE200', 'BSE500']
    if idx not in bse_indices:
        raise HTTPException(status_code=400, detail=f"BSE options only available for: {', '.join(bse_indices)}")
    
    try:
        # For BSE, we'll try to use yfinance as fallback since BSE options data is limited
        # This is a placeholder - actual BSE options data fetching would require BSE API access
        raise HTTPException(status_code=501, detail="BSE options data fetching not yet implemented. BSE options data requires specialized BSE API access.")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bse/fetch/json", response_model=DirectOptionsData)
def api_fetch_bse_options_json(request: FetchOptionsRequest):
    """Fetch BSE options data and return JSON directly (limited availability)"""
    idx = _normalize_index_name(request.index)
    
    # Check if it's a BSE index
    bse_indices = ['SENSEX', 'BANKEX', 'BSE100', 'BSE200', 'BSE500']
    if idx not in bse_indices:
        raise HTTPException(status_code=400, detail=f"BSE options only available for: {', '.join(bse_indices)}")
    
    try:
        # For BSE, we'll try to use yfinance as fallback since BSE options data is limited
        # This is a placeholder - actual BSE options data fetching would require BSE API access
        raise HTTPException(status_code=501, detail="BSE options data fetching not yet implemented. BSE options data requires specialized BSE API access.")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bse/live-chain", response_model=Dict[str, Any])
def api_get_bse_live_chain(
    index: str = Query(..., description="BSE Index symbol, e.g. SENSEX, BANKEX"),
    num_strikes: int = Query(10, description="Number of strikes around ATM")
):
    """Get live BSE options chain (limited availability)"""
    idx = _normalize_index_name(index)
    
    # Check if it's a BSE index
    bse_indices = ['SENSEX', 'BANKEX', 'BSE100', 'BSE200', 'BSE500']
    if idx not in bse_indices:
        raise HTTPException(status_code=400, detail=f"BSE options only available for: {', '.join(bse_indices)}")
    
    try:
        # For BSE, we'll try to use yfinance as fallback since BSE options data is limited
        # This is a placeholder - actual BSE options data fetching would require BSE API access
        raise HTTPException(status_code=501, detail="BSE options data fetching not yet implemented. BSE options data requires specialized BSE API access.")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bse/live-analytics", response_model=AnalyticsResponse)
def api_get_bse_live_analytics(
    index: str = Query(..., description="BSE Index symbol, e.g. SENSEX, BANKEX")
):
    """Get live BSE options analytics (limited availability)"""
    idx = _normalize_index_name(index)
    
    # Check if it's a BSE index
    bse_indices = ['SENSEX', 'BANKEX', 'BSE100', 'BSE200', 'BSE500']
    if idx not in bse_indices:
        raise HTTPException(status_code=400, detail=f"BSE options only available for: {', '.join(bse_indices)}")
    
    try:
        # For BSE, we'll try to use yfinance as fallback since BSE options data is limited
        # This is a placeholder - actual BSE options data fetching would require BSE API access
        raise HTTPException(status_code=501, detail="BSE options analytics not yet implemented. BSE options data requires specialized BSE API access.")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bse/live-price", response_model=Dict[str, Any])
def api_get_bse_live_option_price(
    index: str = Query(..., description="BSE Index symbol, e.g. SENSEX"),
    strike: float = Query(..., description="Strike price"),
    expiry: str = Query(..., description="Expiry date"),
    option_type: str = Query(..., description="Option type: CE or PE")
):
    """Get live BSE option price (limited availability)"""
    idx = _normalize_index_name(index)
    
    # Check if it's a BSE index
    bse_indices = ['SENSEX', 'BANKEX', 'BSE100', 'BSE200', 'BSE500']
    if idx not in bse_indices:
        raise HTTPException(status_code=400, detail=f"BSE options only available for: {', '.join(bse_indices)}")
    
    try:
        # For BSE, we'll try to use yfinance as fallback since BSE options data is limited
        # This is a placeholder - actual BSE options data fetching would require BSE API access
        raise HTTPException(status_code=501, detail="BSE options data fetching not yet implemented. BSE options data requires specialized BSE API access.")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
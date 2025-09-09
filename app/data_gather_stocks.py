import os
import time
import json
import bisect
from datetime import datetime
import pandas as pd
from nsepython import option_chain, nse_quote

# ==============================================================================
# SECTION 1: UTILITY AND HELPER FUNCTIONS
# ==============================================================================

def _expand_side(df: pd.DataFrame, side: str) -> pd.DataFrame:
    """
    Helper function to expand the 'CE' or 'PE' dictionary column into separate columns.
    """
    valid_rows = df[df[side].apply(lambda x: isinstance(x, dict))]
    if valid_rows.empty:
        return pd.DataFrame()
        
    side_data = valid_rows[side].apply(pd.Series)
    side_data = side_data.add_prefix(f'{side}_')
    return side_data

def get_available_expiries(index_name: str) -> list:
    """
    Connects to NSE and fetches the list of all available expiry dates for an index.

    Args:
        index_name (str): The symbol of the index (e.g., "NIFTY", "BANKNIFTY").

    Returns:
        list: A list of available expiry date strings.
    """
    try:
        print(f"Fetching available expiries for {index_name}...")
        resp = option_chain(index_name)
        if 'records' in resp and 'expiryDates' in resp['records']:
            expiries = resp['records']['expiryDates']
            print(f"Found {len(expiries)} expiry dates.")
            return expiries
        else:
            print("Could not find expiry dates in the response.")
            return []
    except Exception as e:
        print(f"Error fetching expiries for {index_name}: {e}")
        return []

def fetch_index_price(index_name: str) -> dict:
    """
    Fetches the latest price data for a given NSE index.

    Args:
        index_name (str): The symbol of the index (e.g., "NIFTY", "BANKNIFTY").

    Returns:
        dict: A dictionary with the latest price information or an error.
    """
    try:
        print(f"Fetching latest price for index: {index_name}...")
        quote = nse_quote(index_name)

        # Debug logging
        print(f"NSE Quote response for {index_name}: {quote}")

        if not quote:
            return {'error': f"No data found for index '{index_name}'. NSE quote returned None."}

        # Determine last price: different NSE responses use different keys for indices vs stocks
        last_price_str = None
        if isinstance(quote, dict):
            # preferred key
            if 'lastPrice' in quote:
                last_price_str = quote['lastPrice']
            # index responses often include 'underlyingValue'
            elif 'underlyingValue' in quote:
                last_price_str = quote['underlyingValue']
            # some responses nest info under 'underlyingInfo'
            elif isinstance(quote.get('underlyingInfo'), dict) and 'lastPrice' in quote.get('underlyingInfo'):
                last_price_str = quote['underlyingInfo']['lastPrice']

        if last_price_str is None:
            return {'error': f"No lastPrice or underlyingValue found in NSE quote for '{index_name}'. Available keys: {list(quote.keys()) if isinstance(quote, dict) else 'Not a dict'}"}

        # Handle comma-separated prices
        # last_price_str may already be numeric
        if isinstance(last_price_str, str):
            last_price_str = last_price_str.replace(',', '')

        # normalize to float
        try:
            if isinstance(last_price_str, str):
                last_price_str = last_price_str.replace(',', '')
            last_price = float(last_price_str)
        except Exception:
            return {'error': f"Unable to parse last price for '{index_name}': {last_price_str!r}"}

        # pChange and change may not be present for index responses; provide safe defaults
        pchange_raw = quote.get('pChange', quote.get('pChangeInPercent', 0)) if isinstance(quote, dict) else 0
        change_raw = quote.get('change', 0) if isinstance(quote, dict) else 0
        timestamp_val = None
        # common timestamp keys
        for k in ('secDate', 'fut_timestamp', 'opt_timestamp', 'timestamp'):
            if isinstance(quote, dict) and k in quote:
                timestamp_val = quote.get(k)
                break
        if not timestamp_val:
            timestamp_val = datetime.now().strftime("%d %b %Y %H:%M:%S")

        price_data = {
            'symbol': index_name,
            'lastPrice': last_price,
            'pChange': float(pchange_raw) if isinstance(pchange_raw, (int, float, str)) else 0,
            'change': float(change_raw) if isinstance(change_raw, (int, float, str)) else 0,
            'timestamp': timestamp_val
        }
        return price_data
    except Exception as e:
        print(f"Error in fetch_index_price for {index_name}: {e}")
        return {'error': f"An error occurred while fetching index price for '{index_name}': {e}"}

def fetch_stock_price(stock_symbol: str) -> dict:
    """
    Fetches the latest price data for a given NSE stock symbol.

    Args:
        stock_symbol (str): The NSE symbol for the stock (e.g., "RELIANCE", "INFY").

    Returns:
        dict: A dictionary with the latest price information or an error.
    """
    try:
        print(f"Fetching latest price for stock: {stock_symbol}...")
        quote = nse_quote(stock_symbol)
        
        info = quote.get('info', {})
        price_info = quote.get('priceInfo', {})
        
        if not info or 'symbol' not in info or not price_info:
             return {'error': f"No data found for stock '{stock_symbol}'. Please use a valid NSE symbol."}
             
        price_data = {
            'symbol': info.get('symbol'),
            'companyName': info.get('companyName'),
            'lastPrice': price_info.get('lastPrice'),
            'pChange': price_info.get('pChange'),
            'change': price_info.get('change'),
            'timestamp': quote.get('metadata', {}).get('lastUpdateTime', datetime.now().strftime("%d-%b-%Y %H:%M:%S"))
        }
        return price_data
    except Exception as e:
        return {'error': f"An error occurred while fetching stock price for '{stock_symbol}': {e}"}

# ==============================================================================
# SECTION 2: CORE ANALYTICAL FUNCTIONS
# ==============================================================================

def calculate_pcr(df: pd.DataFrame) -> dict:
    # ... (function remains unchanged) ...
    pcr_data = {'pcr_by_oi': 0, 'pcr_by_volume': 0}
    if 'PE_openInterest' in df.columns and 'CE_openInterest' in df.columns:
        total_pe_oi = df['PE_openInterest'].sum()
        total_ce_oi = df['CE_openInterest'].sum()
        if total_ce_oi > 0:
            pcr_data['pcr_by_oi'] = round(total_pe_oi / total_ce_oi, 2)
    if 'PE_totalTradedVolume' in df.columns and 'CE_totalTradedVolume' in df.columns:
        total_pe_volume = df['PE_totalTradedVolume'].sum()
        total_ce_volume = df['CE_totalTradedVolume'].sum()
        if total_ce_volume > 0:
            pcr_data['pcr_by_volume'] = round(total_pe_volume / total_ce_volume, 2)
    return pcr_data

def find_high_oi_strikes(df: pd.DataFrame, top_n: int = 5) -> dict:
    # ... (function remains unchanged) ...
    results = {'resistance_strikes': [], 'support_strikes': []}
    if 'CE_openInterest' in df.columns:
        top_calls = df.nlargest(top_n, 'CE_openInterest')[['strikePrice', 'CE_openInterest']]
        results['resistance_strikes'] = top_calls.to_dict('records')
    if 'PE_openInterest' in df.columns:
        top_puts = df.nlargest(top_n, 'PE_openInterest')[['strikePrice', 'PE_openInterest']]
        results['support_strikes'] = top_puts.to_dict('records')
    return results

def calculate_max_pain(df: pd.DataFrame) -> dict:
    # ... (function remains unchanged) ...
    strikes = sorted(df['strikePrice'].unique())
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
    return {
        'max_pain_strike': int(max_pain_strike),
        'total_loss_value': int(total_loss_at_strike[max_pain_strike])
    }

# ==============================================================================
# SECTION 3: CORE DATA FETCHING AND SAVING FUNCTIONS
# ==============================================================================

def fetch_and_save_option_chain(index_name: str, num_strikes_around_atm: int = 25):
    # ... (function remains unchanged) ...
    start_time = time.time()
    output_dir = "option_chain_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    try:
        print(f"Fetching live option chain for '{index_name}' from NSE...")
        resp = option_chain(index_name)
        if not (isinstance(resp, dict) and 'records' in resp and 'data' in resp['records']):
             raise RuntimeError(f"Invalid response structure from NSE. Full response: {resp}")
        df_full = pd.DataFrame(resp['records']['data'])
        if df_full.empty:
            raise RuntimeError("NSE returned no option chain data.")
        if 'strikePrice' not in df_full.columns:
            raise RuntimeError("Column 'strikePrice' is missing from the data.")
        df_full['strikePrice'] = pd.to_numeric(df_full['strikePrice'], errors='coerce')
        nearest_expiry = resp['records']['expiryDates'][0]
        print(f"Nearest expiry date found: {nearest_expiry}")
        df = df_full[df_full['expiryDate'] == nearest_expiry].copy()
        if df.empty:
            raise RuntimeError(f"No option data found for the nearest expiry: {nearest_expiry}")
        ce_data = _expand_side(df, 'CE')
        pe_data = _expand_side(df, 'PE')
        df_processed = pd.concat([df[['strikePrice', 'expiryDate']], ce_data, pe_data], axis=1)
        underlying_value = float(resp['records']['underlyingValue'])
        strikes = sorted(df_processed['strikePrice'].unique())
        atm_strike_index = bisect.bisect_left(strikes, underlying_value)
        if atm_strike_index > 0 and abs(strikes[atm_strike_index-1] - underlying_value) < abs(strikes[atm_strike_index] - underlying_value):
            atm_strike_index -= 1
        low_index = max(0, atm_strike_index - num_strikes_around_atm)
        high_index = min(len(strikes) - 1, atm_strike_index + num_strikes_around_atm)
        selected_strikes = strikes[low_index:high_index+1]
        df_final = df_processed[df_processed['strikePrice'].isin(selected_strikes)].sort_values(['strikePrice']).reset_index(drop=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_expiry = str(nearest_expiry).replace(' ', '_').replace('/', '-')
        base_filename = f"{index_name.lower()}_option_chain_{safe_expiry}_{timestamp}"
        csv_path = os.path.join(output_dir, f"{base_filename}.csv")
        meta_path = os.path.join(output_dir, f"{base_filename}.json")
        df_final.to_csv(csv_path, index=False)
        metadata = {
            'createdAtUTC': datetime.utcnow().isoformat(),
            'indexName': index_name,
            'nearestExpiry': nearest_expiry,
            'underlyingValue': float(underlying_value),
            'atmStrike': int(strikes[atm_strike_index]),
            'selectedStrikesRange': [int(selected_strikes[0]), int(selected_strikes[-1])],
            'totalStrikesFetched': int(len(df_final))
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        elapsed = time.time() - start_time
        print("\n--- SUCCESS (Nearest Expiry) ---")
        print(f"Saved CSV: {csv_path}")
        print(f"Saved Metadata: {meta_path}")
        print(f"Rows: {len(df_final)} | Strikes: {selected_strikes[0]} to {selected_strikes[-1]} | ATM ~{underlying_value:.2f}")
        print(f"Elapsed Time: {elapsed:.2f} seconds")
    except Exception as exc:
        print(f"\n--- ERROR ---")
        print(f"Runner failed for index '{index_name}': {exc}")
        raise

def fetch_specific_expiry_option_chain(index_name: str, expiry_date: str, num_strikes_around_atm: int = 25):
    # ... (function remains unchanged) ...
    start_time = time.time()
    output_dir = "option_chain_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    try:
        print(f"Fetching live option chain for '{index_name}' for expiry '{expiry_date}' from NSE...")
        resp = option_chain(index_name)
        if not (isinstance(resp, dict) and 'records' in resp and 'data' in resp['records']):
             raise RuntimeError(f"Invalid response structure from NSE. Full response: {resp}")
        available_expiries = resp['records']['expiryDates']
        if expiry_date not in available_expiries:
            raise ValueError(f"Expiry date '{expiry_date}' not found. Available dates are: {available_expiries}")
        df_full = pd.DataFrame(resp['records']['data'])
        if 'strikePrice' not in df_full.columns:
            raise RuntimeError("Column 'strikePrice' is missing.")
        df_full['strikePrice'] = pd.to_numeric(df_full['strikePrice'], errors='coerce')
        df = df_full[df_full['expiryDate'] == expiry_date].copy()
        if df.empty:
            raise RuntimeError(f"No option data found for the specified expiry: {expiry_date}")
        ce_data = _expand_side(df, 'CE')
        pe_data = _expand_side(df, 'PE')
        df_processed = pd.concat([df[['strikePrice', 'expiryDate']], ce_data, pe_data], axis=1)
        underlying_value = float(resp['records']['underlyingValue'])
        strikes = sorted(df_processed['strikePrice'].unique())
        atm_strike_index = bisect.bisect_left(strikes, underlying_value)
        if atm_strike_index > 0 and abs(strikes[atm_strike_index-1] - underlying_value) < abs(strikes[atm_strike_index] - underlying_value):
            atm_strike_index -= 1
        low_index = max(0, atm_strike_index - num_strikes_around_atm)
        high_index = min(len(strikes) - 1, atm_strike_index + num_strikes_around_atm)
        selected_strikes = strikes[low_index:high_index+1]
        df_final = df_processed[df_processed['strikePrice'].isin(selected_strikes)].sort_values(['strikePrice']).reset_index(drop=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_expiry = str(expiry_date).replace(' ', '_').replace('/', '-')
        base_filename = f"{index_name.lower()}_option_chain_{safe_expiry}_{timestamp}"
        csv_path = os.path.join(output_dir, f"{base_filename}.csv")
        meta_path = os.path.join(output_dir, f"{base_filename}.json")
        df_final.to_csv(csv_path, index=False)
        metadata = {
            'createdAtUTC': datetime.utcnow().isoformat(),
            'indexName': index_name,
            'selectedExpiry': expiry_date,
            'underlyingValue': float(underlying_value),
            'atmStrike': int(strikes[atm_strike_index]),
            'selectedStrikesRange': [int(selected_strikes[0]), int(selected_strikes[-1])],
            'totalStrikesFetched': int(len(df_final))
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        elapsed = time.time() - start_time
        print("\n--- SUCCESS (Specific Expiry) ---")
        print(f"Saved CSV: {csv_path}")
        print(f"Saved Metadata: {meta_path}")
        print(f"Rows: {len(df_final)} | Strikes: {selected_strikes[0]} to {selected_strikes[-1]} | ATM ~{underlying_value:.2f}")
        print(f"Elapsed Time: {elapsed:.2f} seconds")
    except Exception as exc:
        print(f"\n--- ERROR ---")
        print(f"Runner failed for index '{index_name}' with expiry '{expiry_date}': {exc}")
        raise

# ==============================================================================
# SECTION 4: EXAMPLE WORKFLOW AND USAGE OF NEW FUNCTIONS
# ==============================================================================

if __name__ == "__main__":
    # This block runs when you execute the script directly from the terminal.
    
    print("--- Running Example: Fetching Live Prices ---")
    nifty_price = fetch_index_price("NIFTY")
    print(f"--> NIFTY Price Data: {nifty_price}")
    
    reliance_price = fetch_stock_price("RELIANCE")
    print(f"--> RELIANCE Price Data: {reliance_price}")
    
    invalid_stock = fetch_stock_price("INVALIDSTOCK")
    print(f"--> Invalid Stock Data Check: {invalid_stock}")

    print("\n" + "="*50 + "\n")
    
    print("--- Running Example: Full Option Chain Analysis Workflow for NIFTY ---")
    
    # Step 1: Get available expiry dates for NIFTY
    nifty_expiries = get_available_expiries("NIFTY")
    if not nifty_expiries:
        print("Could not retrieve NIFTY expiries. Exiting analysis.")
    else:
        # Step 2: Fetch the full option chain data for the nearest expiry
        try:
            fetch_and_save_option_chain(index_name="NIFTY", num_strikes_around_atm=50)
            
            # Step 3: Read the saved CSV and perform analysis
            output_dir = "option_chain_data"
            nifty_files = [f for f in os.listdir(output_dir) if f.startswith('nifty') and f.endswith('.csv')]
            latest_nifty_file = sorted(nifty_files, reverse=True)[0]
            latest_csv_path = os.path.join(output_dir, latest_nifty_file)
            
            print(f"\nReading '{latest_csv_path}' for analysis...")
            df_for_analysis = pd.read_csv(latest_csv_path)

            # Step 4: Run analytical functions and print results
            print("\n--- ANALYTICAL RESULTS FOR NIFTY ---")

            pcr_results = calculate_pcr(df_for_analysis)
            print(f"Put-Call Ratio (by OI): {pcr_results['pcr_by_oi']}")
            
            oi_levels = find_high_oi_strikes(df_for_analysis, top_n=5)
            print("\nTop 5 Resistance Strikes (Highest Call OI):")
            for item in oi_levels['resistance_strikes']:
                print(f"  Strike: {item['strikePrice']}, OI: {item['CE_openInterest']}")
            
            print("\nTop 5 Support Strikes (Highest Put OI):")
            for item in oi_levels['support_strikes']:
                print(f"  Strike: {item['strikePrice']}, OI: {item['PE_openInterest']}")
            
            max_pain_result = calculate_max_pain(df_for_analysis)
            print(f"\nMax Pain Strike: {max_pain_result['max_pain_strike']}")

        except (ValueError, RuntimeError) as e:
            print(f"\nCould not complete NIFTY analysis. Reason: {e}")


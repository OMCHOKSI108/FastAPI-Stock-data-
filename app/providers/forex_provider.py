# app/providers/forex_provider.py
import yfinance as yf
import asyncio
import pandas as pd
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Common forex pairs
FOREX_PAIRS = {
    "EURUSD": {"base": "EUR", "quote": "USD", "description": "Euro vs US Dollar"},
    "GBPUSD": {"base": "GBP", "quote": "USD", "description": "British Pound vs US Dollar"},
    "USDJPY": {"base": "USD", "quote": "JPY", "description": "US Dollar vs Japanese Yen"},
    "USDCHF": {"base": "USD", "quote": "CHF", "description": "US Dollar vs Swiss Franc"},
    "AUDUSD": {"base": "AUD", "quote": "USD", "description": "Australian Dollar vs US Dollar"},
    "USDCAD": {"base": "USD", "quote": "CAD", "description": "US Dollar vs Canadian Dollar"},
    "NZDUSD": {"base": "NZD", "quote": "USD", "description": "New Zealand Dollar vs US Dollar"},
    "EURJPY": {"base": "EUR", "quote": "JPY", "description": "Euro vs Japanese Yen"},
    "GBPJPY": {"base": "GBP", "quote": "JPY", "description": "British Pound vs Japanese Yen"},
    "EURGBP": {"base": "EUR", "quote": "GBP", "description": "Euro vs British Pound"},
    "EURCHF": {"base": "EUR", "quote": "CHF", "description": "Euro vs Swiss Franc"},
    "GBPCHF": {"base": "GBP", "quote": "CHF", "description": "British Pound vs Swiss Franc"},
    "AUDJPY": {"base": "AUD", "quote": "JPY", "description": "Australian Dollar vs Japanese Yen"},
    "CADJPY": {"base": "CAD", "quote": "JPY", "description": "Canadian Dollar vs Japanese Yen"},
    "CHFJPY": {"base": "CHF", "quote": "JPY", "description": "Swiss Franc vs Japanese Yen"},
    "NZDJPY": {"base": "NZD", "quote": "JPY", "description": "New Zealand Dollar vs Japanese Yen"},
    "EURAUD": {"base": "EUR", "quote": "AUD", "description": "Euro vs Australian Dollar"},
    "GBPAUD": {"base": "GBP", "quote": "AUD", "description": "British Pound vs Australian Dollar"},
    "AUDCHF": {"base": "AUD", "quote": "CHF", "description": "Australian Dollar vs Swiss Franc"},
    "AUDCAD": {"base": "AUD", "quote": "CAD", "description": "Australian Dollar vs Canadian Dollar"},
    "AUDNZD": {"base": "AUD", "quote": "NZD", "description": "Australian Dollar vs New Zealand Dollar"},
    "CADCHF": {"base": "CAD", "quote": "CHF", "description": "Canadian Dollar vs Swiss Franc"},
    "NZDCHF": {"base": "NZD", "quote": "CHF", "description": "New Zealand Dollar vs Swiss Franc"},
    "GBPCAD": {"base": "GBP", "quote": "CAD", "description": "British Pound vs Canadian Dollar"},
    "EURCAD": {"base": "EUR", "quote": "CAD", "description": "Euro vs Canadian Dollar"},
    "EURNZD": {"base": "EUR", "quote": "NZD", "description": "Euro vs New Zealand Dollar"},
    "GBPNZD": {"base": "GBP", "quote": "NZD", "description": "British Pound vs New Zealand Dollar"},
    "USDNOK": {"base": "USD", "quote": "NOK", "description": "US Dollar vs Norwegian Krone"},
    "USDSEK": {"base": "USD", "quote": "SEK", "description": "US Dollar vs Swedish Krona"},
    "USDDKK": {"base": "USD", "quote": "DKK", "description": "US Dollar vs Danish Krone"},
    "USDSGD": {"base": "USD", "quote": "SGD", "description": "US Dollar vs Singapore Dollar"},
    "USDHKD": {"base": "USD", "quote": "HKD", "description": "US Dollar vs Hong Kong Dollar"},
    "USDKRW": {"base": "USD", "quote": "KRW", "description": "US Dollar vs South Korean Won"},
    "USDZAR": {"base": "USD", "quote": "ZAR", "description": "US Dollar vs South African Rand"},
    "USDMXN": {"base": "USD", "quote": "MXN", "description": "US Dollar vs Mexican Peso"},
    "USDBRL": {"base": "USD", "quote": "BRL", "description": "US Dollar vs Brazilian Real"},
    "USDRUB": {"base": "USD", "quote": "RUB", "description": "US Dollar vs Russian Ruble"},
    "USDTRY": {"base": "USD", "quote": "TRY", "description": "US Dollar vs Turkish Lira"},
    "USDINR": {"base": "USD", "quote": "INR", "description": "US Dollar vs Indian Rupee"},
    "USDCNY": {"base": "USD", "quote": "CNY", "description": "US Dollar vs Chinese Yuan"},
    "USDTHB": {"base": "USD", "quote": "THB", "description": "US Dollar vs Thai Baht"},
    "USDMYR": {"base": "USD", "quote": "MYR", "description": "US Dollar vs Malaysian Ringgit"},
    "USDIDR": {"base": "USD", "quote": "IDR", "description": "US Dollar vs Indonesian Rupiah"},
    "USDPHP": {"base": "USD", "quote": "PHP", "description": "US Dollar vs Philippine Peso"},
    "USDVND": {"base": "USD", "quote": "VND", "description": "US Dollar vs Vietnamese Dong"},
    "USDTWD": {"base": "USD", "quote": "TWD", "description": "US Dollar vs Taiwan Dollar"},
    "USDARS": {"base": "USD", "quote": "ARS", "description": "US Dollar vs Argentine Peso"},
    "USDCLP": {"base": "USD", "quote": "CLP", "description": "US Dollar vs Chilean Peso"},
    "USDCOP": {"base": "USD", "quote": "COP", "description": "US Dollar vs Colombian Peso"},
    "USDPEN": {"base": "USD", "quote": "PEN", "description": "US Dollar vs Peruvian Sol"},
    "USDPLN": {"base": "USD", "quote": "PLN", "description": "US Dollar vs Polish Zloty"},
    "USDCZK": {"base": "USD", "quote": "CZK", "description": "US Dollar vs Czech Koruna"},
    "USDHUF": {"base": "USD", "quote": "HUF", "description": "US Dollar vs Hungarian Forint"},
    "USDRON": {"base": "USD", "quote": "RON", "description": "US Dollar vs Romanian Leu"},
    "USDBGN": {"base": "USD", "quote": "BGN", "description": "US Dollar vs Bulgarian Lev"},
    "USDHRK": {"base": "USD", "quote": "HRK", "description": "US Dollar vs Croatian Kuna"},
    "USDRSD": {"base": "USD", "quote": "RSD", "description": "US Dollar vs Serbian Dinar"},
    "USDMKD": {"base": "USD", "quote": "MKD", "description": "US Dollar vs Macedonian Denar"},
    "USDALL": {"base": "USD", "quote": "ALL", "description": "US Dollar vs Albanian Lek"},
    "USDBAM": {"base": "USD", "quote": "BAM", "description": "US Dollar vs Bosnia-Herzegovina Convertible Mark"},
    "USDBYN": {"base": "USD", "quote": "BYN", "description": "US Dollar vs Belarusian Ruble"},
    "USDAMD": {"base": "USD", "quote": "AMD", "description": "US Dollar vs Armenian Dram"},
    "USDGEL": {"base": "USD", "quote": "GEL", "description": "US Dollar vs Georgian Lari"},
    "USDAZN": {"base": "USD", "quote": "AZN", "description": "US Dollar vs Azerbaijani Manat"},
    "USDKZT": {"base": "USD", "quote": "KZT", "description": "US Dollar vs Kazakhstani Tenge"},
    "USDKGS": {"base": "USD", "quote": "KGS", "description": "US Dollar vs Kyrgyzstani Som"},
    "USDTJS": {"base": "USD", "quote": "TJS", "description": "US Dollar vs Tajikistani Somoni"},
    "USDTMT": {"base": "USD", "quote": "TMT", "description": "US Dollar vs Turkmenistani Manat"},
    "USDUZS": {"base": "USD", "quote": "UZS", "description": "US Dollar vs Uzbekistani Som"},
    "USDMNT": {"base": "USD", "quote": "MNT", "description": "US Dollar vs Mongolian Tugrik"},
    "USDKPW": {"base": "USD", "quote": "KPW", "description": "US Dollar vs North Korean Won"},
    "USDLBP": {"base": "USD", "quote": "LBP", "description": "US Dollar vs Lebanese Pound"},
    "USDSYP": {"base": "USD", "quote": "SYP", "description": "US Dollar vs Syrian Pound"},
    "USDYER": {"base": "USD", "quote": "YER", "description": "US Dollar vs Yemeni Rial"},
    "USDSDG": {"base": "USD", "quote": "SDG", "description": "US Dollar vs Sudanese Pound"},
    "USDSOS": {"base": "USD", "quote": "SOS", "description": "US Dollar vs Somali Shilling"},
    "USDDJF": {"base": "USD", "quote": "DJF", "description": "US Dollar vs Djiboutian Franc"},
    "USDKMF": {"base": "USD", "quote": "KMF", "description": "US Dollar vs Comorian Franc"},
    "USDMGA": {"base": "USD", "quote": "MGA", "description": "US Dollar vs Malagasy Ariary"},
    "USDMUR": {"base": "USD", "quote": "MUR", "description": "US Dollar vs Mauritian Rupee"},
    "USDMVR": {"base": "USD", "quote": "MVR", "description": "US Dollar vs Maldivian Rufiyaa"},
    "USDMWK": {"base": "USD", "quote": "MWK", "description": "US Dollar vs Malawian Kwacha"},
    "USDMZN": {"base": "USD", "quote": "MZN", "description": "US Dollar vs Mozambican Metical"},
    "USDNAD": {"base": "USD", "quote": "NAD", "description": "US Dollar vs Namibian Dollar"},
    "USDSZL": {"base": "USD", "quote": "SZL", "description": "US Dollar vs Swazi Lilangeni"},
    "USDBWP": {"base": "USD", "quote": "BWP", "description": "US Dollar vs Botswana Pula"},
    "USDLRD": {"base": "USD", "quote": "LRD", "description": "US Dollar vs Liberian Dollar"},
    "USDSLL": {"base": "USD", "quote": "SLL", "description": "US Dollar vs Sierra Leonean Leone"},
    "USDGMD": {"base": "USD", "quote": "GMD", "description": "US Dollar vs Gambian Dalasi"},
    "USDGNF": {"base": "USD", "quote": "GNF", "description": "US Dollar vs Guinean Franc"},
    "USDLYD": {"base": "USD", "quote": "LYD", "description": "US Dollar vs Libyan Dinar"},
    "USDTND": {"base": "USD", "quote": "TND", "description": "US Dollar vs Tunisian Dinar"},
    "USDDZD": {"base": "USD", "quote": "DZD", "description": "US Dollar vs Algerian Dinar"},
    "USDMAD": {"base": "USD", "quote": "MAD", "description": "US Dollar vs Moroccan Dirham"},
    "USDBHD": {"base": "USD", "quote": "BHD", "description": "US Dollar vs Bahraini Dinar"},
    "USDKWD": {"base": "USD", "quote": "KWD", "description": "US Dollar vs Kuwaiti Dinar"},
    "USDOMR": {"base": "USD", "quote": "OMR", "description": "US Dollar vs Omani Rial"},
    "USDQAR": {"base": "USD", "quote": "QAR", "description": "US Dollar vs Qatari Riyal"},
    "USDSAR": {"base": "USD", "quote": "SAR", "description": "US Dollar vs Saudi Riyal"},
    "USDAED": {"base": "USD", "quote": "AED", "description": "US Dollar vs UAE Dirham"},
    "USDJOD": {"base": "USD", "quote": "JOD", "description": "US Dollar vs Jordanian Dinar"},
    "USDLBP": {"base": "USD", "quote": "LBP", "description": "US Dollar vs Lebanese Pound"},
    "USDSYP": {"base": "USD", "quote": "SYP", "description": "US Dollar vs Syrian Pound"},
    "USDYER": {"base": "USD", "quote": "YER", "description": "US Dollar vs Yemeni Rial"},
    "USDSDG": {"base": "USD", "quote": "SDG", "description": "US Dollar vs Sudanese Pound"},
    "USDSOS": {"base": "USD", "quote": "SOS", "description": "US Dollar vs Somali Shilling"},
    "USDDJF": {"base": "USD", "quote": "DJF", "description": "US Dollar vs Djiboutian Franc"},
    "USDKMF": {"base": "USD", "quote": "KMF", "description": "US Dollar vs Comorian Franc"},
    "USDMGA": {"base": "USD", "quote": "MGA", "description": "US Dollar vs Malagasy Ariary"},
    "USDMUR": {"base": "USD", "quote": "MUR", "description": "US Dollar vs Mauritian Rupee"},
    "USDMVR": {"base": "USD", "quote": "MVR", "description": "US Dollar vs Maldivian Rufiyaa"},
    "USDMWK": {"base": "USD", "quote": "MWK", "description": "US Dollar vs Malawian Kwacha"},
    "USDMZN": {"base": "USD", "quote": "MZN", "description": "US Dollar vs Mozambican Metical"},
    "USDNAD": {"base": "USD", "quote": "NAD", "description": "US Dollar vs Namibian Dollar"},
    "USDSZL": {"base": "USD", "quote": "SZL", "description": "US Dollar vs Swazi Lilangeni"},
    "USDBWP": {"base": "USD", "quote": "BWP", "description": "US Dollar vs Botswana Pula"},
    "USDLRD": {"base": "USD", "quote": "LRD", "description": "US Dollar vs Liberian Dollar"},
    "USDSLL": {"base": "USD", "quote": "SLL", "description": "US Dollar vs Sierra Leonean Leone"},
    "USDGMD": {"base": "USD", "quote": "GMD", "description": "US Dollar vs Gambian Dalasi"},
    "USDGNF": {"base": "USD", "quote": "GNF", "description": "US Dollar vs Guinean Franc"},
    "USDLYD": {"base": "USD", "quote": "LYD", "description": "US Dollar vs Libyan Dinar"},
    "USDTND": {"base": "USD", "quote": "TND", "description": "US Dollar vs Tunisian Dinar"},
    "USDDZD": {"base": "USD", "quote": "DZD", "description": "US Dollar vs Algerian Dinar"},
    "USDMAD": {"base": "USD", "quote": "MAD", "description": "US Dollar vs Moroccan Dirham"},
    "USDBHD": {"base": "USD", "quote": "BHD", "description": "US Dollar vs Bahraini Dinar"},
    "USDKWD": {"base": "USD", "quote": "KWD", "description": "US Dollar vs Kuwaiti Dinar"},
    "USDOMR": {"base": "USD", "quote": "OMR", "description": "US Dollar vs Omani Rial"},
    "USDQAR": {"base": "USD", "quote": "QAR", "description": "US Dollar vs Qatari Riyal"},
    "USDSAR": {"base": "USD", "quote": "SAR", "description": "US Dollar vs Saudi Riyal"},
    "USDAED": {"base": "USD", "quote": "AED", "description": "US Dollar vs UAE Dirham"},
    "USDJOD": {"base": "USD", "quote": "JOD", "description": "US Dollar vs Jordanian Dinar"}
}

async def get_forex_quote(symbol: str) -> Optional[dict]:
    """Fetch current forex quote for a currency pair."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_forex_quote, symbol)

def _sync_forex_quote(symbol: str):
    try:
        # yfinance forex symbols are formatted as EURUSD=X
        yf_symbol = f"{symbol}=X"
        ticker = yf.Ticker(yf_symbol)

        # Get current data
        data = ticker.history(period="1d", interval="1m")
        if data.empty:
            return None

        last = data.iloc[-1]
        price = float(last['Close'])

        # Get bid/ask if available
        try:
            info = ticker.info
            bid = info.get('bid')
            ask = info.get('ask')
        except:
            bid = None
            ask = None

        pair_info = FOREX_PAIRS.get(symbol.upper(), {})
        base_currency = pair_info.get('base', symbol[:3])
        quote_currency = pair_info.get('quote', symbol[3:])

        return {
            "symbol": symbol.upper(),
            "base_currency": base_currency,
            "quote_currency": quote_currency,
            "price": price,
            "bid": bid,
            "ask": ask,
            "timestamp": last.name.to_pydatetime().isoformat()
        }
    except Exception as e:
        logger.error(f"Forex quote fetch error for {symbol}: {e}")
        return None

async def get_forex_historical(symbol: str, period: str = "1d") -> Optional[list]:
    """Fetch historical forex data."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_forex_historical, symbol, period)

def _sync_forex_historical(symbol: str, period: str) -> Optional[list]:
    try:
        yf_symbol = f"{symbol}=X"
        ticker = yf.Ticker(yf_symbol)
        data = ticker.history(period=period)

        if data.empty:
            return None

        # Convert to list of dicts
        historical = []
        for idx, row in data.iterrows():
            historical.append({
                "timestamp": idx.isoformat(),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0
            })
        return historical
    except Exception as e:
        logger.error(f"Forex historical fetch error for {symbol}: {e}")
        return None

def get_available_pairs() -> List[Dict[str, str]]:
    """Get list of available forex pairs."""
    return [
        {
            "symbol": symbol,
            "base_currency": info["base"],
            "quote_currency": info["quote"],
            "description": info["description"]
        }
        for symbol, info in FOREX_PAIRS.items()
    ]

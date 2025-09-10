from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import os
import json
import pandas as pd
from datetime import datetime
from ..schemas import AnalyticsResponse, FetchResultMeta

router = APIRouter()

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'option_chain_data')

def convert_expiry_format(expiry: str) -> str:
    """Convert DDMMYY format to DD-MMM-YYYY format for NSE"""
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
            raise ValueError(f"Invalid month in expiry date: {month}")
        
        return f"{day}-{month_names[month]}-{year}"
    else:
        # Assume it's already in DD-MMM-YYYY format
        return expiry

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

@router.get("/pcr", response_model=Dict[str, float])
def get_pcr(index: str = Query(...), expiry: Optional[str] = Query(None, description="Specific expiry date (DDMMYY format, optional)"), limit: int = Query(500, gt=0, le=5000)):
    """Get Put-Call Ratio for the latest option chain data"""
    idx = index.strip().upper()
    files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(f"{idx.lower()}_") and f.endswith('.csv')]
    if not files:
        raise HTTPException(status_code=404, detail=f"No saved option-chain CSVs found for {idx}")
    
    # Filter by expiry if specified
    if expiry:
        try:
            nse_expiry = convert_expiry_format(expiry)
            files = [f for f in files if nse_expiry.replace(' ', '_').replace('/', '-') in f]
            if not files:
                raise HTTPException(status_code=404, detail=f"No saved option-chain CSVs found for {idx} with expiry {nse_expiry} (input: {expiry})")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    latest_file = sorted(files, reverse=True)[0]
    csv_path = os.path.join(OUTPUT_DIR, latest_file)
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to read saved CSV")
    if limit:
        df = df.head(limit)
    pcr = calculate_pcr(df)
    return pcr

@router.get("/max-pain", response_model=Dict[str, Any])
def get_max_pain(index: str = Query(...), expiry: Optional[str] = Query(None, description="Specific expiry date (DDMMYY format, optional)"), limit: int = Query(500, gt=0, le=5000)):
    """Get Max Pain calculation for the latest option chain data"""
    idx = index.strip().upper()
    files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(f"{idx.lower()}_") and f.endswith('.csv')]
    if not files:
        raise HTTPException(status_code=404, detail=f"No saved option-chain CSVs found for {idx}")
    
    # Filter by expiry if specified
    if expiry:
        try:
            nse_expiry = convert_expiry_format(expiry)
            files = [f for f in files if nse_expiry.replace(' ', '_').replace('/', '-') in f]
            if not files:
                raise HTTPException(status_code=404, detail=f"No saved option-chain CSVs found for {idx} with expiry {nse_expiry} (input: {expiry})")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    latest_file = sorted(files, reverse=True)[0]
    csv_path = os.path.join(OUTPUT_DIR, latest_file)
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to read saved CSV")
    if limit:
        df = df.head(limit)
    max_pain = calculate_max_pain(df)
    return max_pain

@router.get("/top-oi", response_model=Dict[str, List[Dict[str, Any]]])
def get_top_oi(index: str = Query(...), expiry: Optional[str] = Query(None, description="Specific expiry date (DDMMYY format, optional)"), top_n: int = Query(5, gt=0, le=20), limit: int = Query(500, gt=0, le=5000)):
    """Get top open interest strikes for the latest option chain data"""
    idx = index.strip().upper()
    files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(f"{idx.lower()}_") and f.endswith('.csv')]
    if not files:
        raise HTTPException(status_code=404, detail=f"No saved option-chain CSVs found for {idx}")
    
    # Filter by expiry if specified
    if expiry:
        try:
            nse_expiry = convert_expiry_format(expiry)
            files = [f for f in files if nse_expiry.replace(' ', '_').replace('/', '-') in f]
            if not files:
                raise HTTPException(status_code=404, detail=f"No saved option-chain CSVs found for {idx} with expiry {nse_expiry} (input: {expiry})")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    latest_file = sorted(files, reverse=True)[0]
    csv_path = os.path.join(OUTPUT_DIR, latest_file)
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to read saved CSV")
    if limit:
        df = df.head(limit)
    top_oi = find_high_oi_strikes(df, top_n=top_n)
    return top_oi

@router.get("/summary", response_model=AnalyticsResponse)
def get_analytics_summary(index: str = Query(...), expiry: Optional[str] = Query(None, description="Specific expiry date (DDMMYY format, optional)"), limit: int = Query(500, gt=0, le=5000)):
    """Get complete analytics summary for the latest option chain data"""
    idx = index.strip().upper()
    files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith(f"{idx.lower()}_") and f.endswith('.csv')]
    if not files:
        raise HTTPException(status_code=404, detail=f"No saved option-chain CSVs found for {idx}")
    
    # Filter by expiry if specified
    if expiry:
        try:
            nse_expiry = convert_expiry_format(expiry)
            files = [f for f in files if nse_expiry.replace(' ', '_').replace('/', '-') in f]
            if not files:
                raise HTTPException(status_code=404, detail=f"No saved option-chain CSVs found for {idx} with expiry {nse_expiry} (input: {expiry})")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
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

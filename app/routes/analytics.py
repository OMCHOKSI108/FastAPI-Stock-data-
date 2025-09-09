from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import sys
import os
import pandas as pd

# Add the parent directory to sys.path to import data_gather_stocks
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.data_gather_stocks import (
    calculate_pcr,
    find_high_oi_strikes,
    calculate_max_pain,
    fetch_index_price
)
from app.schemas import (
    PCRResponse,
    TopOIResponse,
    MaxPainResponse,
    AnalyticsSummaryResponse,
    TopOIStrike,
    User
)
from app.auth import get_current_user

router = APIRouter()

def _load_latest_dataframe(index: str) -> pd.DataFrame:
    """Helper function to load the latest options data for an index"""
    output_dir = "option_chain_data"
    if not os.path.exists(output_dir):
        raise HTTPException(status_code=404, detail="No option data available")

    # Find latest CSV file for the index
    files = [f for f in os.listdir(output_dir) if f.startswith(f"{index.lower()}_") and f.endswith('.csv')]
    if not files:
        raise HTTPException(status_code=404, detail=f"No data found for index {index}")

    latest_file = sorted(files, reverse=True)[0]
    csv_path = os.path.join(output_dir, latest_file)

    return pd.read_csv(csv_path)

@router.get("/pcr", response_model=PCRResponse)
async def get_pcr(
    index: str,
    expiry: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate Put-Call Ratio for the given index.
    """
    try:
        df = _load_latest_dataframe(index)

        # Filter by expiry if specified
        if expiry:
            df = df[df['expiryDate'] == expiry]

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified parameters")

        pcr_data = calculate_pcr(df)

        return PCRResponse(
            pcr_by_oi=pcr_data['pcr_by_oi'],
            pcr_by_volume=pcr_data['pcr_by_volume']
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate PCR: {str(e)}")

# Temporary public endpoint for testing (remove after debugging)
@router.get("/pcr/public", response_model=PCRResponse)
async def get_pcr_public(
    index: str,
    expiry: Optional[str] = None
):
    """
    Public PCR endpoint for testing - NO AUTH REQUIRED.
    Calculate Put-Call Ratio for the given index.
    """
    try:
        df = _load_latest_dataframe(index)

        # Filter by expiry if specified
        if expiry:
            df = df[df['expiryDate'] == expiry]

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified parameters")

        pcr_data = calculate_pcr(df)

        return PCRResponse(
            pcr_by_oi=pcr_data['pcr_by_oi'],
            pcr_by_volume=pcr_data['pcr_by_volume']
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate PCR: {str(e)}")

@router.get("/top-oi", response_model=TopOIResponse)
async def get_top_oi(
    index: str,
    expiry: Optional[str] = None,
    top_n: int = 5,
    current_user: User = Depends(get_current_user)
):
    """
    Get top open interest strikes for calls (resistance) and puts (support).
    """
    try:
        df = _load_latest_dataframe(index)

        # Filter by expiry if specified
        if expiry:
            df = df[df['expiryDate'] == expiry]

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified parameters")

        oi_data = find_high_oi_strikes(df, top_n)

        resistance_strikes = [
            TopOIStrike(strikePrice=item['strikePrice'], openInterest=item['CE_openInterest'])
            for item in oi_data['resistance_strikes']
        ]

        support_strikes = [
            TopOIStrike(strikePrice=item['strikePrice'], openInterest=item['PE_openInterest'])
            for item in oi_data['support_strikes']
        ]

        return TopOIResponse(
            resistance_strikes=resistance_strikes,
            support_strikes=support_strikes
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get top OI: {str(e)}")

@router.get("/max-pain", response_model=MaxPainResponse)
async def get_max_pain(
    index: str,
    expiry: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Calculate maximum pain strike for the given index.
    """
    try:
        df = _load_latest_dataframe(index)

        # Filter by expiry if specified
        if expiry:
            df = df[df['expiryDate'] == expiry]

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified parameters")

        max_pain_data = calculate_max_pain(df)

        return MaxPainResponse(
            max_pain_strike=max_pain_data['max_pain_strike'],
            total_loss_value=max_pain_data['total_loss_value']
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate max pain: {str(e)}")

@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    index: str,
    expiry: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive analytics summary including PCR, top OI, max pain, and underlying price.
    """
    try:
        df = _load_latest_dataframe(index)

        # Filter by expiry if specified
        if expiry:
            df = df[df['expiryDate'] == expiry]

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for the specified parameters")

        # Get underlying price
        price_data = fetch_index_price(index.upper())
        if 'error' in price_data:
            underlying_price = 0.0  # Fallback
        else:
            underlying_price = price_data['lastPrice']

        # Calculate all analytics
        pcr_data = calculate_pcr(df)
        oi_data = find_high_oi_strikes(df, 5)
        max_pain_data = calculate_max_pain(df)

        pcr_response = PCRResponse(
            pcr_by_oi=pcr_data['pcr_by_oi'],
            pcr_by_volume=pcr_data['pcr_by_volume']
        )

        resistance_strikes = [
            TopOIStrike(strikePrice=item['strikePrice'], openInterest=item['CE_openInterest'])
            for item in oi_data['resistance_strikes']
        ]
        support_strikes = [
            TopOIStrike(strikePrice=item['strikePrice'], openInterest=item['PE_openInterest'])
            for item in oi_data['support_strikes']
        ]
        top_oi_response = TopOIResponse(
            resistance_strikes=resistance_strikes,
            support_strikes=support_strikes
        )

        max_pain_response = MaxPainResponse(
            max_pain_strike=max_pain_data['max_pain_strike'],
            total_loss_value=max_pain_data['total_loss_value']
        )

        return AnalyticsSummaryResponse(
            pcr=pcr_response,
            top_oi=top_oi_response,
            max_pain=max_pain_response,
            underlying_price=underlying_price
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics summary: {str(e)}")

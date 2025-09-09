from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional
import sys
import os
import uuid
import pandas as pd
from datetime import datetime

# Add the parent directory to sys.path to import data_gather_stocks
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_gather_stocks import (
    get_available_expiries,
    fetch_and_save_option_chain,
    fetch_specific_expiry_option_chain
)
from app.schemas import (
    FetchOptionsRequest,
    FetchOptionsExpiryRequest,
    OptionsSnapshotResponse,
    OptionStrikeData,
    JobResponse,
    User
)
from app.auth import get_current_user

router = APIRouter()

# In-memory job storage (TODO: replace with database)
jobs = {}

@router.get("/expiries")
async def get_expiries(index: str):
    """
    Return available expiries for an index.
    """
    try:
        expiries = get_available_expiries(index.upper())
        if not expiries:
            raise HTTPException(status_code=404, detail=f"No expiries found for index {index}")
        return {"index": index.upper(), "expiries": expiries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch expiries: {str(e)}")

@router.post("/fetch", response_model=JobResponse)
async def fetch_options(
    request: FetchOptionsRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger immediate fetch for the nearest expiry and persist a snapshot.
    """
    job_id = str(uuid.uuid4())

    # Store job status
    jobs[job_id] = {
        "status": "pending",
        "job_type": "fetch_options",
        "user_id": current_user.id,
        "params": request.dict(),
        "created_at": datetime.utcnow()
    }

    # Add background task
    background_tasks.add_task(
        _background_fetch_options,
        job_id,
        request.index,
        request.num_strikes
    )

    return JobResponse(
        job_id=job_id,
        status="accepted",
        message="Options fetch job queued successfully"
    )

@router.post("/fetch/expiry", response_model=JobResponse)
async def fetch_options_expiry(
    request: FetchOptionsExpiryRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Fetch & save for a specific expiry.
    """
    job_id = str(uuid.uuid4())

    # Store job status
    jobs[job_id] = {
        "status": "pending",
        "job_type": "fetch_options_expiry",
        "user_id": current_user.id,
        "params": request.dict(),
        "created_at": datetime.utcnow()
    }

    # Add background task
    background_tasks.add_task(
        _background_fetch_options_expiry,
        job_id,
        request.index,
        request.expiry,
        request.num_strikes
    )

    return JobResponse(
        job_id=job_id,
        status="accepted",
        message="Options fetch job for specific expiry queued successfully"
    )

@router.get("/latest", response_model=OptionsSnapshotResponse)
async def get_latest_options(
    index: str,
    limit: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Return most recent snapshot rows for an index (nearest expiry by default).
    """
    try:
        # TODO: Load from database instead of file system
        output_dir = "option_chain_data"
        if not os.path.exists(output_dir):
            raise HTTPException(status_code=404, detail="No option data available")

        # Find latest CSV file for the index
        files = [f for f in os.listdir(output_dir) if f.startswith(f"{index.lower()}_") and f.endswith('.csv')]
        if not files:
            raise HTTPException(status_code=404, detail=f"No data found for index {index}")

        latest_file = sorted(files, reverse=True)[0]
        csv_path = os.path.join(output_dir, latest_file)

        # Read the CSV
        df = pd.read_csv(csv_path)

        # Convert to response format
        rows = []
        for _, row in df.iterrows():
            rows.append(OptionStrikeData(
                strikePrice=row['strikePrice'],
                expiryDate=row['expiryDate'],
                CE_openInterest=row.get('CE_openInterest'),
                CE_lastPrice=row.get('CE_lastPrice'),
                CE_totalTradedVolume=row.get('CE_totalTradedVolume'),
                PE_openInterest=row.get('PE_openInterest'),
                PE_lastPrice=row.get('PE_lastPrice'),
                PE_totalTradedVolume=row.get('PE_totalTradedVolume')
            ))

        # Limit results if specified
        if limit:
            rows = rows[:limit]

        # TODO: Load proper metadata
        meta = {
            "index": index.upper(),
            "total_rows": len(rows),
            "createdAtUTC": datetime.utcnow().isoformat()
        }

        return OptionsSnapshotResponse(meta=meta, rows=rows)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No option data available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load latest options: {str(e)}")

# Background task functions
async def _background_fetch_options(job_id: str, index: str, num_strikes: int):
    """Background task to fetch options for nearest expiry"""
    try:
        jobs[job_id]["status"] = "running"

        # Call the existing function
        fetch_and_save_option_chain(index.upper(), num_strikes)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["completed_at"] = datetime.utcnow()

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error_message"] = str(e)

async def _background_fetch_options_expiry(job_id: str, index: str, expiry: str, num_strikes: int):
    """Background task to fetch options for specific expiry"""
    try:
        jobs[job_id]["status"] = "running"

        # Call the existing function
        fetch_specific_expiry_option_chain(index.upper(), expiry, num_strikes)

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["completed_at"] = datetime.utcnow()

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error_message"] = str(e)

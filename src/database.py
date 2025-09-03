import asyncpg
import pandas as pd
from typing import Optional

import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Database configuration is now loaded from environment variables.
# See .env.example for the required variables.
DB_CONFIG = {
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": os.environ.get("DB_NAME"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432))
}

async def fetch_ohlcv_data(
    pool: asyncpg.Pool, 
    table_name: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetches OHLCV data from the specified PostgreSQL table and returns it as a Pandas DataFrame.

    Args:
        pool: An asyncpg connection pool.
        table_name: The name of the table containing the OHLCV data.
        start_date: The start date for the data range (YYYY-MM-DD).
        end_date: The end date for the data range (YYYY-MM-DD).

    Returns:
        A Pandas DataFrame with the OHLCV data, with the 'timestamp' column set as the index.
        Returns an empty DataFrame if no data is found or an error occurs.
    """
    query = f"SELECT * FROM {table_name}"
    conditions = []
    params = []

    if start_date:
        conditions.append("timestamp >= $1")
        params.append(pd.to_datetime(start_date))
    if end_date:
        # The placeholder index will be $2 if start_date is also present, otherwise $1
        placeholder = f"${len(params) + 1}"
        conditions.append(f"timestamp <= {placeholder}")
        params.append(pd.to_datetime(end_date))

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY timestamp ASC"

    try:
        async with pool.acquire() as connection:
            stmt = await connection.prepare(query)
            records = await stmt.fetch(*params)
            
            if not records:
                return pd.DataFrame()

            df = pd.DataFrame(records, columns=[desc.name for desc in stmt.get_attributes()])
            df = df.set_index('timestamp')
            # Ensure numeric columns are of the correct type
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col])
            return df

    except asyncpg.PostgresError as e:
        print(f"Database error fetching data: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()


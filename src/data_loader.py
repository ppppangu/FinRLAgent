import pandas as pd
import asyncpg
from typing import Optional

# Import the new database fetching function
from .database import fetch_ohlcv_data

async def load_data_from_db(
    pool: asyncpg.Pool, 
    table_name: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Asynchronously loads trading data from the database using a connection pool.
    """
    print(f"Loading data from database table '{table_name}'...")
    df = await fetch_ohlcv_data(pool, table_name, start_date, end_date)
    if not df.empty:
        print("Data loaded successfully.")
    else:
        print("Warning: No data was loaded. Please check the table name and date range.")
    return df

if __name__ == '__main__':
    # This block is for demonstration and testing purposes.
    # It shows how to use the new data loader.
    # You will need to have a running PostgreSQL server and a populated table.
    import asyncio
    from .database import DB_CONFIG

    async def main():
        pool = None
        try:
            pool = await asyncpg.create_pool(**DB_CONFIG)
            # Replace 'your_ohlcv_table' with the actual name of your table
            table_name = 'your_ohlcv_table' 
            print(f"Attempting to load data from '{table_name}'...")
            
            # Example: Fetch data for a specific range
            # data = await load_data_from_db(pool, table_name, start_date='2023-01-01', end_date='2023-01-31')
            
            # Example: Fetch all data
            data = await load_data_from_db(pool, table_name)

            if not data.empty:
                print("\nLoaded data:")
                print(data.head())
                print("\nData Info:")
                data.info()
            else:
                print("\nCould not load data. Please ensure:")
                print("1. Your PostgreSQL server is running.")
                print(f"2. The credentials in src/database.py (DB_CONFIG) are correct.")
                print(f"3. The table '{table_name}' exists and contains data.")

        except Exception as e:
            print(f"An error occurred during the test run: {e}")
        finally:
            if pool:
                await pool.close()

    asyncio.run(main())

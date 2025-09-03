import asyncio
import os
import ray
import asyncpg
from ray.tune.logger import pretty_print

# Relative imports for execution within the src package
from .data_loader import load_data_from_db
from .agent import create_ppo_trainer
from .database import DB_CONFIG

async def main():
    """
    Main asynchronous function to run the RL training pipeline with a database connection.
    """
    pool = None
    trainer = None # Define trainer here to ensure it's accessible in finally block
    try:
        # --- 1. Initialize Database Pool and Ray ---
        print("Attempting to connect to the database...")
        pool = await asyncpg.create_pool(**DB_CONFIG)
        print("Database connection pool created.")
        
        ray.init(ignore_reinit_error=True)
        print("Ray initialized.")

        # --- 2. Load Data ---
        # Fetch data from the database. Replace 'ohlcv_data' with your actual table name if different.
        table_name = 'ohlcv_data' # <-- IMPORTANT: User might need to change this
        market_data = await load_data_from_db(pool, table_name)

        if market_data.empty:
            print(f"Fatal: No data loaded from table '{table_name}'. Aborting.")
            print("Please check your database connection, table name, and ensure it contains data.")
            return

        # --- 3. Create Agent ---
        env_config = {
            "df": market_data,
            "initial_balance": 10000
        }
        trainer = create_ppo_trainer(env_config)
        print("PPO Trainer created.")

        # --- 4. Training Loop ---
        training_iterations = 10
        print(f"Starting training for {training_iterations} iterations...")
        for i in range(training_iterations):
            result = trainer.train()
            print(f"\n--- Iteration {i+1}/{training_iterations} ---")
            print(pretty_print(result))

        print("\nTraining complete.")

        # --- 5. Save Checkpoint ---
        checkpoint_dir = trainer.save()
        print(f"\nCheckpoint saved in directory: {checkpoint_dir}")

    except (asyncpg.exceptions.InvalidPasswordError, asyncpg.exceptions.CannotConnectNowError) as e:
        print(f"Fatal Database Connection Error: {e}")
        print("Please check your database credentials in 'src/database.py' and ensure the server is running.")
    except asyncpg.exceptions.UndefinedTableError as e:
        print(f"Fatal Database Error: {e}")
        print(f"Please ensure the table '{table_name}' exists in your database.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # --- 6. Shutdown ---
        if trainer:
            trainer.stop()
        if ray.is_initialized():
            ray.shutdown()
            print("Ray shut down.")
        if pool:
            await pool.close()
            print("Database connection pool closed.")


if __name__ == '__main__':
    # To run this script, navigate to the project root directory in your terminal
    # and execute: python src/main.py
    asyncio.run(main())

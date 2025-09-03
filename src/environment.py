import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class TradingEnv(gym.Env):
    """A custom trading environment for reinforcement learning."""
    metadata = {'render_modes': ['human']}

    def __init__(self, config: dict):
        super(TradingEnv, self).__init__()

        # Extract parameters from the config dictionary
        self.df = config["df"]
        self.initial_balance = config.get("initial_balance", 10000)
        
        # The trading environment will have a single data source, so the number of steps is fixed
        self._max_episode_steps = len(self.df) - 1
        self.current_step = 0

        # Action space: 0: Hold, 1: Buy, 2: Sell
        self.action_space = spaces.Discrete(3)

        # Observation space: [balance, shares_held, current_price]
        # We use a Box space for continuous values.
        # Set low and high values for each component of the observation.
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0]),  # Balance, Shares, Price can't be negative
            high=np.array([np.inf, np.inf, np.inf]), # No upper limit on balance, shares, or price
            dtype=np.float32
        )

        # Initialize state variables that will be reset at the start of each episode
        self.balance = 0.0
        self.shares_held = 0
        self.total_value = 0.0
        
    def _get_obs(self):
        """Get the current observation."""
        return np.array([
            self.balance,
            self.shares_held,
            self.df.loc[self.current_step, 'close']
        ], dtype=np.float32)

    def _get_info(self):
        """Get auxiliary information about the current state."""
        return {'total_value': self.total_value}

    def reset(self, seed=None, options=None):
        """Reset the environment to its initial state."""
        super().reset(seed=seed)
        self.balance = self.initial_balance
        self.shares_held = 0
        self.current_step = 0
        self.total_value = self.initial_balance

        obs = self._get_obs()
        info = self._get_info()
        return obs, info

    def step(self, action):
        """Execute one time step within the environment."""
        # Get the current price from the dataframe
        current_price = self.df.loc[self.current_step, 'close']
        
        # Execute the action
        if action == 1:  # Buy
            # Buy one share if we have enough balance
            if self.balance >= current_price:
                self.balance -= current_price
                self.shares_held += 1
        elif action == 2:  # Sell
            # Sell one share if we have any
            if self.shares_held > 0:
                self.balance += current_price
                self.shares_held -= 1
        # if action is 0 (Hold), we do nothing.

        # Update the total portfolio value
        new_total_value = self.balance + (self.shares_held * current_price)
        
        # Calculate reward as the change in portfolio value from the last step
        reward = new_total_value - self.total_value
        self.total_value = new_total_value

        # Move to the next time step
        self.current_step += 1

        # Check if the episode is done
        terminated = self.current_step >= self._max_episode_steps
        truncated = False # Not using truncation for now

        # Get the next observation and info
        obs = self._get_obs()
        info = self._get_info()

        return obs, reward, terminated, truncated, info

    def render(self, mode='human'):
        """Render the environment (optional)."""
        if mode == 'human':
            print(f'Step: {self.current_step}')
            print(f'Balance: {self.balance:.2f}')
            print(f'Shares held: {self.shares_held}')
            print(f'Total Value: {self.total_value:.2f}')
            print(f'Current Price: {self.df.loc[self.current_step, "close"]:.2f}')
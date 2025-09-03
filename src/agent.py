from ray.rllib.algorithms.ppo import PPOConfig
from environment import TradingEnv # Import our custom environment

def create_ppo_trainer(env_config: dict):
    """
    Creates and configures a PPO trainer for the trading environment.

    Args:
        env_config: A dictionary containing the configuration for the TradingEnv,
                    such as the data frame and initial balance.

    Returns:
        A configured PPO trainer instance.
    """
    config = (
        PPOConfig()
        .environment(
            env=TradingEnv,
            env_config=env_config,
        )
        .framework("torch")
        .env_runners(
            # Use 0 environment runners for simple local training (training will happen on the driver).
            num_env_runners=0
        )
        # Configure resources for the driver. Use 0 GPUs for now as we are on a CPU machine.
        .resources(num_gpus=0)
    )

    # Build the trainer from the config
    trainer = config.build()

    return trainer

if __name__ == '__main__':
    # This block is for informational purposes.
    # The actual instantiation and training will happen in main.py,
    # as it requires data loading and a running Ray instance.
    print("Agent configuration script loaded.")
    print("To use, import create_ppo_trainer and call it with an environment configuration dict.")
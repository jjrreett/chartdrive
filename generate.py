# %%
import numpy as np
import polars as pl

# Parameters for Brownian Motion (Geometric Brownian Motion for stock prices)
n_points = 1_000_000  # Number of points (to generate a large dataset)
dt = 1 / 2520  # Time step (assuming daily data for a year of trading days)
mu = 0.0002   # Drift (expected return)
sigma = 0.01  # Volatility
start_price = 100.0  # Initial stock price
start_timestamp = 1672531200000000  # Unix microseconds for "2023-01-01 00:00:00"

# Define the stock tickers
stock_tickers = ["AAPL", "GOOG", "META", "TSLA", "AMZN"]

# %%
# Generate Brownian motion time series for each stock
np.random.seed(42)
timestamps = start_timestamp + np.arange(n_points) * 60_000_000  # Unix microseconds timestamps

stock_data = {}
for ticker in stock_tickers:
    # Generate Brownian motion for stock prices
    time_series = np.cumsum(np.random.normal(mu * dt, sigma * np.sqrt(dt), n_points))
    prices = start_price * np.exp(time_series)
    stock_data[ticker] = prices

# %%
# Create a Polars DataFrame
df = pl.DataFrame({
    "time": timestamps,
    **stock_data  # Unpack stock price data for each ticker
})

# %%
# Write to Parquet file
output_file = "data.parquet"
df.write_parquet(output_file)

print(f"Data written to {output_file}")

import pandas as pd

# Prepares data for further analysis
def prepare_data(file_path, group_by=True):
    # Read data
    df = pd.read_csv(file_path, names=['timestamp', 'sentiment', 'peer_id', 'sender'])
    # Transform column with timestamps to datetime
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    # Convert peer_id to str
    df['peer_id'] = df['peer_id'].astype(str)
    # Drop all columns that we do not need
    df = df.drop(['timestamp'], axis=1)
    # Set datetime as index
    df.set_index('datetime', inplace=True)
    # Current functionality is to group by peer_id (Switch in the Dashboard)
    if group_by:
        df = df.groupby(['peer_id'])
        
    # Return dataframe
    return df

# Rolling mean of sentiment and datetime
def moving_average(df, window_size):
    # Create new dataframe with rolling mean of sentiment
    df_rolling = df.rolling(window=window_size).mean().dropna(axis=0, how='all')
    # Return dataframe
    return df_rolling

# Exponential moving average of sentiment and datetime
def exponential_moving_average(df, window_size):
    # Create new dataframe with exponential moving average of sentiment
    df_ema = df.ewm(span=window_size).mean().dropna(axis=0, how='all')
    # Return dataframe
    return df_ema

